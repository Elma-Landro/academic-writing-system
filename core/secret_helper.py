
"""
Helper pour la gestion sécurisée des secrets dans Replit.
"""

import os
import streamlit as st
from typing import Optional

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Obtient une valeur de secret de façon sécurisée.
    
    Args:
        key: Nom de la clé du secret
        default: Valeur par défaut si le secret n'existe pas
    
    Returns:
        Valeur du secret ou valeur par défaut
    """
    # Essayer d'abord les variables d'environnement
    value = os.getenv(key)
    if value:
        return value
    
    # Essayer ensuite les secrets Streamlit
    try:
        return str(st.secrets[key])
    except (KeyError, AttributeError):
        pass
    
    # Retourner la valeur par défaut
    return default

def check_required_secrets() -> dict:
    """
    Vérifie que tous les secrets requis sont configurés.
    
    Returns:
        Dictionnaire avec le statut de chaque secret
    """
    required_secrets = [
        "OPENAI_API_KEY",
        "GOOGLE_CLIENT_ID", 
        "GOOGLE_CLIENT_SECRET"
    ]
    
    optional_secrets = [
        "FILEVERSE_API_KEY"
    ]
    
    status = {}
    
    for secret in required_secrets:
        status[secret] = {
            "configured": get_secret(secret) is not None,
            "required": True
        }
    
    for secret in optional_secrets:
        status[secret] = {
            "configured": get_secret(secret) is not None,
            "required": False
        }
    
    return status
