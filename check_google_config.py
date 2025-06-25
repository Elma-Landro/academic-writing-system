
#!/usr/bin/env python3
"""
Script de vérification de la configuration Google OAuth et APIs.
"""

import os
import requests
from core.secret_helper import get_secret

def check_google_oauth_config():
    """Vérifie la configuration OAuth Google."""
    print("=== Vérification Configuration Google OAuth ===")
    
    client_id = get_secret('GOOGLE_CLIENT_ID')
    client_secret = get_secret('GOOGLE_CLIENT_SECRET')
    
    if not client_id:
        print("❌ GOOGLE_CLIENT_ID manquant")
        return False
    else:
        print(f"✅ GOOGLE_CLIENT_ID configuré: {client_id[:20]}...")
    
    if not client_secret:
        print("❌ GOOGLE_CLIENT_SECRET manquant")
        return False
    else:
        print(f"✅ GOOGLE_CLIENT_SECRET configuré: {client_secret[:10]}...")
    
    return True

def check_redirect_uri():
    """Vérifie l'URI de redirection."""
    print("\n=== Vérification URI de Redirection ===")
    
    replit_domain = os.getenv('REPLIT_DEV_DOMAIN')
    if replit_domain:
        redirect_uri = f"https://{replit_domain}/oauth2callback"
        print(f"✅ URI de redirection Replit: {redirect_uri}")
        return redirect_uri
    else:
        print("⚠️ Variable REPLIT_DEV_DOMAIN non trouvée")
        return None

def check_google_apis():
    """Vérifie quels APIs Google sont disponibles."""
    print("\n=== APIs Google Recommandées ===")
    
    apis = [
        ("Google OAuth2 API", "https://www.googleapis.com/oauth2/v2/userinfo"),
        ("Google Drive API", "https://www.googleapis.com/drive/v3/about"),
        ("Google People API", "https://people.googleapis.com/v1/people/me")
    ]
    
    print("Pour votre application, vous devez activer ces APIs dans Google Console:")
    for name, url in apis:
        print(f"  • {name}")
    
    print("\nÉtapes pour activer les APIs:")
    print("1. Allez sur https://console.cloud.google.com/apis/library")
    print("2. Sélectionnez votre projet 'Academic writing system'")
    print("3. Recherchez et activez chaque API listée ci-dessus")

def main():
    """Fonction principale de vérification."""
    print("🔍 Vérification de la configuration Google\n")
    
    # Vérification OAuth
    oauth_ok = check_google_oauth_config()
    
    # Vérification URI
    redirect_uri = check_redirect_uri()
    
    # Information sur les APIs
    check_google_apis()
    
    print("\n=== Résumé ===")
    if oauth_ok and redirect_uri:
        print("✅ Configuration de base OK")
        print(f"📋 Assurez-vous que cette URI est dans Google Console: {redirect_uri}")
        print("📋 Vérifiez que les APIs nécessaires sont activées")
    else:
        print("❌ Configuration incomplète")
        print("Configurez GOOGLE_CLIENT_ID et GOOGLE_CLIENT_SECRET dans les secrets")

if __name__ == "__main__":
    main()
