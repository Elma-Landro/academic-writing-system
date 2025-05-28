import streamlit as st
import os
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

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
    PROJECT_TYPES: List[str] = field(default_factory=lambda: [
        "Article académique",
        "Mémoire",
        "Thèse",
        "Rapport de recherche",
        "Autre"
    ])
    WRITING_STYLES: List[str] = field(default_factory=lambda: [
        "Standard",
        "Académique",
        "CRÉSUS-NAKAMOTO",
        "AcademicWritingCrypto"
    ])
    DISCIPLINES: List[str] = field(default_factory=lambda: [
        "Sciences sociales",
        "Économie",
        "Droit",
        "Informatique",
        "Autre"
    ])

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
def create_project(data: dict, context: ProjectContext) -> Optional[str]:
    """Create a new project."""
    try:
        project_id = context.create_project(**data)
        return project_id
    except Exception as e:
        st.error(f"Erreur lors de la création du projet: {str(e)}")
        return None

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
                        if st.button("Ouvrir", key=f"open_{project.get('project_id', '')}"):
                            navigate_to("project_overview", current_project_id=project.get("project_id", ""))
            else:
                st.info("Connectez-vous pour accéder à vos projets.")
        
        elif current_page == "new_project":
            if not auth_manager.is_authenticated():
                st.warning("Veuillez vous connecter pour créer un projet.")
                return
            
            st.title("Nouveau projet")
            with st.form("new_project_form"):
                title = st.text_input("Titre du projet")
                description = st.text_area("Description")
                project_type = st.selectbox("Type de projet", config.PROJECT_TYPES)
                style = st.selectbox("Style d'écriture", config.WRITING_STYLES)
                discipline = st.selectbox("Discipline", config.DISCIPLINES)
                
                if st.form_submit_button("Créer"):
                    project_data = {
                        'title': title,
                        'description': description,
                        'type': project_type,
                        'style': style,
                        'discipline': discipline
                    }
                    
                    is_valid, errors = validate_project_form(project_data)
                    if is_valid:
                        project_id = create_project(project_data, project_context)
                        if project_id:
                            st.success("Projet créé avec succès!")
                            navigate_to("project_overview", current_project_id=project_id)
                    else:
                        for error in errors:
                            st.error(error)
        
        elif current_page == "project_overview":
            if not auth_manager.is_authenticated():
                st.warning("Veuillez vous connecter pour accéder aux projets.")
                return
            
            if not st.session_state.current_project_id:
                st.error("Aucun projet sélectionné.")
                navigate_to("home")
                return
            
            project = project_context.load_project(st.session_state.current_project_id)
            if project:
                st.title(project.get("title", "Sans titre"))
                st.write(project.get("description", ""))
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("Storyboard"):
                        navigate_to("storyboard")
                with col2:
                    if st.button("Rédaction"):
                        navigate_to("redaction")
                with col3:
                    if st.button("Révision"):
                        navigate_to("revision")
                with col4:
                    if st.button("Finalisation"):
                        navigate_to("finalisation")
        
        elif current_page == "storyboard":
            if not auth_manager.is_authenticated():
                st.warning("Veuillez vous connecter pour accéder à cette fonctionnalité.")
                return
            
            render_storyboard(
                project_id=st.session_state.current_project_id,
                project_context=project_context,
                history_manager=history_manager,
                adaptive_engine=adaptive_engine
            )
        
        elif current_page == "redaction":
            if not auth_manager.is_authenticated():
                st.warning("Veuillez vous connecter pour accéder à cette fonctionnalité.")
                return
                
            render_redaction(
                project_id=st.session_state.current_project_id,
                section_id=st.session_state.current_section_id,
                project_context=project_context,
                history_manager=history_manager,
                adaptive_engine=adaptive_engine,
                integration_layer=integration_layer
            )
        
        elif current_page == "revision":
            if not auth_manager.is_authenticated():
                st.warning("Veuillez vous connecter pour accéder à cette fonctionnalité.")
                return
                
            render_revision(
                project_id=st.session_state.current_project_id,
                section_id=st.session_state.current_section_id,
                project_context=project_context,
                history_manager=history_manager,
                adaptive_engine=adaptive_engine,
                integration_layer=integration_layer
            )
        
        elif current_page == "finalisation":
            if not auth_manager.is_authenticated():
                st.warning("Veuillez vous connecter pour accéder à cette fonctionnalité.")
                return
                
            render_finalisation(
                project_id=st.session_state.current_project_id,
                project_context=project_context,
                history_manager=history_manager
            )
    
    except Exception as e:
        st.error(f"Une erreur est survenue: {str(e)}")

if __name__ == "__main__":
    main()
