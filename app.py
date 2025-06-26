"""
Academic Writing System - Main Application
Complete Streamlit application with proper authentication and module integration.
"""

import streamlit as st
import logging
import os
from datetime import datetime
from typing import Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Academic Writing System",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import core modules with better error handling
core_modules_available = True
page_modules_available = True

try:
    from core.auth_system import auth_manager, require_auth, render_login_page
    from core.database_layer import db_manager
    from core.config_manager import config_manager
    from core.adaptive_engine import AdaptiveEngine
    from core.integration_layer import IntegrationLayer
    from services.ai_service import ai_service
    logger.info("Core modules imported successfully")
except ImportError as e:
    logger.error(f"Failed to import core modules: {e}")
    core_modules_available = False

try:
    from modules.storyboard import render_storyboard
    from modules.redaction import render_redaction
    from modules.revision import render_revision
    from modules.finalisation import render_finalisation
    logger.info("Page modules imported successfully")
except ImportError as e:
    logger.error(f"Failed to import page modules: {e}")
    page_modules_available = False

# Show error page if modules are not available
if not core_modules_available or not page_modules_available:
    st.error("🚫 Application Error")
    st.markdown("""
    **The application encountered an import error.**

    This might be due to:
    - Missing dependencies
    - Configuration issues
    - Module path problems

    Please check the logs for more details.
    """)

    if st.button("🔄 Retry"):
        st.rerun()

    st.stop()

def initialize_app():
    """Initialize the application and check system status."""
    try:
        # Initialize session state
        if 'page' not in st.session_state:
            st.session_state.page = 'home'

        if 'project_id' not in st.session_state:
            st.session_state.project_id = None

        # Initialize system components with error handling
        adaptive_engine = None
        integration_layer = None
        system_status = {'openai': False, 'google_oauth': False, 'fileverse': False}

        try:
            adaptive_engine = AdaptiveEngine()
            logger.info("AdaptiveEngine initialized successfully")
        except Exception as e:
            logger.warning(f"AdaptiveEngine initialization failed: {e}")

        try:
            integration_layer = IntegrationLayer()
            logger.info("IntegrationLayer initialized successfully")
        except Exception as e:
            logger.warning(f"IntegrationLayer initialization failed: {e}")

        try:
            system_status = config_manager.get_system_status()
            logger.info("System status retrieved successfully")
        except Exception as e:
            logger.warning(f"Failed to get system status: {e}")

        # Show warnings for missing configurations (only if sidebar is available)
        try:
            if not system_status.get('openai', False):
                st.sidebar.error("🚫 OpenAI API not configured")
                st.sidebar.markdown("""
                **To use AI features:**
                1. Get an OpenAI API key from [OpenAI](https://platform.openai.com/api-keys)
                2. Add it in the Secrets tab as `OPENAI_API_KEY`
                """)

            if not system_status.get('google_oauth', False):
                st.sidebar.warning("⚠️ Google OAuth not configured")

            if not system_status.get('fileverse', False):
                st.sidebar.info("ℹ️ FileVerse not configured (optional)")
        except Exception as e:
            logger.warning(f"Failed to show sidebar warnings: {e}")

        return adaptive_engine, integration_layer, system_status

    except Exception as e:
        st.error(f"Failed to initialize application: {e}")
        logger.error(f"App initialization error: {e}")
        st.markdown("**Debug info:**")
        st.code(str(e))
        st.stop()

def render_sidebar(user: Optional[Any]) -> None:
    """Render the navigation sidebar."""
    with st.sidebar:
        st.title("📝 Academic Writing")

        if user:
            st.write(f"👤 {user.display_name}")

            # Navigation menu
            st.markdown("### Navigation")

            # Navigation constants
            NAVIGATION_PAGES = {
                'home': '🏠 Home',
                'projects': '📁 My Projects',
                'storyboard': '📋 Storyboard',
                'redaction': '✍️ Writing',
                'revision': '🔍 Revision',
                'finalisation': '📄 Finalization',
                'profile': '⚙️ Profile'
            }

            pages = NAVIGATION_PAGES

            for page_key, page_name in pages.items():
                if st.button(page_name, key=f"nav_{page_key}"):
                    st.session_state.page = page_key
                    st.rerun()

            st.markdown("---")

            # Project selector
            if st.session_state.project_id:
                st.markdown("### Current Project")
                try:
                    projects = db_manager.get_user_projects(user.id)
                    current_project = next((p for p in projects if p.id == st.session_state.project_id), None)
                    if current_project:
                        st.write(f"📝 {current_project.title}")
                        if st.button("Change Project"):
                            st.session_state.project_id = None
                            st.session_state.page = 'projects'
                            st.rerun()
                except Exception as e:
                    st.error(f"Error loading project: {e}")

            st.markdown("---")

            # Logout button
            if st.button("🚪 Logout"):
                auth_manager.logout()

        else:
            st.write("Please log in to continue")

def render_home_page(user):
    """Render the home page."""
    st.title("🏠 Academic Writing System")
    st.markdown("### Welcome to the next generation of academic writing!")

    if user:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📁 Projects", len(db_manager.get_user_projects(user.id)))

        with col2:
            st.metric("✍️ Status", "Active")

        with col3:
            st.metric("🚀 Version", "2.0")

        st.markdown("---")

        # Quick actions
        # Debug OAuth URLs
        if st.checkbox("🔧 Debug OAuth URLs"):
            st.code(f"""
URLs à configurer dans Google Cloud Console :
- http://localhost:5000/oauth2callback
- https://{auth_manager.get_replit_url()}/oauth2callback
- https://academic-writing-system-mael-rolland.streamlit.app/oauth2callback
            """)

        st.markdown("### Quick Actions")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📝 New Project", type="primary"):
                st.session_state.page = 'projects'
                st.rerun()

        with col2:
            if st.button("📋 Continue Writing"):
                projects = db_manager.get_user_projects(user.id)
                if projects:
                    st.session_state.project_id = projects[0].id
                    st.session_state.page = 'storyboard'
                    st.rerun()
                else:
                    st.info("No projects found. Create one first!")

        with col3:
            if st.button("📊 View Analytics"):
                st.session_state.page = 'profile'
                st.rerun()

        # Recent projects
        st.markdown("### Recent Projects")
        projects = db_manager.get_user_projects(user.id)

        if projects:
            for project in projects[:3]:
                with st.expander(f"📝 {project.title}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Type:** {project.project_type}")
                        st.write(f"**Status:** {project.status}")
                        st.write(f"**Updated:** {project.updated_at.strftime('%Y-%m-%d %H:%M')}")
                    with col2:
                        if st.button("Open", key=f"open_{project.id}"):
                            st.session_state.project_id = project.id
                            st.session_state.page = 'storyboard'
                            st.rerun()
        else:
            st.info("No projects yet. Create your first project to get started!")

    else:
        st.info("Please log in to access your projects and start writing.")

def render_projects_page(user):
    """Render the projects management page."""
    st.title("📁 My Projects")

    # Create new project
    with st.expander("➕ Create New Project", expanded=False):
        with st.form("new_project"):
            title = st.text_input("Project Title")
            description = st.text_area("Description")

            col1, col2 = st.columns(2)
            with col1:
                project_type = st.selectbox("Type", [
                    "Article académique",
                    "Thèse",
                    "Mémoire",
                    "Rapport de recherche",
                    "Communication"
                ])

            with col2:
                style = st.selectbox("Style", [
                    "Académique",
                    "Standard",
                    "CRÉSUS-NAKAMOTO",
                    "AcademicWritingCrypto"
                ])

            if st.form_submit_button("Create Project", type="primary"):
                if title:
                    try:
                        project = db_manager.create_project(
                            user_id=user.id,
                            title=title,
                            description=description,
                            project_type=project_type,
                            style=style
                        )
                        st.success(f"Project '{title}' created successfully!")
                        st.session_state.project_id = project.id
                        st.session_state.page = 'storyboard'
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to create project: {e}")
                else:
                    st.error("Please provide a project title.")

    # List existing projects
    st.markdown("### Your Projects")
    projects = db_manager.get_user_projects(user.id)

    if projects:
        for project in projects:
            with st.container():
                col1, col2, col3 = st.columns([4, 2, 1])

                with col1:
                    st.markdown(f"**{project.title}**")
                    st.caption(f"{project.project_type} • {project.style}")
                    if project.description:
                        st.write(project.description[:100] + "..." if len(project.description) > 100 else project.description)

                with col2:
                    st.write(f"**Status:** {project.status}")
                    st.write(f"**Updated:** {project.updated_at.strftime('%Y-%m-%d')}")

                with col3:
                    if st.button("Open", key=f"open_project_{project.id}"):
                        st.session_state.project_id = project.id
                        st.session_state.page = 'storyboard'
                        st.rerun()

                st.markdown("---")
    else:
        st.info("No projects found. Create your first project above!")

def render_profile_page(user):
    """Render the user profile page."""
    st.title("⚙️ User Profile")

    # User information
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Account Information")
        st.write(f"**Name:** {user.display_name}")
        st.write(f"**Email:** {user.email}")
        st.write(f"**Member since:** {user.created_at.strftime('%Y-%m-%d')}")

        if user.wallet_address:
            st.write(f"**Wallet:** {user.wallet_address[:10]}...{user.wallet_address[-8:]}")

    with col2:
        st.subheader("Statistics")
        projects = db_manager.get_user_projects(user.id)
        st.metric("Total Projects", len(projects))

        completed_projects = [p for p in projects if p.status == 'completed']
        st.metric("Completed Projects", len(completed_projects))

        # AI usage stats (if available)
        try:
            usage_stats = ai_service.get_usage_stats(user.id)
            st.metric("AI Requests (7 days)", usage_stats['total_requests'])
        except:
            st.metric("AI Requests", "N/A")

    # Preferences
    st.subheader("Preferences")
    with st.form("preferences"):
        default_style = st.selectbox("Default Writing Style", [
            "Académique",
            "Standard", 
            "CRÉSUS-NAKAMOTO",
            "AcademicWritingCrypto"
        ], index=0)

        default_length = st.number_input("Default Article Length (words)", 
                                       min_value=500, max_value=10000, value=3000)

        if st.form_submit_button("Save Preferences"):
            try:
                # Update user preferences in database
                with db_manager.get_session() as session:
                    user_obj = session.query(db_manager.User).filter_by(id=user.id).first()
                    if user_obj:
                        user_obj.preferences = {
                            'default_style': default_style,
                            'default_length': default_length
                        }
                        session.commit()
                st.success("Preferences saved!")
            except Exception as e:
                st.error(f"Failed to save preferences: {e}")

def handle_oauth_callback():
    """Handle OAuth callback from Google."""
    from urllib.parse import parse_qs
    # Get query parameters
    query_params = st.query_params

    if 'code' in query_params:
        code = query_params['code'][0]
        state = query_params.get('state', [None])[0]

        # Process the callback
        success = auth_manager.handle_oauth_callback(code, state)

        if success:
            st.success("Authentification réussie!")
            st.rerun()
        else:
            st.error("Erreur d'authentification")

def main():
    """Main application entry point."""
    try:
        # Initialize application
        adaptive_engine, integration_layer, system_status = initialize_app()

        # Check authentication
        user = auth_manager.get_current_user()

        # Render sidebar
        render_sidebar(user)

        # Route to appropriate page
        if not user:
            # === INTERFACE D'AUTHENTIFICATION ===
            if not st.session_state.get('is_authenticated', False):
                st.title("🔐 Academic Writing System - Login")

                # Section Google Account
                st.subheader("Google Account")
                st.write("Login with your Google account for full features:")

                # Vérification si on a des paramètres d'URL (retour OAuth)
                query_params = st.query_params
                if 'code' in query_params:
                    st.info("Traitement de l'authentification en cours...")
                    handle_oauth_callback()

                # Rendu du système d'authentification
                try:
                    auth_manager.render_google_login()
                except Exception as e:
                    st.error(f"Erreur d'authentification: {e}")
                    logger.error(f"Authentication error: {e}")

                # Section Web3 Wallet
                st.subheader("Web3 Wallet")
                st.write("Connect your crypto wallet:")

                wallet_address = st.text_input("Wallet Address", key="wallet_input")
                signature = st.text_input("Signature", type="password", key="signature_input")

                if st.button("Connect Wallet", key="connect_wallet"):
                    if wallet_address and signature:
                        # Validation basique (à améliorer)
                        st.session_state.wallet_address = wallet_address
                        st.session_state.wallet_signature = signature
                        st.session_state.web3_authenticated = True
                        st.session_state.is_authenticated = True
                        st.success("Web3 wallet connected!")
                        st.rerun()
                    else:
                        st.error("Please provide both wallet address and signature")

                # Si aucune authentification
                if not st.session_state.get('web3_authenticated', False):
                    st.info("Please authenticate using Google Account or Web3 Wallet to access the system.")
                return

        page = st.session_state.get('page', 'home')

        if page == 'home':
            render_home_page(user)

        elif page == 'projects':
            render_projects_page(user)

        elif page == 'profile':
            render_profile_page(user)

        elif page == 'storyboard':
            if st.session_state.project_id:
                render_storyboard(st.session_state.project_id, None, None, adaptive_engine)
            else:
                st.warning("Please select a project first.")
                st.session_state.page = 'projects'
                st.rerun()

        elif page == 'redaction':
            if st.session_state.project_id:
                render_redaction(st.session_state.project_id, None, None, adaptive_engine)
            else:
                st.warning("Please select a project first.")
                st.session_state.page = 'projects'
                st.rerun()

        elif page == 'revision':
            if st.session_state.project_id:
                render_revision(st.session_state.project_id, None, None, adaptive_engine)
            else:
                st.warning("Please select a project first.")
                st.session_state.page = 'projects'
                st.rerun()

        elif page == 'finalisation':
            if st.session_state.project_id:
                render_finalisation(st.session_state.project_id, None, None, adaptive_engine)
            else:
                st.warning("Please select a project first.")
                st.session_state.page = 'projects'
                st.rerun()

        else:
            st.error(f"Unknown page: {page}")
            st.session_state.page = 'home'
            st.rerun()

    except Exception as e:
        st.error(f"Application error: {e}")
        logger.error(f"Main application error: {e}")

if __name__ == "__main__":
    main()