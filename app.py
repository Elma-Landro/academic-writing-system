import streamlit as st
import os
import uuid
from datetime import datetime

from utils.common import sidebar
from core.integration_layer import IntegrationLayer
from core.user_profile import UserProfile
from core.project_context import ProjectContext
from core.adaptive_engine import AdaptiveEngine
from core.history_manager import HistoryManager

from modules.storyboard import render_storyboard
from modules.redaction import render_redaction
from modules.revision import render_revision
from modules.finalisation import render_finalisation

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Système de Rédaction Académique",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation des variables de session
if "page" not in st.session_state:
    st.session_state.page = "home"
    
if "current_project_id" not in st.session_state:
    st.session_state.current_project_id = None

# Initialisation de l'authentification Google et du gestionnaire de sédimentation
@st.cache_resource
def init_auth_and_sedimentation():
    from auth_manager import is_authenticated, get_credentials
    from sedimentation_manager import SedimentationManager
    
    # Vérification de l'authentification
    if is_authenticated():
        return SedimentationManager()
    return None

# Récupération du gestionnaire de sédimentation si l'utilisateur est authentifié
sedimentation_manager = init_auth_and_sedimentation()

# Initialisation du système
@st.cache_resource
def initialize_system():
    """Initialise le système et retourne les composants principaux."""
    integration_layer = IntegrationLayer()
    integration_layer.initialize_system()
    
    user_profile = integration_layer.get_module("user_profile")
    project_context = integration_layer.get_module("project_context")
    adaptive_engine = integration_layer.get_module("adaptive_engine")
    history_manager = integration_layer.get_module("history_manager")
    
    return integration_layer, user_profile, project_context, adaptive_engine, history_manager

# Récupération des composants du système
integration_layer, user_profile, project_context, adaptive_engine, history_manager = initialize_system()

# Récupération de la liste des projets
projects = project_context.get_all_projects()

# Fonction modifiée pour la barre latérale avec authentification Google
def sidebar_with_auth(projects, current_project_id):
    # Code existant de la barre latérale
    st.sidebar.title("Navigation")
    
    # Sélection de la page
    pages = ["Accueil", "Mes projets", "Paramètres"]
    selected_page = st.sidebar.radio("Aller à", pages)
    
    if selected_page == "Accueil" and st.session_state.page != "home":
        st.session_state.page = "home"
        st.rerun()
    elif selected_page == "Mes projets" and st.session_state.page != "projects":
        st.session_state.page = "projects"
        st.rerun()
    elif selected_page == "Paramètres" and st.session_state.page != "settings":
        st.session_state.page = "settings"
        st.rerun()
    
    # Affichage des projets
    st.sidebar.title("Mes projets")
    
    if st.sidebar.button("➕ Nouveau projet"):
        st.session_state.page = "new_project"
        st.rerun()
    
    if projects:
        for project in projects:
            if st.sidebar.button(
                project.get("title", "Sans titre"),
                key=f"sidebar_{project.get('project_id', '')}"
            ):
                st.session_state.current_project_id = project.get("project_id", "")
                st.session_state.page = "project_overview"
                st.rerun()
    else:
        st.sidebar.info("Aucun projet disponible.")
    
    # Ajout de la gestion de l'authentification Google
    st.sidebar.markdown("---")
    from auth_manager import is_authenticated, logout
    
    if is_authenticated():
        user_info = st.session_state.user_info
        st.sidebar.write(f"👤 Connecté en tant que: {user_info.get('email')}")
        if st.sidebar.button("Se déconnecter"):
            logout()
            st.experimental_rerun()
    else:
        st.sidebar.warning("Non connecté")
        if st.sidebar.button("Se connecter avec Google"):
            st.session_state.page = "login"
            st.experimental_rerun()
    
    # Affichage du projet actuel
    if current_project_id:
        current_project = None
        for project in projects:
            if project.get("project_id", "") == current_project_id:
                current_project = project
                break
        
        if current_project:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Projet actuel")
            st.sidebar.info(current_project.get("title", "Sans titre"))
            
            # Navigation dans le projet
            if st.sidebar.button("Vue d'ensemble"):
                st.session_state.page = "project_overview"
                st.rerun()
            
            if st.sidebar.button("Storyboard"):
                st.session_state.page = "storyboard"
                st.rerun()
            
            if st.sidebar.button("Rédaction"):
                st.session_state.page = "redaction"
                st.rerun()
            
            if st.sidebar.button("Révision"):
                st.session_state.page = "revision"
                st.rerun()
            
            if st.sidebar.button("Finalisation"):
                st.session_state.page = "finalisation"
                st.rerun()
            
            if st.sidebar.button("Historique"):
                st.session_state.page = "history"
                st.rerun()
            
            if st.sidebar.button("Paramètres du projet"):
                st.session_state.page = "project_settings"
                st.rerun()

# Affichage de la barre latérale avec authentification
sidebar_with_auth(projects, st.session_state.current_project_id)

# Gestion des différentes pages
if st.session_state.page == "home":
    st.title("Bienvenue dans le Système de Rédaction Académique")
    
    st.markdown("""
    Ce système vous aide à structurer, rédiger et réviser vos textes académiques
    en suivant un workflow optimisé et en utilisant des techniques d'IA avancées.
    
    ### Pour commencer:
    
    1. Créez un nouveau projet en cliquant sur "➕ Nouveau projet" dans la barre latérale
    2. Définissez le storyboard de votre article
    3. Rédigez chaque section en suivant le plan
    4. Révisez et améliorez votre texte
    5. Finalisez et exportez votre document
    
    ### Fonctionnalités principales:
    
    - **Storyboard Engine**: Structuration narrative et organisation des idées
    - **Agent de Déploiement Théorique**: Rédaction assistée par IA
    - **Module de Révision**: Amélioration du style et de la cohérence
    - **Finalisation**: Export dans différents formats (PDF, DOCX, etc.)
    - **Sédimentation Contextuelle**: Sauvegarde de l'évolution de votre projet sur Google Drive
    """)
    
    # Affichage des projets récents
    if projects:
        st.subheader("Projets récents")
        
        # Création de colonnes pour afficher les projets
        cols = st.columns(3)
        
        for i, project in enumerate(projects[:6]):  # Limite à 6 projets récents
            with cols[i % 3]:
                st.markdown(f"**{project.get('title', 'Sans titre')}**")
                st.caption(f"Dernière modification: {project.get('last_modified', '')[:10]}")
                st.caption(f"Type: {project.get('type', 'Non spécifié')}")
                
                if st.button("Ouvrir", key=f"open_{project.get('project_id', '')}"):
                    st.session_state.current_project_id = project.get("project_id", "")
                    st.session_state.page = "project_overview"
                    st.rerun()

elif st.session_state.page == "login":
    # Page de login Google
    from auth_manager import create_oauth_flow, get_user_info
    
    st.title("Connexion au Système de Rédaction Académique")
    
    if not is_authenticated():
        st.write("Veuillez vous connecter avec votre compte Google pour accéder au système.")
        
        # Création du flux OAuth
        flow = create_oauth_flow()
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        # Bouton de connexion
        st.markdown(f"""
        <a href="{auth_url}" target="_self">
            <button style="background-color:#4285F4; color:white; border:none; padding:10px 20px; border-radius:5px;">
                Se connecter avec Google
            </button>
        </a>
        """, unsafe_allow_html=True)
    else:
        st.success(f"Connecté en tant que {st.session_state.user_info.get('email')}")
        st.button("Continuer", on_click=lambda: setattr(st.session_state, 'page', 'home'))

elif st.session_state.page == "new_project":
    st.title("Créer un nouveau projet")
    
    # Vérification de l'authentification pour la sédimentation
    from auth_manager import is_authenticated
    
    if not is_authenticated() and sedimentation_manager is None:
        st.warning("Pour bénéficier de la sédimentation contextuelle et de la sauvegarde sur Google Drive, veuillez vous connecter avec votre compte Google.")
    
    # Formulaire de création de projet
    with st.form("new_project_form"):
        title = st.text_input("Titre du projet")
        description = st.text_area("Description")
        
        project_type = st.selectbox(
            "Type de projet",
            ["Article académique", "Mémoire", "Thèse", "Rapport de recherche", "Autre"]
        )
        
        style = st.selectbox(
            "Style d'écriture",
            ["Standard", "Académique", "CRÉSUS-NAKAMOTO", "AcademicWritingCrypto"]
        )
        
        discipline = st.selectbox(
            "Discipline",
            ["Sciences sociales", "Économie", "Droit", "Informatique", "Autre"]
        )
        
        preferred_length = st.slider(
            "Longueur cible (mots)",
            min_value=1000,
            max_value=20000,
            value=5000,
            step=1000
        )
        
        submitted = st.form_submit_button("Créer le projet")
        
        if submitted:
            if not title:
                st.error("Le titre est obligatoire.")
            else:
                # Création du projet
                preferences = {
                    "style": style,
                    "discipline": discipline,
                    "preferred_length": preferred_length
                }
                
                project_id = project_context.create_project(
                    title=title,
                    description=description,
                    project_type=project_type,
                    preferences=preferences
                )
                
                # Mise à jour des statistiques utilisateur
                user_profile.update_statistics("projects_created")
                
                # Journalisation de l'activité
                user_profile.log_activity("create_project", {
                    "project_id": project_id,
                    "title": title
                })
                
                # Sauvegarde de la première version dans l'historique
                project_data = project_context.load_project(project_id)
                history_manager.save_version(
                    project_id=project_id,
                    project_data=project_data,
                    description="Création du projet"
                )
                
                # Sauvegarde avec sédimentation si l'utilisateur est connecté
                if sedimentation_manager:
                    sedimentation_manager.save_project_state(
                        project_id=project_id,
                        project_name=title,
                        data=project_data,
                        stage="creation"
                    )
                
                # Redirection vers la page du projet
                st.session_state.current_project_id = project_id
                st.session_state.page = "project_overview"
                st.success("Projet créé avec succès!")
                st.rerun()

elif st.session_state.page == "project_overview":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    # Chargement des données du projet
    project = project_context.load_project(st.session_state.current_project_id)
    
    # Affichage des informations du projet
    st.title(project.get("title", "Sans titre"))
    st.caption(f"ID: {project.get('project_id', '')}")
    
    # Affichage des métadonnées
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Mots", project.get("metadata", {}).get("word_count", 0))
    
    with col2:
        st.metric("Révisions", project.get("metadata", {}).get("revision_count", 0))
    
    with col3:
        st.metric("Complétion", f"{project.get('metadata', {}).get('completion_percentage', 0):.1f}%")
    
    # Description du projet
    st.subheader("Description")
    st.write(project.get("description", "Aucune description."))
    
    # Suggestion du moteur adaptatif
    suggestion = adaptive_engine.suggest_next_step(
        project_id=st.session_state.current_project_id,
        project_context=project_context
    )
    
    st.info(f"💡 **Suggestion**: {suggestion}")
    
    # Sections du projet
    st.subheader("Sections")
    
    if not project.get("sections"):
        st.write("Aucune section n'a encore été créée.")
        
        if st.button("Commencer le storyboard"):
            st.session_state.page = "storyboard"
            st.rerun()
    else:
        # Affichage des sections existantes
        for i, section in enumerate(project.get("sections", [])):
            with st.expander(f"{i+1}. {section.get('title', 'Sans titre')}"):
                st.write(section.get("content", ""))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Éditer", key=f"edit_{section.get('section_id', '')}"):
                        st.session_state.current_section_id = section.get("section_id", "")
                        st.session_state.page = "redaction"
                        st.rerun()
                
                with col2:
                    if st.button("Réviser", key=f"revise_{section.get('section_id', '')}"):
                        st.session_state.current_section_id = section.get("section_id", "")
                        st.session_state.page = "revision"
                        st.rerun()
    
    # Boutons d'action
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Storyboard"):
            st.session_state.page = "storyboard"
            st.rerun()
    
    with col2:
        if st.button("Rédaction"):
            st.session_state.page = "redaction"
            st.rerun()
    
    with col3:
        if st.button("Révision"):
            st.session_state.page = "revision"
            st.rerun()
    
    with col4:
        if st.button("Finalisation"):
            st.session_state.page = "finalisation"
            st.rerun()
    
    # Visualisation de la sédimentation si l'utilisateur est connecté
    if sedimentation_manager:
        st.markdown("---")
        st.subheader("Sédimentation contextuelle")
        
        if st.button("Afficher l'historique de sédimentation"):
            sedimentation_manager.visualize_sedimentation(
                project_id=st.session_state.current_project_id,
                project_name=project.get("title", "Sans titre")
            )

elif st.session_state.page == "storyboard":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    # Chargement des données du projet
    project = project_context.load_project(st.session_state.current_project_id)
    
    # Rendu du module de storyboard
    render_storyboard(
        project_id=st.session_state.current_project_id,
        project_context=project_context,
        history_manager=history_manager,
        adaptive_engine=adaptive_engine
    )
    
    # Sauvegarde avec sédimentation si l'utilisateur est connecté
    if sedimentation_manager:
        # Rechargement du projet après modifications
        updated_project = project_context.load_project(st.session_state.current_project_id)
        
        sedimentation_manager.save_project_state(
            project_id=st.session_state.current_project_id,
            project_name=project.get("title", "Sans titre"),
            data=updated_project,
            stage="storyboard"
        )

elif st.session_state.page == "redaction":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    # Chargement des données du projet
    project = project_context.load_project(st.session_state.current_project_id)
    
    # Rendu du module de rédaction
    render_redaction(
        project_id=st.session_state.current_project_id,
        section_id=st.session_state.get("current_section_id"),
        project_context=project_context,
        history_manager=history_manager,
        adaptive_engine=adaptive_engine,
        integration_layer=integration_layer
    )
    
    # Sauvegarde avec sédimentation si l'utilisateur est connecté
    if sedimentation_manager:
        # Rechargement du projet après modifications
        updated_project = project_context.load_project(st.session_state.current_project_id)
        
        sedimentation_manager.save_project_state(
            project_id=st.session_state.current_project_id,
            project_name=project.get("title", "Sans titre"),
            data=updated_project,
            stage="redaction"
        )

elif st.session_state.page == "revision":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    # Chargement des données du projet
    project = project_context.load_project(st.session_state.current_project_id)
    
    # Rendu du module de révision
    render_revision(
        project_id=st.session_state.current_project_id,
        section_id=st.session_state.get("current_section_id"),
        project_context=project_context,
        history_manager=history_manager,
        adaptive_engine=adaptive_engine,
        integration_layer=integration_layer
    )
    
    # Sauvegarde avec sédimentation si l'utilisateur est connecté
    if sedimentation_manager:
        # Rechargement du projet après modifications
        updated_project = project_context.load_project(st.session_state.current_project_id)
        
        sedimentation_manager.save_project_state(
            project_id=st.session_state.current_project_id,
            project_name=project.get("title", "Sans titre"),
            data=updated_project,
            stage="revision"
        )

elif st.session_state.page == "finalisation":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    # Chargement des données du projet
    project = project_context.load_project(st.session_state.current_project_id)
    
    # Rendu du module de finalisation
    render_finalisation(
        project_id=st.session_state.current_project_id,
        project_context=project_context,
        history_manager=history_manager
    )
    
    # Sauveg
