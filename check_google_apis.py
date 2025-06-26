
#!/usr/bin/env python3
"""
Script pour vérifier que les APIs Google nécessaires sont activées.
"""

import os
import requests
import json
from core.secret_helper import get_secret

def test_google_api_endpoint(api_name, endpoint, access_token=None):
    """Teste si une API Google est accessible."""
    try:
        headers = {}
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        
        # Test simple de connectivité
        response = requests.get(endpoint, headers=headers, timeout=10)
        
        if response.status_code == 401:
            return "✅ API activée (authentification requise)"
        elif response.status_code == 403:
            return "❌ API non activée ou accès refusé"
        elif response.status_code == 200:
            return "✅ API activée et accessible"
        else:
            return f"⚠️ API réponse: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return f"❌ Erreur de connexion: {e}"

def check_oauth2_api():
    """Vérifie l'API OAuth2."""
    print("\n=== Test OAuth2 API ===")
    
    # Test endpoint public OAuth2
    result = test_google_api_endpoint(
        "OAuth2 API",
        "https://www.googleapis.com/oauth2/v2/userinfo"
    )
    print(f"OAuth2 API: {result}")
    
    # Vérification de la configuration
    client_id = get_secret('GOOGLE_CLIENT_ID')
    if client_id:
        print(f"✅ Client ID configuré: {client_id[:20]}...")
    else:
        print("❌ Client ID manquant")

def check_drive_api():
    """Vérifie l'API Google Drive."""
    print("\n=== Test Google Drive API ===")
    
    result = test_google_api_endpoint(
        "Drive API",
        "https://www.googleapis.com/drive/v3/about"
    )
    print(f"Drive API: {result}")

def check_people_api():
    """Vérifie l'API Google People."""
    print("\n=== Test Google People API ===")
    
    result = test_google_api_endpoint(
        "People API",
        "https://people.googleapis.com/v1/people/me"
    )
    print(f"People API: {result}")

def check_sheets_api():
    """Vérifie l'API Google Sheets (optionnelle)."""
    print("\n=== Test Google Sheets API ===")
    
    result = test_google_api_endpoint(
        "Sheets API",
        "https://sheets.googleapis.com/v4/spreadsheets"
    )
    print(f"Sheets API: {result}")

def provide_activation_instructions():
    """Fournit les instructions pour activer les APIs."""
    print("\n=== Instructions d'activation des APIs ===")
    print("1. Allez sur: https://console.cloud.google.com/apis/library")
    print("2. Sélectionnez votre projet")
    print("3. Recherchez et activez ces APIs:")
    print("   • Google+ API (pour OAuth2)")
    print("   • Google Drive API")
    print("   • People API")
    print("   • Google Sheets API (optionnel)")
    
    print("\n=== URLs directes ===")
    apis = [
        ("Google+ API", "https://console.cloud.google.com/apis/library/plus.googleapis.com"),
        ("Drive API", "https://console.cloud.google.com/apis/library/drive.googleapis.com"),
        ("People API", "https://console.cloud.google.com/apis/library/people.googleapis.com"),
        ("Sheets API", "https://console.cloud.google.com/apis/library/sheets.googleapis.com")
    ]
    
    for name, url in apis:
        print(f"   • {name}: {url}")

def main():
    """Fonction principale."""
    print("🔍 Vérification des APIs Google\n")
    
    # Tests des APIs
    check_oauth2_api()
    check_drive_api()
    check_people_api()
    check_sheets_api()
    
    # Instructions
    provide_activation_instructions()
    
    print("\n=== Résumé ===")
    print("Si vous voyez '❌ API non activée', suivez les instructions ci-dessus.")
    print("Les APIs avec '✅ API activée' sont correctement configurées.")

if __name__ == "__main__":
    main()
