
"""
Secure configuration management with environment validation and secret handling.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from cryptography.fernet import Fernet
import base64
import json

@dataclass
class DatabaseConfig:
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

@dataclass
class AIConfig:
    openai_api_key: str
    venice_api_key: Optional[str] = None
    default_model: str = "gpt-4o"
    max_tokens: int = 4000
    temperature: float = 0.7

@dataclass
class FileVerseConfig:
    api_key: str
    base_url: str = "https://api.fileverse.io"
    timeout: int = 30

@dataclass
class AuthConfig:
    google_client_id: str
    google_client_secret: str
    session_secret_key: str
    token_expiry_hours: int = 24

class SecureConfigManager:
    """Secure configuration manager with encryption for sensitive data."""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive configuration."""
        key_file = "data/.config_key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            os.makedirs("data", exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a sensitive configuration value."""
        return self.cipher.encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a sensitive configuration value."""
        return self.cipher.decrypt(encrypted_value.encode()).decode()
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration with validation."""
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        return DatabaseConfig(
            url=database_url,
            pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20')),
            echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
        )
    
    def get_ai_config(self) -> AIConfig:
        """Get AI configuration with API key validation."""
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        return AIConfig(
            openai_api_key=openai_key,
            venice_api_key=os.getenv('VENICE_API_KEY'),
            default_model=os.getenv('AI_DEFAULT_MODEL', 'gpt-4o'),
            max_tokens=int(os.getenv('AI_MAX_TOKENS', '4000')),
            temperature=float(os.getenv('AI_TEMPERATURE', '0.7'))
        )
    
    def get_fileverse_config(self) -> FileVerseConfig:
        """Get FileVerse configuration."""
        api_key = os.getenv('FILEVERSE_API_KEY')
        if not api_key:
            raise ValueError("FILEVERSE_API_KEY environment variable is required")
        
        return FileVerseConfig(
            api_key=api_key,
            base_url=os.getenv('FILEVERSE_BASE_URL', 'https://api.fileverse.io'),
            timeout=int(os.getenv('FILEVERSE_TIMEOUT', '30'))
        )
    
    def get_auth_config(self) -> AuthConfig:
        """Get authentication configuration."""
        google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        session_secret = os.getenv('SESSION_SECRET_KEY')
        
        if not all([google_client_id, google_client_secret, session_secret]):
            raise ValueError("Authentication environment variables are required")
        
        return AuthConfig(
            google_client_id=google_client_id,
            google_client_secret=google_client_secret,
            session_secret_key=session_secret,
            token_expiry_hours=int(os.getenv('TOKEN_EXPIRY_HOURS', '24'))
        )
    
    def validate_all_configs(self) -> Dict[str, bool]:
        """Validate all configuration sections."""
        results = {}
        
        try:
            self.get_database_config()
            results['database'] = True
        except Exception:
            results['database'] = False
        
        try:
            self.get_ai_config()
            results['ai'] = True
        except Exception:
            results['ai'] = False
        
        try:
            self.get_fileverse_config()
            results['fileverse'] = True
        except Exception:
            results['fileverse'] = False
        
        try:
            self.get_auth_config()
            results['auth'] = True
        except Exception:
            results['auth'] = False
        
        return results

# Global configuration manager
config_manager = SecureConfigManager()
