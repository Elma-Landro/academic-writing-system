
import os

print("=== Test rapide OpenAI ===")

# 1. Vérifier la clé API
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ ERREUR: OPENAI_API_KEY non trouvée dans les secrets")
    exit(1)

print(f"✅ Clé API trouvée: {api_key[:10]}...{api_key[-4:]}")

# 2. Tester l'import OpenAI
try:
    from openai import OpenAI
    print("✅ Module OpenAI importé avec succès")
except ImportError as e:
    print(f"❌ ERREUR d'import OpenAI: {e}")
    exit(1)

# 3. Tester la connexion
try:
    client = OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Dis juste 'Test réussi'"}],
        max_tokens=10,
        temperature=0.1
    )
    
    result = response.choices[0].message.content
    print(f"🎉 SUCCÈS! Réponse OpenAI: {result}")
    print(f"Tokens utilisés: {response.usage.total_tokens}")
    
except Exception as e:
    print(f"❌ ERREUR OpenAI: {e}")
    
    # Diagnostics spécifiques
    error_str = str(e).lower()
    if "authentication" in error_str or "invalid" in error_str:
        print("🔍 Problème: Clé API invalide ou expirée")
    elif "quota" in error_str or "rate limit" in error_str:
        print("🔍 Problème: Quota dépassé ou limite de taux")
    elif "billing" in error_str:
        print("🔍 Problème: Compte sans crédits ou carte non configurée")
    else:
        print("🔍 Erreur inconnue")

print("\n=== Fin du test ===")
