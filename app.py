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
# Handle OAuth Callback First
###########################################
# Gérer le retour OAuth avant tout autre import
if "code" in st.query_params:
    try:
        import auth_manager
        code = st.query_params.get("code")
        state = st.query_params.get("state")

        if isinstance(code, list):
            code = code[0]
        if isinstance(state, list):
            state = state[0]

        success = auth_manager.handle_oauth_callback(code, state)
        if success:
            # Nettoyer l'URL et recharger
            st.query_params.clear()
            st.success("🎉 Connexion réussie!")
            st.rerun()
        else:
            st.error("❌ Échec de l'authentification")

    except Exception as e:
        st.error(f"Erreur OAuth: {str(e)}")

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
from sedimentation_manager import SedimentationManager, SedimentationPhase
# Add FileVerseManager
from core.fileverse_manager import FileVerseManager

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
        'page': 'home',
        'current_project_id': None,
        'current_section_id': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

###########################################
# System Initialization
###########################################
@st.cache_resource
def initialize_system():
    """Initialize system components."""
    try:
        integration_layer = IntegrationLayer()
        integration_layer.initialize_system()

        project_context = integration_layer.get_module("project_context")
        history_manager = integration_layer.get_module("history_manager")

        # Initialiser le gestionnaire Fileverse
        fileverse_manager = FileVerseManager()

        # Initialiser le gestionnaire de sédimentation
        sedimentation_manager = SedimentationManager(project_context, history_manager, fileverse_manager)

        return (
            integration_layer,
            integration_layer.get_module("user_profile"),
            project_context,
            integration_layer.get_module("adaptive_engine"),
            history_manager,
            sedimentation_manager,
            fileverse_manager
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
    st.sidebar.title("🏠 Navigation")

    # Authentication status
    auth_status = auth_manager.get_auth_status()

    # Initialiser Web3 si pas encore fait
    from utils.web3_integration import initialize_web3_session
    initialize_web3_session()

    # Affichage des statuts d'authentification
    if auth_status['is_authenticated']:
        user = auth_status['user']
        st.sidebar.success(f"👤 {user.get('name', user.get('email', 'Utilisateur'))}")

    # Statut Web3 optionnel
    if st.session_state.get("web3_authenticated"):
        wallet_addr = st.session_state.get("web3_wallet_address", "")
        st.sidebar.info(f"🔗 Wallet: {wallet_addr[:6]}...{wallet_addr[-4:]}")

    if auth_status['is_authenticated']:
        user = auth_status['user']
        st.sidebar.success(f"👤 {user.get('name', user.get('email', 'Utilisateur'))}")

        # Navigation principale
        pages = {
            "🏠 Accueil": "home",
            "📁 Mes projets": "projects", 
            "⚙️ Paramètres": "settings"
        }

        for page_label, page_key in pages.items():
            if st.sidebar.button(page_label, use_container_width=True):
                navigate_to(page_key)

        # Section projets
        st.sidebar.markdown("---")
        st.sidebar.subheader("📝 Mes projets")

        if st.sidebar.button("➕ Nouveau projet", use_container_width=True, type="primary"):
            navigate_to("new_project")

        # Liste des projets
        if projects:
            for project in projects[:5]:  # Limiter à 5 projets récents
                title = project.get("title", "Sans titre")
                if len(title) > 20:
                    title = title[:17] + "..."

                if st.sidebar.button(
                    title,
                    key=f"sidebar_{project.get('project_id', '')}",
                    use_container_width=True
                ):
                    navigate_to("project_overview", current_project_id=project.get("project_id", ""))

            if len(projects) > 5:
                st.sidebar.caption(f"... et {len(projects) - 5} autres projets")
        else:
            st.sidebar.info("Aucun projet disponible")

        # Déconnexion
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Se déconnecter", use_container_width=True):
            auth_manager.logout()
            st.rerun()

    else:
        st.sidebar.warning("⚠️ Non connecté")
        st.sidebar.markdown("Connectez-vous pour accéder à vos projets:")
        auth_manager.login_button()

###########################################
# Main Application
###########################################
def main():
    """Main application entry point."""
    try:
        # Initialize system
        (
            integration_layer,
            user_profile,
            project_context,
            adaptive_engine,
            history_manager,
            sedimentation_manager,
            fileverse_manager
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
            st.title("🎓 Système de Rédaction Académique")
            st.markdown("### Bienvenue dans votre assistant d'écriture académique intelligent")

            if not auth_manager.is_authenticated():
                st.info("👋 Connectez-vous pour commencer à travailler sur vos projets académiques.")
                auth_manager.login_button()
            else:
                user = auth_manager.get_current_user()
                st.success(f"Bonjour {user.get('given_name', user.get('name', 'cher utilisateur'))} !")

                # Dashboard rapide
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("📁 Projets", len(projects))
                    if st.button("➕ Nouveau projet", use_container_width=True):
                        navigate_to("new_project")

                with col2:
                    recent_projects = len([p for p in projects if p.get('last_modified')])
                    st.metric("📝 Récents", recent_projects)

                with col3:
                    st.metric("⭐ En cours", len([p for p in projects if p.get('status') == 'active']))

                # Projets récents
                if projects:
                    st.subheader("📚 Projets récents")
                    for project in projects[:3]:
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**{project.get('title', 'Sans titre')}**")
                                st.caption(project.get('description', 'Aucune description')[:100] + "...")
                            with col2:
                                if st.button("Ouvrir", key=f"home_open_{project.get('project_id', '')}"):
                                    navigate_to("project_overview", current_project_id=project.get("project_id", ""))

        elif current_page == "new_project":
            if not auth_manager.is_authenticated():
                st.warning("⚠️ Vous devez vous connecter pour créer un projet.")
                auth_manager.login_button()
                return

            st.title("➕ Nouveau projet")
            st.markdown("Créez un nouveau projet de rédaction académique")

            with st.form("new_project_form"):
                col1, col2 = st.columns(2)

                with col1:
                    title = st.text_input("Titre du projet *", placeholder="Ex: Analyse des crypto-monaies")
                    project_type = st.selectbox("Type de projet", config.PROJECT_TYPES)
                    discipline = st.selectbox("Discipline", config.DISCIPLINES)

                with col2:
                    description = st.text_area("Description", placeholder="Décrivez brièvement votre projet...")
                    style = st.selectbox("Style d'écriture", config.WRITING_STYLES)

                submitted = st.form_submit_button("🚀 Créer le projet", type="primary")

                if submitted:
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
                            st.success("✅ Projet créé avec succès!")
                            st.balloons()
                            navigate_to("project_overview", current_project_id=project_id)
                    else:
                        for error in errors:
                            st.error(error)

        elif current_page == "project_overview":
            if not auth_manager.is_authenticated():
                st.warning("⚠️ Vous devez vous connecter pour accéder aux projets.")
                auth_manager.login_button()
                return

            if not st.session_state.current_project_id:
                st.error("❌ Aucun projet sélectionné.")
                if st.button("← Retour à l'accueil"):
                    navigate_to("home")
                return

            project = project_context.load_project(st.session_state.current_project_id)
            if project:
                st.title(f"📁 {project.get('title', 'Sans titre')}")
                st.markdown(f"*{project.get('description', 'Aucune description')}*")

                # Étapes du projet
                st.subheader("🔄 Étapes du projet")

                col1, col2, col3, col4 = st.columns(4)

                steps = [
                    ("📋 Storyboard", "storyboard", "Planifier la structure"),
                    ("✍️ Rédaction", "redaction", "Écrire le contenu"),
                    ("🔍 Révision", "revision", "Réviser et améliorer"),
                    ("📄 Finalisation", "finalisation", "Finaliser et exporter")
                ]

                for i, ((title, page, desc), col) in enumerate(zip(steps, [col1, col2, col3, col4])):
                    with col:
                        if st.button(title, key=f"step_{i}", use_container_width=True):
                            navigate_to(page)
                        st.caption(desc)
            else:
                st.error("❌ Projet non trouvé.")
                if st.button("← Retour à l'accueil"):
                    navigate_to("home")

        elif current_page in ["storyboard", "redaction", "revision", "finalisation"]:
            # Vérifier l'authentification pour tous les modules
            if not auth_manager.is_authenticated():
                st.warning("⚠️ Vous devez vous connecter pour accéder à cette fonctionnalité.")
                auth_manager.login_button()
                return

            # Navigation breadcrumb
            if st.session_state.current_project_id:
                project = project_context.load_project(st.session_state.current_project_id)
                if project:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.caption(f"📁 {project.get('title', 'Sans titre')} > {current_page.title()}")
                    with col2:
                        if st.button("← Retour projet"):
                            navigate_to("project_overview")

            # Rendre le module approprié
            if current_page == "storyboard":
                render_storyboard(
                    project_id=st.session_state.current_project_id,
                    project_context=project_context,
                    history_manager=history_manager,
                    adaptive_engine=adaptive_engine,
                    sedimentation_manager=sedimentation_manager
                )
            elif current_page == "redaction":
                render_redaction(
                    project_id=st.session_state.current_project_id,
                    section_id=st.session_state.current_section_id,
                    project_context=project_context,
                    history_manager=history_manager,
                    adaptive_engine=adaptive_engine,
                    integration_layer=integration_layer,
                    sedimentation_manager=sedimentation_manager
                )
            elif current_page == "revision":
                render_revision(
                    project_id=st.session_state.current_project_id,
                    section_id=st.session_state.current_section_id,
                    project_context=project_context,
                    history_manager=history_manager,
                    adaptive_engine=adaptive_engine,
                    integration_layer=integration_layer,
                    sedimentation_manager=sedimentation_manager
                )
            elif current_page == "finalisation":
                render_finalisation(
                    project_id=st.session_state.current_project_id,
                    project_context=project_context,
                    history_manager=history_manager,
                    adaptive_engine=adaptive_engine,
                    sedimentation_manager=sedimentation_manager
                )

        else:
            st.error(f"❌ Page '{current_page}' non trouvée.")
            if st.button("← Retour à l'accueil"):
                navigate_to("home")

    except Exception as e:
        st.error(f"❌ Une erreur est survenue: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()