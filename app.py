import streamlit as st
import os
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

###########################################
# Application Configuration
###########################################
@dataclass
class AppConfig:
    """Application configuration constants."""
    PAGE_TITLE: str = "Système de Rédaction Académique"
    PAGE_ICON: str = "📝"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "expanded"
    PROJECT_TYPES: List[str] = [
        "Article académique",
        "Mémoire",
        "Thèse",
        "Rapport de recherche",
        "Autre"
    ]
    WRITING_STYLES: List[str] = [
        "Standard",
        "Académique",
        "CRÉSUS-NAKAMOTO",
        "AcademicWritingCrypto"
    ]
    DISCIPLINES: List[str] = [
        "Sciences sociales",
        "Économie",
        "Droit",
        "Informatique",
        "Autre"
    ]

config = AppConfig()

###########################################
# Streamlit Configuration
###########################################
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state=config.SIDEBAR_STATE
)

###########################################
# System Path Configuration
###########################################
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

###########################################
# Imports
###########################################
import auth_manager
from utils.common import sidebar
from core.integration_layer import IntegrationLayer
from core.user_profile import UserProfile
from core.project_context import ProjectContext
from core.adaptive_engine import AdaptiveEngine
from core.history_manager import HistoryManager

# Render modules
from modules.storyboard import render_storyboard
from modules.redaction import render_redaction
from modules.revision import render_revision
from modules.finalisation import render_finalisation

###########################################
# Session State Management
###########################################
def initialize_session_state():
    """Initialize session state variables."""
    defaults = {
        'google_credentials': None,
        'user_info': None,
        'page': 'home',
        'current_project_id': None,
        'current_section_id': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

###########################################
# Authentication Management
###########################################
def handle_oauth_callback():
    """Handle OAuth callback."""
    try:
        if "code" not in st.query_params:
            return False
            
        code = st.query_params["code"][0]
        flow = auth_manager.create_oauth_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        st.session_state.google_credentials = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        st.session_state.user_info = auth_manager.get_user_info(credentials)
        st.success(f"Connecté en tant que {st.session_state.user_info.get('email')}")
        return True
        
    except Exception as e:
        st.error(f"Erreur d'authentification: {str(e)}")
        return False

def handle_login():
    """Initialize login process."""
    try:
        flow = auth_manager.create_oauth_flow()
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")

###########################################
# System Initialization
###########################################
@st.cache_resource
def initialize_system():
    """Initialize system components."""
    try:
        integration_layer = IntegrationLayer()
        integration_layer.initialize_system()
        
        return (
            integration_layer,
            integration_layer.get_module("user_profile"),
            integration_layer.get_module("project_context"),
            integration_layer.get_module("adaptive_engine"),
            integration_layer.get_module("history_manager")
        )
    except Exception as e:
        st.error(f"Erreur d'initialisation: {str(e)}")
        st.stop()

###########################################
# Project Management
###########################################
def get_current_project(projects: List[dict], project_id: str) -> Optional[dict]:
    """Get current project by ID."""
    return next(
        (p for p in projects if p.get("project_id", "") == project_id),
        None
    )

def validate_project_form(data: dict) -> tuple[bool, List[str]]:
    """Validate project form data."""
    errors = []
    if not data.get('title'):
        errors.append("Le titre est obligatoire.")
    if len(data.get('title', '')) > 100:
        errors.append("Le titre ne doit pas dépasser 100 caractères.")
    if not data.get('description'):
        errors.append("La description est obligatoire.")
    return len(errors) == 0, errors

###########################################
# Navigation
###########################################
def navigate_to(page: str, **kwargs):
    """Handle navigation."""
    st.session_state.page = page
    for key, value in kwargs.items():
        st.session_state[key] = value
    st.rerun()

###########################################
# Sidebar Implementation
###########################################
def render_sidebar(projects: List[Dict[str, Any]], current_project_id: Optional[str]):
    """Render sidebar with navigation and authentication."""
    st.sidebar.title("Navigation")
    
    # Authentication status
    if auth_manager.is_authenticated():
        user_info = st.session_state.user_info
        st.sidebar.success(f"👤 {user_info.get('email')}")
        
        # Navigation
        pages = ["Accueil", "Mes projets", "Paramètres"]
        selected_page = st.sidebar.radio("Aller à", pages)
        
        if selected_page != st.session_state.page:
            navigate_to(selected_page.lower().replace(' ', '_'))
        
        # Projects section
        st.sidebar.title("Mes projets")
        if st.sidebar.button("➕ Nouveau projet"):
            navigate_to("new_project")
        
        for project in projects:
            if st.sidebar.button(
                project.get("title", "Sans titre"),
                key=f"sidebar_{project.get('project_id', '')}"
            ):
                navigate_to("project_overview", current_project_id=project.get("project_id", ""))
        
        # Logout option
        st.sidebar.markdown("---")
        if st.sidebar.button("Se déconnecter"):
            auth_manager.logout()
            st.rerun()
            
    else:
        st.sidebar.warning("Non connecté")
        if st.sidebar.button("Se connecter avec Google"):
            handle_login()

###########################################
# Main Application
###########################################
def main():
    """Main application entry point."""
    # Handle OAuth callback
    if "code" in st.query_params:
        if handle_oauth_callback():
            st.rerun()
    
    try:
        # Initialize system
        (
            integration_layer,
            user_profile,
            project_context,
            adaptive_engine,
            history_manager
        ) = initialize_system()
        
        # Get projects if authenticated
        projects = []
        if auth_manager.is_authenticated():
            projects = project_context.get_all_projects()
        
        # Display sidebar
        render_sidebar(projects, st.session_state.current_project_id)
        
        # Page routing
        current_page = st.session_state.page
        
        if current_page == "home":
            st.title("Bienvenue dans le Système de Rédaction Académique")
            
            if auth_manager.is_authenticated():
                if projects:
                    st.subheader("Projets récents")
                    for project in projects[:6]:
                        st.write(f"- {project.get('title', 'Sans titre')}")
            else:
                st.info("Connectez-vous pour accéder à vos projets.")
        
        elif current_page == "new_project":
            if not auth_manager.is_authenticated():
                st.warning("Veuillez vous connecter pour créer un projet.")
                return
            
            st.title("Nouveau projet")
            # Project creation form here...
        
        elif current_page in ["project_overview", "storyboard", "redaction", "revision"]:
            if not auth_manager.is_authenticated():
                st.warning("Veuillez vous connecter pour accéder aux projets.")
                return
            
            if not st.session_state.current_project_id:
                st.error("Aucun projet sélectionné.")
                navigate_to("home")
                return
            
            # Render appropriate page content here...
    
    except Exception as e:
        st.error(f"Une erreur est survenue: {str(e)}")

if __name__ == "__main__":
    main()
