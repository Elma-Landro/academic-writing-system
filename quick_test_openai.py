import os

print("=== Test OpenAI PROPRE ===")

# 1. Vérifier la clé API
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ ERREUR: Clé API non trouvée")
    exit(1)

print(f"✅ Clé API: {api_key[:10]}...{api_key[-4:]}")

# 2. Test avec la méthode la plus simple possible
try:
    from openai import OpenAI
    print("✅ Import réussi")

    # Méthode la plus basique : utiliser la variable d'environnement directement
    client = OpenAI(api_key=api_key)

    print("✅ Client créé")

    # Test minimal
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Dis 'OK'"}],
        max_tokens=5
    )

    print(f"🎉 SUCCÈS! Réponse: {response.choices[0].message.content}")
    print(f"✅ Tokens: {response.usage.total_tokens}")

except Exception as e:
    print(f"❌ ERREUR: {e}")
    print(f"Type d'erreur: {type(e).__name__}")

print("\n=== Fin ===")