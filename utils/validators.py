
"""
Input validation and sanitization utilities.
"""

import re
import html
from typing import Any, Dict, List, Optional

class ValidationError(Exception):
    """Custom validation error."""
    pass

class InputValidator:
    """Secure input validation."""
    
    @staticmethod
    def validate_project_title(title: str) -> str:
        """Validate and sanitize project title."""
        if not title or not title.strip():
            raise ValidationError("Title cannot be empty")
        
        title = html.escape(title.strip())
        
        if len(title) > 200:
            raise ValidationError("Title too long (max 200 characters)")
        
        # Only allow alphanumeric, spaces, and basic punctuation
        if not re.match(r'^[a-zA-Z0-9\s\.\-_,;:!?\'"()]+$', title):
            raise ValidationError("Title contains invalid characters")
        
        return title
    
    @staticmethod
    def validate_project_id(project_id: str) -> str:
        """Validate project ID format."""
        if not project_id:
            raise ValidationError("Project ID cannot be empty")
        
        # Must be UUID format
        if not re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', project_id):
            raise ValidationError("Invalid project ID format")
        
        return project_id
    
    @staticmethod
    def sanitize_content(content: str) -> str:
        """Sanitize user content."""
        if not isinstance(content, str):
            return ""
        
        # Basic HTML escaping
        content = html.escape(content)
        
        # Limit size to prevent DoS
        if len(content) > 100000:  # 100KB limit
            content = content[:100000]
        
        return content
