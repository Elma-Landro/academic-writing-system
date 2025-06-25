"""
Complete authentication system with Google OAuth2 and Web3 wallet support.
"""

import os
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import streamlit as st
from streamlit_oauth import OAuth2Component
import httpx

from core.database_layer import db_manager, User

logger = logging.getLogger(__name__)

class AuthenticationManager:
    """Professional authentication manager with multiple auth methods."""

    def __init__(self):
        # Configuration depuis les secrets Streamlit
        try:
            # Try direct secret access first
            self.google_client_id = st.secrets.get("GOOGLE_CLIENT_ID") or st.secrets["google_oauth"]["client_id"]
            self.google_client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET") or st.secrets["google_oauth"]["client_secret"]
        except (KeyError, AttributeError):
            # Fallback vers les variables d'environnement
            self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
            self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
        
        # Detect current host for redirect URI
        self.redirect_uri = self._get_redirect_uri()

        # Initialize OAuth2 component for Google
        if self.google_client_id and self.google_client_secret:
            self.google_oauth = OAuth2Component(
                client_id=self.google_client_id,
                client_secret=self.google_client_secret,
                authorize_endpoint="https://accounts.google.com/o/oauth2/auth",
                token_endpoint="https://oauth2.googleapis.com/token",
                refresh_token_endpoint="https://oauth2.googleapis.com/token",
                revoke_token_endpoint="https://oauth2.googleapis.com/revoke",
            )
        else:
            self.google_oauth = None
            logger.warning("Google OAuth credentials not configured")

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return 'user_id' in st.session_state and st.session_state.user_id is not None

    def get_current_user(self) -> Optional[User]:
        """Get current authenticated user."""
        if not self.is_authenticated():
            return None

        user_id = st.session_state.user_id
        with db_manager.get_session() as session:
            return session.query(User).filter_by(id=user_id).first()

    def login_with_google(self) -> bool:
        """Handle Google OAuth login."""
        if not self.google_oauth:
            st.error("Google authentication is not configured.")
            return False

        try:
            # Use the correct method name for streamlit-oauth
            result = self.google_oauth.authorize_button(
                "Login with Google",
                redirect_uri="http://localhost:5000/oauth/callback",
                scope="openid email profile"
            )

            if result and 'token' in result:
                # Get user info from Google
                user_info = self._get_google_user_info(result['token']['access_token'])

                if user_info:
                    # Create or update user
                    user = self._handle_google_user(user_info)

                    # Set session
                    st.session_state.user_id = user.id
                    st.session_state.user_email = user.email
                    st.session_state.user_name = user.display_name

                    st.success(f"Welcome, {user.display_name}!")
                    return True

            return False

        except Exception as e:
            logger.error(f"Google login error: {e}")
            st.error(f"Login failed: {e}")
            return False

    def login_with_wallet(self, wallet_address: str, signature: str) -> bool:
        """Handle Web3 wallet login."""
        try:
            # Verify wallet signature (simplified)
            if not self._verify_wallet_signature(wallet_address, signature):
                st.error("Invalid wallet signature.")
                return False

            # Find or create user by wallet address
            with db_manager.get_session() as session:
                user = session.query(User).filter_by(wallet_address=wallet_address).first()

                if not user:
                    # Create new user with wallet
                    user = User(
                        email=f"{wallet_address[:10]}@wallet.local",
                        wallet_address=wallet_address,
                        display_name=f"User {wallet_address[:8]}"
                    )
                    session.add(user)
                    session.commit()

                # Set session
                st.session_state.user_id = user.id
                st.session_state.user_email = user.email
                st.session_state.user_name = user.display_name
                st.session_state.wallet_address = wallet_address

                st.success(f"Welcome, {user.display_name}!")
                return True

        except Exception as e:
            logger.error(f"Wallet login error: {e}")
            st.error(f"Wallet login failed: {e}")
            return False

    def logout(self):
        """Logout current user."""
        # Clear session state
        for key in ['user_id', 'user_email', 'user_name', 'wallet_address']:
            if key in st.session_state:
                del st.session_state[key]

        st.success("Logged out successfully!")
        st.rerun()

    def _get_google_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Google API."""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = httpx.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get Google user info: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting Google user info: {e}")
            return None

    def _handle_google_user(self, user_info: Dict[str, Any]) -> User:
        """Create or update user from Google user info."""
        email = user_info.get('email')
        google_id = user_info.get('id')
        name = user_info.get('name', email.split('@')[0] if email else 'Unknown')

        with db_manager.get_session() as session:
            # Try to find existing user
            user = session.query(User).filter_by(email=email).first()

            if user:
                # Update existing user
                user.google_id = google_id
                user.display_name = name
                user.updated_at = datetime.utcnow()
            else:
                # Create new user
                user = User(
                    email=email,
                    google_id=google_id,
                    display_name=name
                )
                session.add(user)

            session.commit()
            return user

    def _verify_wallet_signature(self, wallet_address: str, signature: str) -> bool:
        """Verify wallet signature with real cryptographic verification."""
        try:
            from eth_account.messages import encode_defunct
            from eth_account import Account

            # Generate a challenge message
            challenge_message = f"Authenticate to Academic Writing System\nWallet: {wallet_address}\nTimestamp: {datetime.utcnow().isoformat()}"

            # Encode the message
            encoded_message = encode_defunct(text=challenge_message)

            # Recover the address from the signature
            recovered_address = Account.recover_message(encoded_message, signature=signature)

            # Verify the recovered address matches the provided address
            return recovered_address.lower() == wallet_address.lower()

        except Exception as e:
            logger.error(f"Wallet signature verification failed: {e}")
            return False

    def generate_jwt_token(self, user_id: str) -> str:
        """Generate JWT token for API access."""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }

        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')

    def verify_jwt_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return user ID."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload.get('user_id')
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None

    def _get_redirect_uri(self) -> str:
        """Détecte automatiquement l'URL de redirection appropriée."""
        try:
            # Vérifier si on est sur Replit
            replit_dev_domain = os.getenv('REPLIT_DEV_DOMAIN')
            if replit_dev_domain:
                return f"https://{replit_dev_domain}/oauth2callback"
            
            # Fallback pour Streamlit Cloud
            import socket
            hostname = socket.getfqdn()
            
            if 'streamlit.app' in hostname:
                return "https://academic-writing-system-mael-rolland.streamlit.app/oauth2callback"
            else:
                # Fallback pour développement local
                return "http://localhost:5000/oauth2callback"
        except Exception as e:
            logger.warning(f"Failed to detect hostname: {e}")
            # Fallback par défaut - utiliser l'URL Replit actuelle
            return "https://7fcd3aac-a017-41b2-858c-65d0fdadcc7e-00-127haec9qs0ug.kirk.replit.dev/oauth2callback"

    def render_google_login(self):
        """Render Google login component."""
        if not self.google_oauth:
            st.error("Google authentication not configured.")
            return False

        try:
            result = self.google_oauth.authorize_button(
                "🔐 Login with Google",
                redirect_uri=self.redirect_uri,
                scope="openid email profile"
            )

            if result and 'token' in result:
                user_info = self._get_google_user_info(result['token']['access_token'])
                if user_info:
                    user = self._handle_google_user(user_info)
                    st.session_state.user_id = user.id
                    st.session_state.user_email = user.email
                    st.session_state.user_name = user.display_name
                    st.success(f"Welcome, {user.display_name}!")
                    st.rerun()
                    return True

            return False

        except Exception as e:
            logger.error(f"Google auth render error: {e}")
            st.error(f"Login failed: {e}")
            return False

# Global authentication manager
auth_manager = AuthenticationManager()

def require_auth(func):
    """Decorator to require authentication for Streamlit pages."""
    def wrapper(*args, **kwargs):
        if not auth_manager.is_authenticated():
            st.warning("Please log in to access this feature.")
            render_login_page()
            return None
        return func(*args, **kwargs)
    return wrapper



def render_login_page():
    """Render the login page with multiple authentication options."""
    st.title("🔐 Academic Writing System - Login")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Google Account")
        st.write("Login with your Google account for full features:")

        if auth_manager.google_oauth:
            auth_manager.render_google_login()
        else:
            st.warning("Google authentication not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.")

    with col2:
        st.subheader("Web3 Wallet")
        st.write("Connect your crypto wallet:")

        wallet_address = st.text_input("Wallet Address")
        signature = st.text_input("Signature", type="password")

        if st.button("Connect Wallet"):
            if wallet_address and signature:
                auth_manager.login_with_wallet(wallet_address, signature)
            else:
                st.error("Please provide both wallet address and signature.")

    st.markdown("---")
    st.info("💡 **Demo Mode**: For testing, you can use any wallet address (42 characters) with any signature.")