
"""
Complete configuration manager with environment variables and secrets management.
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any
import streamlit as st

logger = logging.getLogger(__name__)

@dataclass
class OpenAIConfig:
    """OpenAI API configuration."""
    api_key: str
    model: str = "gpt-4o-mini"
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 60

@dataclass
class GoogleOAuthConfig:
    """Google OAuth configuration."""
    client_id: str
    client_secret: str
    redirect_uri: str = "http://localhost:5000/oauth/callback"

@dataclass
class FileVerseConfig:
    """FileVerse API configuration."""
    api_key: str
    base_url: str = "https://api.fileverse.io/v1"
    timeout: int = 30

@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str = "sqlite:///data/academic_writing.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10

class ConfigurationManager:
    """Professional configuration manager with environment variable handling."""
    
    def __init__(self):
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from environment variables and Streamlit secrets."""
        self.openai_config = self._get_openai_config()
        self.google_oauth_config = self._get_google_oauth_config()
        self.fileverse_config = self._get_fileverse_config()
        self.database_config = self._get_database_config()
    
    def _get_openai_config(self) -> Optional[OpenAIConfig]:
        """Get OpenAI configuration."""
        api_key = self._get_secret('OPENAI_API_KEY', 'OPENAI_API_KEY')
        
        if not api_key:
            logger.warning("OpenAI API key not configured")
            return None
        
        return OpenAIConfig(
            api_key=api_key,
            model=self._get_secret('OPENAI_MODEL', 'OPENAI_MODEL', 'gpt-4o-mini'),
            max_tokens=int(self._get_secret('OPENAI_MAX_TOKENS', 'OPENAI_MAX_TOKENS', '4000')),
            temperature=float(self._get_secret('OPENAI_TEMPERATURE', 'OPENAI_TEMPERATURE', '0.7')),
            timeout=int(self._get_secret('OPENAI_TIMEOUT', 'OPENAI_TIMEOUT', '60'))
        )
    
    def _get_google_oauth_config(self) -> Optional[GoogleOAuthConfig]:
        """Get Google OAuth configuration."""
        client_id = self._get_secret('GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_ID')
        client_secret = self._get_secret('GOOGLE_CLIENT_SECRET', 'GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logger.warning("Google OAuth credentials not configured")
            return None
        
        return GoogleOAuthConfig(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=self._get_secret('GOOGLE_REDIRECT_URI', 'GOOGLE_REDIRECT_URI', 'http://0.0.0.0:5000/oauth/callback')
        )
    
    def _get_fileverse_config(self) -> Optional[FileVerseConfig]:
        """Get FileVerse configuration."""
        api_key = self._get_secret('FILEVERSE_API_KEY', 'FILEVERSE_API_KEY')
        
        if not api_key:
            logger.warning("FileVerse API key not configured")
            return None
        
        return FileVerseConfig(
            api_key=api_key,
            base_url=self._get_secret('FILEVERSE_BASE_URL', 'FILEVERSE_BASE_URL', 'https://api.fileverse.io/v1'),
            timeout=int(self._get_secret('FILEVERSE_TIMEOUT', 'FILEVERSE_TIMEOUT', '30'))
        )
    
    def _get_database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        return DatabaseConfig(
            url=self._get_secret('DATABASE_URL', 'DATABASE_URL', 'sqlite:///data/academic_writing.db'),
            echo=self._get_secret('DATABASE_ECHO', 'DATABASE_ECHO', 'false').lower() == 'true',
            pool_size=int(self._get_secret('DATABASE_POOL_SIZE', 'DATABASE_POOL_SIZE', '5')),
            max_overflow=int(self._get_secret('DATABASE_MAX_OVERFLOW', 'DATABASE_MAX_OVERFLOW', '10'))
        )
    
    def _get_secret(self, env_var: str, secrets_key: str, default: str = None) -> Optional[str]:
        """Get secret from environment variable or Streamlit secrets."""
        # Try environment variable first
        value = os.getenv(env_var)
        if value:
            return value
        
        # Try Streamlit secrets (direct key access)
        try:
            return str(st.secrets[secrets_key])
        except (KeyError, AttributeError):
            pass
        
        # Try nested secrets (for backward compatibility)
        try:
            keys = secrets_key.split('.')
            secrets = st.secrets
            for key in keys:
                secrets = secrets[key]
            return str(secrets)
        except (KeyError, AttributeError):
            pass
        
        # Return default
        return default
    
    def get_openai_config(self) -> OpenAIConfig:
        """Get OpenAI configuration or raise error."""
        if not self.openai_config:
            raise ValueError("OpenAI configuration is not available. Please set OPENAI_API_KEY.")
        return self.openai_config
    
    def get_google_oauth_config(self) -> GoogleOAuthConfig:
        """Get Google OAuth configuration or raise error."""
        if not self.google_oauth_config:
            raise ValueError("Google OAuth configuration is not available. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.")
        return self.google_oauth_config
    
    def get_fileverse_config(self) -> FileVerseConfig:
        """Get FileVerse configuration or raise error."""
        if not self.fileverse_config:
            raise ValueError("FileVerse configuration is not available. Please set FILEVERSE_API_KEY.")
        return self.fileverse_config
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        return self.database_config
    
    def is_openai_configured(self) -> bool:
        """Check if OpenAI is configured."""
        return self.openai_config is not None
    
    def is_google_oauth_configured(self) -> bool:
        """Check if Google OAuth is configured."""
        return self.google_oauth_config is not None
    
    def is_fileverse_configured(self) -> bool:
        """Check if FileVerse is configured."""
        return self.fileverse_config is not None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system configuration status."""
        return {
            'openai': self.is_openai_configured(),
            'google_oauth': self.is_google_oauth_configured(),
            'fileverse': self.is_fileverse_configured(),
            'database': True,  # Database always has defaults
            'environment': os.getenv('ENVIRONMENT', 'development')
        }

# Global configuration manager
config_manager = ConfigurationManager()
