import streamlit as st
import os
import uuid
from datetime import datetime
import sys

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Système de Rédaction Académique",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.write("✅ App bien lancée")

# Gestion du retour OAuth (si code présent dans l’URL)
# Gestion du retour OAuth (si code présent dans l’URL)
if "code" in st.query_params:
    try:
        import auth_manager
        code = st.query_params["code"][0]
        st.write("✅ Code OAuth reçu :", code)

        flow = auth_manager.create_oauth_flow()
        st.write("✅ Flux OAuth créé avec succès")

        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Vérification du token
        if not credentials or not credentials.token:
            st.error("❌ Aucun token OAuth récupéré.")
            st.stop()

        st.write("✅ Token récupéré :", credentials.token)

        # Stockage dans la session
        st.session_state.google_credentials = {
            'token': credentials.token,
            'refresh_token': getattr(credentials, 'refresh_token', None),
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
        }

        user_info = auth_manager.get_user_info(credentials)
        st.session_state.user_info = user_info
        st.write("✅ Utilisateur connecté :", user_info.get("email", "inconnu"))

        # Nettoyage de l’URL
        st.experimental_set_query_params()
        st.experimental_rerun()

    except Exception as e:
        st.error(f"❌ Erreur OAuth2 : {str(e)}")
        st.write("❌ Exception complète :", e)
        
st.markdown("### Debug OAuth")
st.write("Query params:", st.query_params)
st.write("User info:", st.session_state.get('user_info'))
st.write("Google credentials:", st.session_state.get('google_credentials'))

# Ajout du répertoire courant au chemin de recherche Python
# Cela permet d'importer les modules à la racine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importation des modules core existants
from utils.common import sidebar
from core.integration_layer import IntegrationLayer
from core.user_profile import UserProfile
from core.project_context import ProjectContext
from core.adaptive_engine import AdaptiveEngine
from core.history_manager import HistoryManager

# Importation des modules de rendu
from modules.storyboard import render_storyboard
from modules.redaction import render_redaction
from modules.revision import render_revision
from modules.finalisation import render_finalisation

# Initialisation des variables de session
if "page" not in st.session_state:
    st.session_state.page = "home"
    
if "current_project_id" not in st.session_state:
    st.session_state.current_project_id = None

# Initialisation de l'authentification Google et du gestionnaire de sédimentation
@st.cache_resource
def init_auth_and_sedimentation():
    """Initialise l'authentification Google et le gestionnaire de sédimentation."""
    try:
        # Import absolu des modules d'authentification
        import auth_manager
        import sedimentation_manager
        
        # Vérification de l'authentification
        if auth_manager.is_authenticated():
            return sedimentation_manager.SedimentationManager()
        return None
    except Exception as e:
        st.warning(f"Impossible d'initialiser l'authentification Google: {str(e)}")
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
    try:
        # Import absolu du module d'authentification
        import auth_manager
        
        if auth_manager.is_authenticated():
            user_info = st.session_state.user_info
            st.sidebar.write(f"👤 Connecté en tant que: {user_info.get('email')}")
            if st.sidebar.button("Se déconnecter"):
                auth_manager.logout()
                st.rerun()
        else:
            st.sidebar.warning("Non connecté")
        if st.sidebar.button("Se connecter avec Google"):
            flow = auth_manager.create_oauth_flow()
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
    except Exception as e:
            st.sidebar.warning(f"Authentification non disponible: {str(e)}")
    
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
    try:
        # Import absolu des modules d'authentification
        import auth_manager
        
        st.title("Connexion au Système de Rédaction Académique")
        
        if not auth_manager.is_authenticated():
            st.write("Veuillez vous connecter avec votre compte Google pour accéder au système.")
            
            # Création du flux OAuth
            flow = auth_manager.create_oauth_flow()
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
            if st.button("Continuer"):
                st.session_state.page = 'home'
                st.rerun()
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation de l'authentification: {str(e)}")
        if st.button("Retour à l'accueil"):
            st.session_state.page = "home"
            st.rerun()

elif st.session_state.page == "new_project":
    st.title("Créer un nouveau projet")
    
    # Vérification de l'authentification pour la sédimentation
    try:
        import auth_manager
        
        if not auth_manager.is_authenticated() and sedimentation_manager is None:
            st.warning("Pour bénéficier de la sédimentation contextuelle et de la sauvegarde sur Google Drive, veuillez vous connecter avec votre compte Google.")
    except Exception as e:
        st.warning(f"Authentification non disponible: {str(e)}")
    
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
                
                # Sauvegarde avec sédimentation si l'utilisateur est authentifié et le gestionnaire est disponible
                if sedimentation_manager:
                    try:
                        sedimentation_manager.save_project_state(
                            project_id=project_id,
                            project_name=title,
                            data=project_data,
                            stage="creation"
                        )
                    except Exception as e:
                        st.warning(f"Impossible de sauvegarder sur Google Drive: {str(e)}")
                
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
        try:
            st.markdown("---")
            st.subheader("Sédimentation contextuelle")
            
            if st.button("Afficher l'historique de sédimentation"):
                sedimentation_manager.visualize_sedimentation(
                    project_id=st.session_state.current_project_id,
                    project_name=project.get("title", "Sans titre")
                )
        except Exception as e:
            st.warning(f"Impossible d'afficher la sédimentation: {str(e)}")

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
        try:
            # Rechargement du projet après modifications
            updated_project = project_context.load_project(st.session_state.current_project_id)
            
            sedimentation_manager.save_project_state(
                project_id=st.session_state.current_project_id,
                project_name=project.get("title", "Sans titre"),
                data=updated_project,
                stage="storyboard"
            )
        except Exception as e:
            st.warning(f"Impossible de sauvegarder sur Google Drive: {str(e)}")

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
        try:
            # Rechargement du projet après modifications
            updated_project = project_context.load_project(st.session_state.current_project_id)
            
            sedimentation_manager.save_project_state(
                project_id=st.session_state.current_project_id,
                project_name=project.get("title", "Sans titre"),
                data=updated_project,
                stage="redaction"
            )
        except Exception as e:
            st.warning(f"Impossible de sauvegarder sur Google Drive: {str(e)}")

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
        try:
            # Rechargement du projet après modifications
            updated_project = project_context.load_project(st.session_state.current_project_id)
            
            sedimentation_manager.save_project_state(
                project_id=st.session_state.current_project_id,
                project_name=project.get("title", "Sans titre"),
                data=updated_project,
                stage="revision"
            )
        except Exception as e:
            st.warning(f"Impossible de sauvegarder sur Google Drive: {str(e)}")

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
    
    # Sauvegarde avec sédimentation si l'utilisateur est connecté
    if sedimentation_manager:
        try:
            # Rechargement du projet après modifications
            updated_project = project_context.load_project(st.session_state.current_project_id)
            
            sedimentation_manager.save_project_state(
                project_id=st.session_state.current_project_id,
                project_name=project.get("title", "Sans titre"),
                data=updated_project,
                stage="finalisation"
            )
        except Exception as e:
            st.warning(f"Impossible de sauvegarder sur Google Drive: {str(e)}")

elif st.session_state.page == "project_settings":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    # Chargement des données du projet
    project = project_context.load_project(st.session_state.current_project_id)
    
    st.title("Paramètres du projet")
    st.subheader(project.get("title", "Sans titre"))
    
    # Formulaire de modification des paramètres
    with st.form("project_settings_form"):
        title = st.text_input("Titre du projet", value=project.get("title", ""))
        description = st.text_area("Description", value=project.get("description", ""))
        
        project_type = st.selectbox(
            "Type de projet",
            ["Article académique", "Mémoire", "Thèse", "Rapport de recherche", "Autre"],
            index=["Article académique", "Mémoire", "Thèse", "Rapport de recherche", "Autre"].index(project.get("type", "Article académique"))
        )
        
        style = st.selectbox(
            "Style d'écriture",
            ["Standard", "Académique", "CRÉSUS-NAKAMOTO", "AcademicWritingCrypto"],
            index=["Standard", "Académique", "CRÉSUS-NAKAMOTO", "AcademicWritingCrypto"].index(project.get("preferences", {}).get("style", "Standard"))
        )
        
        discipline = st.selectbox(
            "Discipline",
            ["Sciences sociales", "Économie", "Droit", "Informatique", "Autre"],
            index=["Sciences sociales", "Économie", "Droit", "Informatique", "Autre"].index(project.get("preferences", {}).get("discipline", "Sciences sociales"))
        )
        
        preferred_length = st.slider(
            "Longueur cible (mots)",
            min_value=1000,
            max_value=20000,
            value=project.get("preferences", {}).get("preferred_length", 5000),
            step=1000
        )
        
        submitted = st.form_submit_button("Enregistrer les modifications")
        
        if submitted:
            if not title:
                st.error("Le titre est obligatoire.")
            else:
                # Mise à jour des données du projet
                project["title"] = title
                project["description"] = description
                project["type"] = project_type
                project["preferences"] = {
                    "style": style,
                    "discipline": discipline,
                    "preferred_length": preferred_length
                }
                
                # Sauvegarde du projet
                project_context.save_project(project)
                
                # Sauvegarde de la version dans l'historique
                history_manager.save_version(
                    project_id=st.session_state.current_project_id,
                    project_data=project,
                    description="Modification des paramètres"
                )
                
                # Sauvegarde avec sédimentation si l'utilisateur est connecté
                if sedimentation_manager:
                    try:
                        sedimentation_manager.save_project_state(
                            project_id=st.session_state.current_project_id,
                            project_name=title,
                            data=project,
                            stage="settings_update"
                        )
                    except Exception as e:
                        st.warning(f"Impossible de sauvegarder sur Google Drive: {str(e)}")
                
                st.success("Paramètres enregistrés avec succès!")
                
                # Redirection vers la page du projet
                st.session_state.page = "project_overview"
                st.rerun()
    
    # Bouton de suppression du projet
    st.markdown("---")
    st.subheader("Zone de danger")
    
    if st.button("Supprimer ce projet", type="primary", help="Cette action est irréversible!"):
        if project_context.delete_project(st.session_state.current_project_id):
            st.success("Projet supprimé avec succès!")
            
            # Redirection vers la page d'accueil
            st.session_state.current_project_id = None
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error("Erreur lors de la suppression du projet.")

elif st.session_state.page == "history":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    st.title("Historique du projet")
    
    # Chargement des données du projet
    project = project_context.load_project(st.session_state.current_project_id)
    st.subheader(project.get("title", "Sans titre"))
    
    # Récupération de l'historique
    history = history_manager.get_project_history(st.session_state.current_project_id)
    
    if not history:
        st.info("Aucun historique disponible pour ce projet.")
    else:
        # Affichage de l'historique
        for i, version in enumerate(history):
            with st.expander(f"Version {i+1} - {version.get('timestamp', '')} - {version.get('description', 'Sans description')}"):
                st.json(version.get("data", {}))
                
                if st.button(f"Restaurer cette version", key=f"restore_{i}"):
                    # Restauration de la version
                    project_context.save_project(version.get("data", {}))
                    
                    # Sauvegarde de la restauration dans l'historique
                    history_manager.save_version(
                        project_id=st.session_state.current_project_id,
                        project_data=version.get("data", {}),
                        description=f"Restauration de la version {i+1}"
                    )
                    
                    # Sauvegarde avec sédimentation si l'utilisateur est connecté
                    if sedimentation_manager:
                        try:
                            sedimentation_manager.save_project_state(
                                project_id=st.session_state.current_project_id,
                                project_name=project.get("title", "Sans titre"),
                                data=version.get("data", {}),
                                stage=f"restore_version_{i+1}"
                            )
                        except Exception as e:
                            st.warning(f"Impossible de sauvegarder sur Google Drive: {str(e)}")
                    
                    st.success("Version restaurée avec succès!")
                    st.rerun()
    
    # Affichage de l'historique de sédimentation si l'utilisateur est connecté
    if sedimentation_manager:
        try:
            st.markdown("---")
            st.subheader("Historique de sédimentation")
            
            sedimentation_manager.visualize_sedimentation(
                project_id=st.session_state.current_project_id,
                project_name=project.get("title", "Sans titre")
            )
        except Exception as e:
            st.warning(f"Impossible d'afficher la sédimentation: {str(e)}")

# Gestion du callback OAuth
if "code" in st.query_params:
    try:
        # Import absolu des modules d'authentification
        import auth_manager
        
        # Récupération du code d'autorisation
        code = st.query_params["code"][0]
        
        # Création du flux OAuth
        flow = auth_manager.create_oauth_flow()
        
        # Échange du code contre un token
        flow.fetch_token(code=code)
        
        # Récupération des identifiants
        credentials = flow.credentials
        
        # Stockage des identifiants dans la session
        st.session_state.google_credentials = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Récupération des informations utilisateur
        user_info = auth_manager.get_user_info(credentials)
        st.session_state.user_info = user_info
        
        # Initialisation du gestionnaire de sédimentation
        st.session_state.sedimentation_manager = init_auth_and_sedimentation()
        
        # Redirection vers la page d'accueil
        st.success(f"Connecté en tant que {user_info.get('email')}")
        st.rerun()
    except Exception as e:
        st.error(f"Erreur lors de l'authentification: {str(e)}")
