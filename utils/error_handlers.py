
"""
Centralized error handling and logging system.
"""

import logging
import traceback
import streamlit as st
from typing import Any, Callable, Dict, Optional
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling."""
    
    @staticmethod
    def handle_api_error(error: Exception, context: str) -> Dict[str, Any]:
        """Handle API-related errors."""
        logger.error(f"API Error in {context}: {str(error)}")
        logger.error(traceback.format_exc())
        
        # Don't expose internal errors to users
        return {
            "success": False,
            "error": "Service temporarily unavailable",
            "code": "API_ERROR"
        }
    
    @staticmethod
    def handle_validation_error(error: Exception, context: str) -> Dict[str, Any]:
        """Handle validation errors."""
        logger.warning(f"Validation Error in {context}: {str(error)}")
        
        return {
            "success": False,
            "error": str(error),
            "code": "VALIDATION_ERROR"
        }
    
    @staticmethod
    def handle_auth_error(error: Exception, context: str) -> Dict[str, Any]:
        """Handle authentication errors."""
        logger.error(f"Auth Error in {context}: {str(error)}")
        
        # Clear potentially corrupted session
        if 'google_credentials' in st.session_state:
            del st.session_state.google_credentials
        if 'user_info' in st.session_state:
            del st.session_state.user_info
        
        return {
            "success": False,
            "error": "Authentication failed. Please login again.",
            "code": "AUTH_ERROR"
        }

def safe_execute(error_type: str = "general"):
    """Decorator for safe function execution."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = f"{func.__module__}.{func.__name__}"
                
                if error_type == "api":
                    return ErrorHandler.handle_api_error(e, context)
                elif error_type == "validation":
                    return ErrorHandler.handle_validation_error(e, context)
                elif error_type == "auth":
                    return ErrorHandler.handle_auth_error(e, context)
                else:
                    logger.error(f"Unexpected error in {context}: {str(e)}")
                    logger.error(traceback.format_exc())
                    return {
                        "success": False,
                        "error": "An unexpected error occurred",
                        "code": "INTERNAL_ERROR"
                    }
        return wrapper
    return decorator
