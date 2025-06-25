
"""
Secure authentication system with proper token management and session handling.
"""

import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import hashlib
import secrets
from sqlalchemy.orm import Session
from core.database_layer import User, db_manager
from core.config_manager import config_manager
import logging

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Custom authentication exception."""
    pass

class TokenManager:
    """Secure JWT token management."""
    
    def __init__(self):
        self.auth_config = config_manager.get_auth_config()
        self.secret_key = self.auth_config.session_secret_key
        self.token_expiry_hours = self.auth_config.token_expiry_hours
    
    def generate_access_token(self, user_id: str, email: str) -> str:
        """Generate secure access token."""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.now(timezone.utc) + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.now(timezone.utc),
            'jti': secrets.token_urlsafe(32)  # Unique token ID
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def generate_refresh_token(self, user_id: str) -> str:
        """Generate secure refresh token."""
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.now(timezone.utc) + timedelta(days=30),
            'iat': datetime.now(timezone.utc),
            'jti': secrets.token_urlsafe(32)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate and decode token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")

class SecureAuthSystem:
    """Secure authentication system with proper session management."""
    
    def __init__(self):
        self.token_manager = TokenManager()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
    def create_user(self, google_user_info: Dict[str, Any]) -> User:
        """Create or update user from Google OAuth info."""
        with db_manager.get_session() as session:
            # Check if user already exists
            existing_user = session.query(User).filter_by(
                email=google_user_info['email']
            ).first()
            
            if existing_user:
                # Update existing user info
                existing_user.name = google_user_info.get('name', existing_user.name)
                existing_user.updated_at = datetime.utcnow()
                session.commit()
                return existing_user
            else:
                # Create new user
                user = User(
                    id=self._generate_user_id(google_user_info['email']),
                    email=google_user_info['email'],
                    name=google_user_info.get('name', ''),
                    preferences={}
                )
                session.add(user)
                session.commit()
                return user
    
    def authenticate_user(self, google_user_info: Dict[str, Any]) -> Dict[str, str]:
        """Authenticate user and return tokens."""
        user = self.create_user(google_user_info)
        
        # Generate tokens
        access_token = self.token_manager.generate_access_token(user.id, user.email)
        refresh_token = self.token_manager.generate_refresh_token(user.id)
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        self.active_sessions[session_id] = {
            'user_id': user.id,
            'email': user.email,
            'created_at': datetime.now(timezone.utc),
            'last_activity': datetime.now(timezone.utc)
        }
        
        logger.info(f"User authenticated: {user.email}")
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'session_id': session_id,
            'user_id': user.id
        }
    
    def validate_session(self, session_id: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Validate user session and token."""
        try:
            # Validate token
            token_payload = self.token_manager.validate_token(access_token)
            
            # Check active session
            if session_id not in self.active_sessions:
                raise AuthenticationError("Session not found")
            
            session_data = self.active_sessions[session_id]
            
            # Verify session matches token
            if session_data['user_id'] != token_payload['user_id']:
                raise AuthenticationError("Session mismatch")
            
            # Update last activity
            session_data['last_activity'] = datetime.now(timezone.utc)
            
            return {
                'user_id': token_payload['user_id'],
                'email': token_payload['email'],
                'session_id': session_id
            }
            
        except AuthenticationError:
            # Clean up invalid session
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            raise
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh access token using refresh token."""
        try:
            payload = self.token_manager.validate_token(refresh_token)
            
            if payload.get('type') != 'refresh':
                raise AuthenticationError("Invalid refresh token")
            
            # Get user info
            with db_manager.get_session() as session:
                user = session.query(User).filter_by(id=payload['user_id']).first()
                if not user:
                    raise AuthenticationError("User not found")
            
            # Generate new access token
            new_access_token = self.token_manager.generate_access_token(user.id, user.email)
            
            return {
                'access_token': new_access_token,
                'user_id': user.id
            }
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise AuthenticationError("Token refresh failed")
    
    def logout_user(self, session_id: str):
        """Logout user and cleanup session."""
        if session_id in self.active_sessions:
            user_email = self.active_sessions[session_id].get('email')
            del self.active_sessions[session_id]
            logger.info(f"User logged out: {user_email}")
    
    def cleanup_expired_sessions(self):
        """Cleanup expired sessions (should be run periodically)."""
        current_time = datetime.now(timezone.utc)
        expired_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            last_activity = session_data['last_activity']
            if current_time - last_activity > timedelta(hours=24):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def _generate_user_id(self, email: str) -> str:
        """Generate consistent user ID from email."""
        return hashlib.sha256(email.encode()).hexdigest()[:16]

# Global auth system instance
auth_system = SecureAuthSystem()
