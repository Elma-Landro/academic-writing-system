import streamlit as st
import os
import uuid
from datetime import datetime, timezone
import sys
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

###########################################
# Application Configuration and Constants
###########################################
@dataclass
class AppConfig:
    """Application configuration constants."""
    PAGE_TITLE: str = "Système de Rédaction Académique"
    PAGE_ICON: str = "📝"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "expanded"
    CURRENT_USER: str = "Elma-Landro"  # Current user login
    TIMESTAMP_FORMAT: str = "%Y-%m-%d %H:%M:%S"
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
# Streamlit Configuration (Must be first)
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
# Module Imports
###########################################
import auth_manager  # Import at top level for better error handling
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
def initialize_session_state() -> None:
    """Initialize all session state variables with default values."""
    defaults = {
        'google_credentials': None,
        'user_info': None,
        'page': 'home',
        'current_project_id': None,
        'current_section_id': None,
        'last_save': None,
        'auth_initialized': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

###########################################
# Error Handling
###########################################
def handle_error(error: Exception, context: str = "General", show_error: bool = True) -> None:
    """Centralized error handling with logging."""
    error_message = f"Erreur {context}: {str(error)}"
    error_time = datetime.now(timezone.utc).strftime(config.TIMESTAMP_FORMAT)
    
    if show_error:
        st.error(error_message)
    
    # Add logging
    import logging
    logging.error(f"[{error_time}] {context} error: {error}", exc_info=True)
    logging.error(f"User: {config.CURRENT_USER}")

###########################################
# Authentication Management
###########################################
def check_authentication() -> bool:
    """Check if user is authenticated using auth_manager."""
    try:
        if not auth_manager.is_authenticated():
            st.warning("Veuillez vous connecter pour accéder à cette fonctionnalité.")
            return False
        return True
    except Exception as e:
        handle_error(e, "Authentication Check")
        return False

def handle_oauth_callback() -> bool:
    """Handle OAuth callback and credential storage."""
    try:
        if "code" not in st.query_params:
            return False
            
        code = st.query_params["code"][0]
        flow = auth_manager.create_oauth_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Store credentials in format expected by auth_manager
        st.session_state.google_credentials = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Get user info using auth_manager
        user_info = auth_manager.get_user_info(credentials)
        st.session_state.user_info = user_info
        st.session_state.auth_initialized = True
        
        st.success(f"Connecté en tant que {user_info.get('email')}")
        return True
        
    except Exception as e:
        handle_error(e, "OAuth Authentication")
        return False

def handle_login() -> None:
    """Handle login initialization."""
    try:
        flow = auth_manager.create_oauth_flow()
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.markdown(
            f'<meta http-equiv="refresh" content="0; url={auth_url}">',
            unsafe_allow_html=True
        )
    except Exception as e:
        handle_error(e, "Login Initialization")

def handle_logout() -> None:
    """Handle logout using auth_manager."""
    try:
        auth_manager.logout()
        st.session_state.auth_initialized = False
        st.rerun()
    except Exception as e:
        handle_error(e, "Logout")

###########################################
# System Initialization
###########################################
@st.cache_resource(ttl=3600)
def initialize_system() -> tuple[IntegrationLayer, UserProfile, ProjectContext, 
                               AdaptiveEngine, HistoryManager]:
    """Initialize system components with proper caching."""
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
        handle_error(e, "System Initialization")
        st.stop()

###########################################
# Sedimentation Management
###########################################
@st.cache_resource(ttl=3600)
def init_auth_and_sedimentation() -> Optional[Any]:
    """Initialize sedimentation manager if authenticated."""
    try:
        import sedimentation_manager
        
        if auth_manager.is_authenticated():
            return sedimentation_manager.SedimentationManager()
        return None
    except Exception as e:
        handle_error(e, "Sedimentation Initialization", show_error=False)
        return None

def save_to_sedimentation(
    manager: Any,
    project_id: str,
    project_name: str,
    data: dict,
    stage: str
) -> bool:
    """Save project state to sedimentation manager."""
    if not manager:
        return False
        
    try:
        current_time = datetime.now(timezone.utc)
        
        manager.save_project_state(
            project_id=project_id,
            project_name=project_name,
            data={
                **data,
                'last_modified_by': config.CURRENT_USER,
                'last_modified_at': current_time.strftime(config.TIMESTAMP_FORMAT)
            },
            stage=stage
        )
        st.session_state.last_save = current_time
        return True
    except Exception as e:
        handle_error(e, "Sedimentation Save", show_error=False)
        st.warning(f"Impossible de sauvegarder sur Google Drive: {str(e)}")
        return False

###########################################
# Project Management
###########################################
def get_current_project(projects: List[dict], project_id: str) -> Optional[dict]:
    """Get current project by ID."""
    return next(
        (p for p in projects if p.get("project_id", "") == project_id),
        None
    )

def validate_project_form(data: dict) -> tuple[bool, list[str]]:
    """Validate project form data."""
    errors = []
    if not data.get('title'):
        errors.append("Le titre est obligatoire.")
    if len(data.get('title', '')) > 100:
        errors.append("Le titre ne doit pas dépasser 100 caractères.")
    if not data.get('description'):
        errors.append("La description est obligatoire.")
    return len(errors) == 0, errors

def create_project(
    data: dict,
    context: ProjectContext,
    user_profile: UserProfile,
    history_manager: HistoryManager,
    sedimentation_manager: Optional[Any] = None
) -> Optional[str]:
    """Create a new project with proper error handling."""
    try:
        # Add creation metadata
        data['created_by'] = config.CURRENT_USER
        data['created_at'] = datetime.now(timezone.utc).strftime(config.TIMESTAMP_FORMAT)
        
        # Create project
        project_id = context.create_project(**data)
        
        # Update user statistics
        user_profile.update_statistics("projects_created")
        
        # Log activity
        user_profile.log_activity("create_project", {
            "project_id": project_id,
            "title": data['title'],
            "timestamp": data['created_at']
        })
        
        # Save initial version
        project_data = context.load_project(project_id)
        history_manager.save_version(
            project_id=project_id,
            project_data=project_data,
            description="Création du projet"
        )
        
        # Handle sedimentation
        if sedimentation_manager:
            save_to_sedimentation(
                sedimentation_manager,
                project_id,
                data['title'],
                project_data,
                "creation"
            )
        
        return project_id
    except Exception as e:
        handle_error(e, "Project Creation")
        return None

###########################################
# Navigation
###########################################
def navigate_to(page: str, **kwargs) -> None:
    """Handle navigation with state management."""
    st.session_state.page = page
    for key, value in kwargs.items():
        st.session_state[key] = value
    st.rerun()

###########################################
# Sidebar Implementation
###########################################
def sidebar_with_auth(
    projects: List[Dict[str, Any]],
    current_project_id: Optional[str]
) -> None:
    """Render sidebar with authentication."""
    st.sidebar.title("Navigation")
    
    # Authentication status
    if auth_manager.is_authenticated():
        user_info = st.session_state.user_info
        st.sidebar.success(f"👤 {user_info.get('email')}")
    else:
        st.sidebar.warning("Non connecté")
        if st.sidebar.button("Se connecter avec Google"):
            handle_login()
            return
    
    # Page selection
    pages = ["Accueil", "Mes projets", "Paramètres"]
    selected_page = st.sidebar.radio("Aller à", pages)
    
    # Navigation handling
    if selected_page == "Accueil" and st.session_state.page != "home":
        navigate_to("home")
    elif selected_page == "Mes projets" and st.session_state.page != "projects":
        if not check_authentication():
            return
        navigate_to("projects")
    elif selected_page == "Paramètres" and st.session_state.page != "settings":
        if not check_authentication():
            return
        navigate_to("settings")
    
    # Projects section (only if authenticated)
    if auth_manager.is_authenticated():
        st.sidebar.markdown("---")
        st.sidebar.title("Mes projets")
        
        if st.sidebar.button("➕ Nouveau projet"):
            navigate_to("new_project")
        
        if projects:
            for project in projects:
                if st.sidebar.button(
                    project.get("title", "Sans titre"),
                    key=f"sidebar_{project.get('project_id', '')}"
                ):
                    navigate_to(
                        "project_overview",
                        current_project_id=project.get("project_id", "")
                    )
        else:
            st.sidebar.info("Aucun projet disponible.")
        
        # Logout option
        st.sidebar.markdown("---")
        if st.sidebar.button("Se déconnecter"):
            handle_logout()
    
    # Current project navigation (if authenticated and project selected)
    if auth_manager.is_authenticated() and current_project_id:
        current_project = get_current_project(projects, current_project_id)
        
        if current_project:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Projet actuel")
            st.sidebar.info(current_project.get("title", "Sans titre"))
            
            # Last modified info
            last_modified = current_project.get("last_modified_at", "")
            if last_modified:
                st.sidebar.caption(f"Dernière modification: {last_modified}")
                st.sidebar.caption(f"Par: {current_project.get('last_modified_by', 'Unknown')}")
            
            # Project navigation buttons
            nav_buttons = [
                ("Vue d'ensemble", "project_overview"),
                ("Storyboard", "storyboard"),
                ("Rédaction", "redaction"),
                ("Révision", "revision"),
                ("Finalisation", "finalisation"),
                ("Historique", "history"),
                ("Paramètres du projet", "project_settings")
            ]
            
            for button_text, page_name in nav_buttons:
                if st.sidebar.button(button_text):
                    navigate_to(page_name)

[... Rest of the main() function and page handlers remain the same as in the previous version,
    but with added authentication checks using check_authentication() where needed ...]

if __name__ == "__main__":
    main()
