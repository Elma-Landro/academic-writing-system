
"""
Module de gestion de l'authentification Google OAuth2.
Utilise les secrets Streamlit pour sécuriser les credentials.
"""

import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import logging

# Configuration des scopes (permissions)
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

def create_oauth_flow():
    """Crée un flux OAuth à partir des secrets Streamlit."""
    try:
        # Vérifier que les secrets sont configurés
        if "google_oauth" not in st.secrets:
            raise ValueError("Section 'google_oauth' manquante dans secrets.toml")
        
        oauth_secrets = st.secrets["google_oauth"]
        required_fields = ["client_id", "client_secret", "redirect_uri"]
        
        for field in required_fields:
            if field not in oauth_secrets:
                raise ValueError(f"Champ '{field}' manquant dans google_oauth secrets")
        
        # Configuration client OAuth
        client_config = {
            "web": {
                "client_id": oauth_secrets["client_id"],
                "client_secret": oauth_secrets["client_secret"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=oauth_secrets["redirect_uri"]
        )
        
        return flow
        
    except Exception as e:
        st.error(f"Erreur configuration OAuth: {str(e)}")
        return None

def get_authorization_url():
    """Génère l'URL d'autorisation Google."""
    try:
        flow = create_oauth_flow()
        if not flow:
            return None
            
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Stocker le state pour validation
        st.session_state.oauth_state = state
        return authorization_url
        
    except Exception as e:
        st.error(f"Erreur génération URL: {str(e)}")
        return None

def handle_oauth_callback(code, state):
    """Traite le callback OAuth avec le code d'autorisation."""
    try:
        # MANDATORY state verification - no exceptions
        if not state or st.session_state.get('oauth_state') != state:
            raise ValueError("État OAuth invalide - possible attaque CSRF")
        
        flow = create_oauth_flow()
        if not flow:
            return False
            
        # Échanger le code contre des tokens
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Stocker les credentials en session
        st.session_state.google_credentials = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Récupérer les infos utilisateur
        user_info = get_user_info(credentials)
        if user_info:
            st.session_state.user_info = user_info
            return True
        else:
            raise ValueError("Impossible de récupérer les informations utilisateur")
            
    except Exception as e:
        st.error(f"Erreur callback OAuth: {str(e)}")
        return False

def get_user_info(credentials):
    """Récupère les informations de l'utilisateur connecté."""
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info
    except Exception as e:
        st.error(f"Erreur récupération utilisateur: {str(e)}")
        return None

def is_authenticated():
    """Vérifie si l'utilisateur est connecté."""
    return (
        'google_credentials' in st.session_state and 
        'user_info' in st.session_state and
        st.session_state.google_credentials is not None
    )

def get_current_user():
    """Retourne les informations de l'utilisateur actuel."""
    if is_authenticated():
        return st.session_state.user_info
    return None

def get_credentials():
    """Récupère les credentials OAuth de l'utilisateur connecté."""
    if is_authenticated():
        try:
            return Credentials.from_authorized_user_info(
                st.session_state.google_credentials
            )
        except Exception as e:
            st.error(f"Erreur credentials: {str(e)}")
            logout()
            return None
    return None

def refresh_token_if_needed():
    """Rafraîchit le token si nécessaire."""
    try:
        credentials = get_credentials()
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh()
            # Mettre à jour en session
            st.session_state.google_credentials.update({
                'token': credentials.token
            })
            return True
        return False
    except Exception as e:
        st.warning(f"Impossible de rafraîchir le token: {str(e)}")
        logout()
        return False

def logout():
    """Déconnecte l'utilisateur."""
    keys_to_remove = [
        'google_credentials', 
        'user_info', 
        'oauth_state'
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

def login_button():
    """Affiche le bouton de connexion Google."""
    if not is_authenticated():
        if st.button("🔐 Se connecter avec Google", type="primary"):
            auth_url = get_authorization_url()
            if auth_url:
                st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', 
                          unsafe_allow_html=True)
                st.info("Redirection vers Google...")
            else:
                st.error("Impossible de générer l'URL d'authentification")
    else:
        user = get_current_user()
        st.success(f"✅ Connecté comme {user.get('name', user.get('email', 'Utilisateur'))}")
        if st.button("🚪 Se déconnecter"):
            logout()
            st.rerun()

def require_auth(func):
    """Décorateur pour exiger une authentification."""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            st.warning("⚠️ Vous devez vous connecter pour accéder à cette fonctionnalité.")
            login_button()
            return None
        
        # Vérifier si le token doit être rafraîchi
        refresh_token_if_needed()
        
        return func(*args, **kwargs)
    return wrapper

def get_auth_status():
    """Retourne le statut d'authentification détaillé."""
    status = {
        'is_authenticated': is_authenticated(),
        'user': get_current_user(),
        'has_valid_token': False
    }
    
    if status['is_authenticated']:
        credentials = get_credentials()
        status['has_valid_token'] = credentials and not credentials.expired
    
    return status
