import streamlit as st
import os
import uuid
from datetime import datetime
import sys
import traceback

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(file)))

# Import existing core modules with error handling
try:
    from utils.common import sidebar
    from core.integration_layer import IntegrationLayer
    from core.user_profile import UserProfile
    from core.project_context import ProjectContext
    from core.adaptive_engine import AdaptiveEngine
    from core.history_manager import HistoryManager
    
    # Import rendering modules
    from modules.storyboard import render_storyboard
    from modules.redaction import render_redaction
    from modules.revision import render_revision
    from modules.finalisation import render_finalisation
    
    MODULES_LOADED = True
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    MODULES_LOADED = False

# Streamlit page configuration
st.set_page_config(
    page_title="Academic Writing System",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
def initialize_session_state():
    """Initialize session state variables with default values."""
    defaults = {
        "page": "home",
        "current_project_id": None,
        "current_section_id": None,
        "google_credentials": None,
        "user_info": None,
        "sedimentation_manager": None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

initialize_session_state()

# Authentication and sedimentation manager initialization
@st.cache_resource
def init_auth_and_sedimentation():
    """Initialize Google authentication and sedimentation manager."""
    try:
        import auth_manager
        import sedimentation_manager
        
        if auth_manager.is_authenticated():
            return sedimentation_manager.SedimentationManager()
        return None
    except Exception as e:
        st.warning(f"Unable to initialize Google authentication: {str(e)}")
        return None

# System initialization
@st.cache_resource
def initialize_system():
    """Initialize the system and return main components."""
    if not MODULES_LOADED:
        return None, None, None, None, None
    
    try:
        integration_layer = IntegrationLayer()
        integration_layer.initialize_system()
        
        user_profile = integration_layer.get_module("user_profile")
        project_context = integration_layer.get_module("project_context")
        adaptive_engine = integration_layer.get_module("adaptive_engine")
        history_manager = integration_layer.get_module("history_manager")
        
        return integration_layer, user_profile, project_context, adaptive_engine, history_manager
    except Exception as e:
        st.error(f"Error initializing system: {str(e)}")
        return None, None, None, None, None

# OAuth2 callback handling
def handle_oauth_callback():
    """Handle OAuth2 callback from Google."""
    if "code" not in st.query_params:
        return False
    
    try:
        import auth_manager
        
        flow = auth_manager.create_oauth_flow()
        flow.fetch_token(code=st.query_params["code"])
        
        credentials = flow.credentials
        user_info = auth_manager.get_user_info(credentials)
        
        # Store in session state
        st.session_state.google_credentials = credentials.to_json()
        st.session_state.user_info = user_info
        st.session_state.page = "home"
        
        # Initialize sedimentation manager
        st.session_state.sedimentation_manager = init_auth_and_sedimentation()
        
        st.success(f"Successfully connected as {user_info.get('email')}")
        return True
    except Exception as e:
        st.error(f"OAuth2 processing error: {e}")
        return False
        # Enhanced sidebar with authentication
def render_sidebar_with_auth(projects, current_project_id):
    """Render sidebar with authentication integration."""
    st.sidebar.title("🧭 Navigation")
    
    # Page selection
    pages = {
        "🏠 Home": "home",
        "📂 My Projects": "projects", 
        "⚙️ Settings": "settings"
    }
    
    for page_name, page_key in pages.items():
        if st.sidebar.button(page_name, key=f"nav_{page_key}"):
            st.session_state.page = page_key
            st.rerun()
    
    # Projects section
    st.sidebar.markdown("---")
    st.sidebar.title("📚 My Projects")
    
    if st.sidebar.button("➕ New Project"):
        st.session_state.page = "new_project"
        st.rerun()
    
    # Display existing projects
    if projects:
        for project in projects[:5]:  # Limit to 5 recent projects
            project_title = project.get("title", "Untitled")[:25] + ("..." if len(project.get("title", "")) > 25 else "")
            
            if st.sidebar.button(
                project_title,
                key=f"sidebar_{project.get('project_id', '')}"
            ):
                st.session_state.current_project_id = project.get("project_id", "")
                st.session_state.page = "project_overview"
                st.rerun()
    else:
        st.sidebar.info("No projects available.")
    
    # Authentication section
    st.sidebar.markdown("---")
    render_auth_section()
    
    # Current project navigation
    if current_project_id and projects:
        render_project_navigation(projects, current_project_id)

def render_auth_section():
    """Render authentication section in sidebar."""
    try:
        import auth_manager
        
        if auth_manager.is_authenticated() and st.session_state.user_info:
            user_email = st.session_state.user_info.get('email', 'Unknown')
            st.sidebar.success(f"👤 Connected: {user_email[:20]}...")
            
            if st.sidebar.button("🚪 Logout"):
                auth_manager.logout()
                # Clear session state
                for key in ["google_credentials", "user_info", "sedimentation_manager"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        else:
            st.sidebar.warning("🔒 Not connected")
            if st.sidebar.button("🔑 Login with Google"):
                st.session_state.page = "login"
                st.rerun()
    except Exception as e:
        st.sidebar.error(f"Authentication error: {str(e)}")

def render_project_navigation(projects, current_project_id):
    """Render current project navigation."""
    current_project = next(
        (p for p in projects if p.get("project_id") == current_project_id),
        None
    )
    
    if current_project:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📄 Current Project")
        st.sidebar.info(current_project.get("title", "Untitled"))
        
        nav_items = [
            ("📊 Overview", "project_overview"),
            ("📋 Storyboard", "storyboard"),
            ("✍️ Writing", "redaction"),
            ("🔍 Revision", "revision"),
            ("🎯 Finalization", "finalisation"),
            ("📜 History", "history"),
            ("⚙️ Settings", "project_settings")
        ]
        
        for label, page in nav_items:
            if st.sidebar.button(label, key=f"proj_nav_{page}"):
                st.session_state.page = page
                st.rerun()

def render_home_page():
    """Render the home page."""
    st.title("🎓 Welcome to the Academic Writing System")
    
    st.markdown("""
    This system helps you structure, write, and revise your academic texts
    using an optimized workflow and advanced AI techniques.
    ### 🚀 Getting Started:
    
    1. Create a new project by clicking "➕ New Project" in the sidebar
    2. Define your article storyboard to structure your ideas
    3. Write each section following your plan
    4. Revise and improve your text with AI assistance
    5. Finalize and export your document in various formats
    
    ### ✨ Key Features:
    
    - 🎬 Storyboard Engine: Narrative structuring and idea organization
    - 🤖 Theoretical Deployment Agent: AI-assisted writing
    - 🔍 Revision Module: Style and coherence improvement
    - 📤 Finalization: Export to PDF, DOCX, and other formats
    - ☁️ Contextual Sedimentation: Save project evolution to Google Drive
    """)
    
    # Display recent projects
    if st.session_state.get('projects'):
        st.subheader("📚 Recent Projects")
        
        cols = st.columns(3)
        projects = st.session_state.projects[:6]  # Limit to 6 recent projects
        
        for i, project in enumerate(projects):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"{project.get('title', 'Untitled')}")
                    st.caption(f"📅 Modified: {project.get('last_modified', '')[:10]}")
                    st.caption(f"📝 Type: {project.get('type', 'Not specified')}")
                    
                    if st.button("Open", key=f"open_{project.get('project_id', '')}"):
                        st.session_state.current_project_id = project.get("project_id", "")
                        st.session_state.page = "project_overview"
                        st.rerun()

def render_login_page():
    """Render the login page."""
    try:
        import auth_manager
        
        st.title("🔐 Login to Academic Writing System")
        
        if not auth_manager.is_authenticated():
            st.markdown("""
            Please connect with your Google account to access the system and benefit from:
            - ☁️ Cloud synchronization of your projects
            - 📊 Progress tracking and analytics
            - 🔒 Secure data storage on Google Drive
            """)
            
            # Create OAuth flow
            flow = auth_manager.create_oauth_flow()
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <a href="{auth_url}" target="_self">
                    <button style="
                        background-color: #4285F4; 
                        color: white; 
                        border: none; 
                        padding: 12px 24px; 
                        border-radius: 8px; 
                        font-size: 16px;
                        cursor: pointer;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    ">
                        🔑 Connect with Google
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success(f"✅ Connected as {st.session_state.user_info.get('email')}")
            if st.button("Continue"):
                st.session_state.page = 'home'
                st.rerun()
    except Exception as e:
        st.error(f"Authentication initialization error: {str(e)}")
        if st.button("Back to Home"):
            st.session_state.page = "home"
            st.rerun()

def save_with_sedimentation(project_id, project_name, project_data, stage):
    """Save project state with sedimentation if available."""
    sedimentation_manager = st.session_state.get('sedimentation_manager')
    if sedimentation_manager:
        try:
            sedimentation_manager.save_project_state(
                project_id=project_id,
                project_name=project_name,
                data=project_data,
                stage=stage
            )
        except Exception as e:
            st.warning(f"Unable to save to Google Drive: {str(e)}")
            def main():
    """Main application function."""
    # Handle OAuth callback first
    if handle_oauth_callback():
        st.rerun()
        return
    
    # Initialize system components
    if MODULES_LOADED:
        system_components = initialize_system()
        if system_components[0] is None:
            st.error("Failed to initialize system components. Please check your configuration.")
            return
        
        integration_layer, user_profile, project_context, adaptive_engine, history_manager = system_components
        
        # Get projects list
        projects = project_context.get_all_projects()
        st.session_state.projects = projects
    else:
        projects = []
    
    # Initialize sedimentation manager
    if not st.session_state.get('sedimentation_manager'):
        st.session_state.sedimentation_manager = init_auth_and_sedimentation()
    
    # Render sidebar
    render_sidebar_with_auth(projects, st.session_state.current_project_id)
    
    # Main content area
    try:
        if st.session_state.page == "home":
            render_home_page()
        
        elif st.session_state.page == "login":
            render_login_page()
        
        elif st.session_state.page == "new_project":
            render_new_project_page(project_context, user_profile, history_manager)
        
        elif st.session_state.page == "project_overview":
            render_project_overview(project_context, adaptive_engine)
        
        elif st.session_state.page in ["storyboard", "redaction", "revision", "finalisation"]:
            render_project_module(
                st.session_state.page,
                project_context,
                history_manager,
                adaptive_engine,
                integration_layer
            )
        
        elif st.session_state.page == "project_settings":
            render_project_settings(project_context, history_manager)
        
        elif st.session_state.page == "history":
            render_project_history(project_context, history_manager)
        
        else:
            st.error("Page not found")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.code(traceback.format_exc())

def render_new_project_page(project_context, user_profile, history_manager):
    """Render new project creation page."""
    st.title("📝 Create New Project")
    
    # Authentication check for sedimentation
    try:
        import auth_manager
        if not auth_manager.is_authenticated():
            st.info("💡 Connect with Google to enable cloud synchronization and contextual sedimentation.")
    except Exception:
        pass
    
    with st.form("new_project_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("📄 Project Title", placeholder="Enter your project title...")
            project_type = st.selectbox(
                "📚 Project Type",
                ["Academic Article", "Thesis", "Dissertation", "Research Report", "Other"]
            )
            discipline = st.selectbox(
                "🎓 Discipline",
                ["Social Sciences", "Economics", "Law", "Computer Science", "Other"]
            )
        
        with col2:
            description = st.text_area("📝 Description", height=100, placeholder="Brief description of your project...")
            style = st.selectbox(
                "✍️ Writing Style",
                ["Standard", "Academic", "CRÉSUS-NAKAMOTO", "AcademicWritingCrypto"]
            )
            preferred_length = st.slider(
                "📏 Target Length (words)",
                min_value=1000,
                max_value=20000,
                value=5000,
                step=1000
            )
        
        submitted = st.form_submit_button("🚀 Create Project", type="primary")
            if submitted:
            if not title.strip():
                st.error("❌ Title is required.")
            else:
                try:
                    # Create project
                    preferences = {
                        "style": style,
                        "discipline": discipline,
                        "preferred_length": preferred_length
                    }
                    
                    project_id = project_context.create_project(
                        title=title.strip(),
                        description=description.strip(),
                        project_type=project_type,
                        preferences=preferences
                    )
                    
                    # Update user statistics
                    user_profile.update_statistics("projects_created")
                    user_profile.log_activity("create_project", {
                        "project_id": project_id,
                        "title": title
                    })
                    
                    # Save initial version
                    project_data = project_context.load_project(project_id)
                    history_manager.save_version(
                        project_id=project_id,
                        project_data=project_data,
                        description="Project creation"
                    )
                    
                    # Save with sedimentation
                    save_with_sedimentation(project_id, title, project_data, "creation")
                    
                    # Redirect to project
                    st.session_state.current_project_id = project_id
                    st.session_state.page = "project_overview"
                    st.success("✅ Project created successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error creating project: {str(e)}")

def render_project_overview(project_context, adaptive_engine):
    """Render project overview page."""
    if not st.session_state.current_project_id:
        st.error("❌ No project selected.")
        st.session_state.page = "home"
        st.rerun()
        return
    
    project = project_context.load_project(st.session_state.current_project_id)
    
    st.title(f"📄 {project.get('title', 'Untitled')}")
    st.caption(f"ID: {project.get('project_id', '')}")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 Words", project.get("metadata", {}).get("word_count", 0))
    with col2:
        st.metric("🔄 Revisions", project.get("metadata", {}).get("revision_count", 0))
    with col3:
        st.metric("✅ Completion", f"{project.get('metadata', {}).get('completion_percentage', 0):.1f}%")
    with col4:
        st.metric("📊 Sections", len(project.get("sections", [])))
    
    # Description
    if project.get("description"):
        st.subheader("📝 Description")
        st.write(project.get("description"))
    
    # AI suggestion
    try:
        suggestion = adaptive_engine.suggest_next_step(
            project_id=st.session_state.current_project_id,
            project_context=project_context
        )
        st.info(f"💡 AI Suggestion: {suggestion}")
    except Exception as e:
        st.warning(f"Unable to get AI suggestion: {str(e)}")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    actions = [
        ("📋 Storyboard", "storyboard"),
        ("✍️ Writing", "redaction"),
        ("🔍 Revision", "revision"),
        ("🎯 Finalization", "finalisation")
    ]
    
    for i, (label, page) in enumerate(actions):
        with [col1, col2, col3, col4][i]:
            if st.button(label, key=f"action_{page}"):
                st.session_state.page = page
                st.rerun()

# Additional helper functions would continue here...
# (render_project_module, render_project_settings, etc.)

if name == "main":
    main()
