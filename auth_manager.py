import streamlit as st
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json
from typing import Optional, Dict, Any
import logging

# Configuration
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email'
]

REDIRECT_URI = "https://ing-system-mael-rolland.streamlit.app/oauth2callback"

class GoogleAuthManager:
    """Gestionnaire d'authentification Google robuste avec gestion d'erreurs complète."""

    def __init__(self):
        self.credentials_file = "data/user_credentials.json"
        self.logger = logging.getLogger(__name__)
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Assure que le répertoire data existe."""
        os.makedirs("data", exist_ok=True)

    def _get_client_config(self) -> Dict[str, Any]:
        """Récupère la configuration client depuis les secrets."""
        try:
            # Utiliser directement les variables d'environnement (secrets Replit)
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

            # Si pas trouvé, essayer les secrets Streamlit
            if not client_id and hasattr(st, 'secrets'):
                try:
                    client_id = st.secrets.get("GOOGLE_CLIENT_ID") or st.secrets["google"]["client_id"]
                    client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET") or st.secrets["google"]["client_secret"]
                except (KeyError, AttributeError):
                    pass

            if not client_id or not client_secret:
                raise ValueError("Google OAuth credentials not found")

            return {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [
                        "https://ing-system-mael-rolland.streamlit.app/oauth2callback",
                        "https://academic-writing-system-mael-rolland.streamlit.app/oauth2callback"
                    ]
                }
            }
        except Exception as e:
            self.logger.error(f"Missing Google configuration: {e}")
            raise ValueError(f"Configuration Google manquante: {e}")

    def create_oauth_flow(self) -> Optional[Flow]:
        """Crée le flow OAuth avec gestion d'erreurs."""
        try:
            client_config = self._get_client_config()
            flow = Flow.from_client_config(
                client_config,
                scopes=SCOPES,
                redirect_uri=self.get_redirect_uri()
            )
            return flow
        except Exception as e:
            self.logger.error(f"Erreur création flow OAuth: {e}")
            st.error(f"Erreur de configuration OAuth: {e}")
            return None

    def get_authorization_url(self) -> Optional[str]:
        """Génère l'URL d'autorisation."""
        try:
            flow = self.create_oauth_flow()
            if not flow:
                return None

            auth_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )

            # Stocker l'état pour validation
            st.session_state.oauth_state = state
            self.logger.info("URL d'autorisation générée avec succès")
            return auth_url

        except Exception as e:
            self.logger.error(f"Erreur génération URL d'autorisation: {e}")
            st.error(f"Erreur lors de la génération de l'URL d'autorisation: {e}")
            return None

    def handle_oauth_callback(self, code: str, state: str = None) -> bool:
        """Gère le callback OAuth avec validation d'état."""
        try:
            # Validation de l'état (si applicable)
            if state and hasattr(st.session_state, 'oauth_state'):
                if state != st.session_state.oauth_state:
                    self.logger.warning("État OAuth invalide")
                    st.error("État d'authentification invalide")
                    return False

            flow = self.create_oauth_flow()
            if not flow:
                return False

            # Échange du code contre les credentials
            flow.fetch_token(code=code)
            credentials = flow.credentials

            # Validation des credentials
            if not self._validate_credentials(credentials):
                return False

            # Sauvegarde des credentials
            self._save_credentials(credentials)

            # Récupération des informations utilisateur
            user_info = self._get_user_info(credentials)
            if user_info:
                st.session_state.user_info = user_info
                st.session_state.is_authenticated = True

                self.logger.info(f"Authentification réussie pour {user_info.get('email', 'utilisateur inconnu')}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Erreur callback OAuth: {e}")
            st.error(f"Erreur lors de l'authentification: {e}")
            return False

    def _validate_credentials(self, credentials: Credentials) -> bool:
        """Valide les credentials reçus."""
        try:
            if not credentials:
                raise ValueError("Credentials vides")

            if not credentials.valid:
                if credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                else:
                    raise ValueError("Credentials invalides et non renouvelables")

            return True

        except Exception as e:
            self.logger.error(f"Validation credentials échouée: {e}")
            st.error(f"Credentials invalides: {e}")
            return False

    def _save_credentials(self, credentials: Credentials):
        """Sauvegarde sécurisée des credentials."""
        try:
            creds_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }

            with open(self.credentials_file, 'w') as f:
                json.dump(creds_data, f, indent=2)

            self.logger.info("Credentials sauvegardés avec succès")

        except Exception as e:
            self.logger.error(f"Erreur sauvegarde credentials: {e}")
            st.error(f"Erreur lors de la sauvegarde: {e}")

    def _load_credentials(self) -> Optional[Credentials]:
        """Charge les credentials sauvegardés."""
        try:
            if not os.path.exists(self.credentials_file):
                return None

            with open(self.credentials_file, 'r') as f:
                creds_data = json.load(f)

            credentials = Credentials(
                token=creds_data['token'],
                refresh_token=creds_data.get('refresh_token'),
                token_uri=creds_data['token_uri'],
                client_id=creds_data['client_id'],
                client_secret=creds_data['client_secret'],
                scopes=creds_data['scopes']
            )

            # Validation et rafraîchissement si nécessaire
            if self._validate_credentials(credentials):
                return credentials

            return None

        except Exception as e:
            self.logger.error(f"Erreur chargement credentials: {e}")
            return None

    def _get_user_info(self, credentials: Credentials) -> Optional[Dict[str, Any]]:
        """Récupère les informations utilisateur."""
        try:
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()

            return {
                'id': user_info.get('id'),
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'given_name': user_info.get('given_name'),
                'picture': user_info.get('picture')
            }

        except Exception as e:
            self.logger.error(f"Erreur récupération info utilisateur: {e}")
            st.error(f"Erreur lors de la récupération des informations utilisateur: {e}")
            return None

    def is_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est authentifié."""
        return st.session_state.get('is_authenticated', False)

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Récupère les informations de l'utilisateur actuel."""
        return st.session_state.get('user_info')

    def get_credentials(self) -> Optional[Credentials]:
        """Récupère les credentials actuels."""
        if self.is_authenticated():
            return self._load_credentials()
        return None

    def logout(self):
        """Déconnecte l'utilisateur."""
        try:
            # Supprimer le fichier de credentials
            if os.path.exists(self.credentials_file):
                os.remove(self.credentials_file)

            # Nettoyer la session
            st.session_state.is_authenticated = False
            st.session_state.user_info = None
            if hasattr(st.session_state, 'oauth_state'):
                del st.session_state.oauth_state

            self.logger.info("Déconnexion réussie")

        except Exception as e:
            self.logger.error(f"Erreur déconnexion: {e}")
            st.error(f"Erreur lors de la déconnexion: {e}")

    def get_auth_status(self) -> Dict[str, Any]:
        """Récupère le statut d'authentification complet."""
        return {
            'is_authenticated': self.is_authenticated(),
            'user': self.get_current_user(),
            'has_valid_credentials': self._load_credentials() is not None
        }

    def get_redirect_uri(self):
        """Obtient l'URI de redirection basée sur l'environnement."""
        # Toujours utiliser l'URL Streamlit déployée
        return "https://ing-system-mael-rolland.streamlit.app/oauth2callback"

    def is_replit_environment(self) -> bool:
        """Vérifie si l'environnement est Replit."""
        return "REPL_ID" in os.environ

# Instance globale
auth_manager = GoogleAuthManager()

# Fonctions d'interface pour compatibilité
def is_authenticated() -> bool:
    return auth_manager.is_authenticated()

def get_current_user() -> Optional[Dict[str, Any]]:
    return auth_manager.get_current_user()

def get_auth_status() -> Dict[str, Any]:
    return auth_manager.get_auth_status()

def handle_oauth_callback(code: str, state: str = None) -> bool:
    return auth_manager.handle_oauth_callback(code, state)

def logout():
    auth_manager.logout()

def login_button():
    """Affiche le bouton de connexion."""
    if not auth_manager.is_authenticated():
        try:
            auth_url = auth_manager.get_authorization_url()
            if auth_url:
                st.markdown(f"""
                <a href="{auth_url}" target="_self">
                    <button style="
                        background-color: #4285f4;
                        color: white;
                        padding: 10px 20px;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 16px;
                        width: 100%;
                    ">
                        🔐 Se connecter avec Google
                    </button>
                </a>
                """, unsafe_allow_html=True)
            else:
                st.error("Impossible de générer l'URL de connexion. Vérifiez la configuration.")
                st.info("Assurez-vous que GOOGLE_CLIENT_ID et GOOGLE_CLIENT_SECRET sont configurés dans les secrets.")
        except Exception as e:
            st.error(f"Erreur lors de la création du bouton de connexion: {e}")
            st.info("Vérifiez la configuration Google OAuth dans les secrets Replit.")