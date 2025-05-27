
"""
Module de gestion de l'authentification Google.
Permet la connexion des utilisateurs via Google OAuth.
"""

import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Configuration des scopes (permissions)
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/drive.file"
]

def create_oauth_flow():
    """Crée un flux OAuth à partir de la configuration stockée dans Streamlit secrets."""
    client_config = {
        "web": {
            "client_id": st.secrets["google_oauth"]["client_id"],
            "client_secret": st.secrets["google_oauth"]["client_secret"],
            "auth_uri": st.secrets["google_oauth"]["auth_uri"],
            "token_uri": st.secrets["google_oauth"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google_oauth"]["auth_provider_x509_cert_url"],
            "redirect_uris": st.secrets["google_oauth"]["redirect_uris"]
        }
    }

    redirect_uris = st.secrets["google_oauth"]["redirect_uris"]
    redirect_uri = redirect_uris[0] if len(redirect_uris) == 1 else redirect_uris[1]

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

    return flow

def get_user_info(credentials):
    """Récupère les informations de l'utilisateur connecté."""
    service = build('oauth2', 'v2', credentials=credentials)
    return service.userinfo().get().execute()

def is_authenticated():
    """Vérifie si l'utilisateur est connecté."""
    return 'google_credentials' in st.session_state

def get_credentials():
    """Récupère les identifiants de l'utilisateur connecté."""
    if is_authenticated():
        return Credentials.from_authorized_user_info(
            st.session_state.google_credentials
        )
    return None

def logout():
    """Déconnecte l'utilisateur."""
    if 'google_credentials' in st.session_state:
        del st.session_state.google_credentials
    if 'user_info' in st.session_state:
        del st.session_state.user_info
