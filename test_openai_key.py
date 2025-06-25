
import os
import streamlit as st
from openai import OpenAI

def test_openai_connection():
    """Test la connexion à l'API OpenAI"""
    
    st.title("🔑 Test de la clé API OpenAI")
    
    # Récupérer la clé API
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        st.error("❌ Clé API OpenAI non trouvée dans les secrets")
        st.info("Ajoutez OPENAI_API_KEY dans vos secrets Replit")
        return
    
    st.success(f"✅ Clé API trouvée: {api_key[:10]}...{api_key[-4:]}")
    
    if st.button("🧪 Tester la connexion OpenAI"):
        try:
            with st.spinner("Test en cours..."):
                client = OpenAI(api_key=api_key)
                
                # Test simple avec un prompt court
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Bonjour! Réponds juste 'Test réussi' si tu me reçois."}],
                    max_tokens=50,
                    temperature=0.1
                )
                
                result = response.choices[0].message.content
                
                st.success("🎉 Connexion OpenAI réussie!")
                st.info(f"Réponse: {result}")
                st.write(f"Modèle utilisé: {response.model}")
                st.write(f"Tokens utilisés: {response.usage.total_tokens}")
                
        except Exception as e:
            st.error(f"❌ Erreur de connexion: {str(e)}")
            
            # Diagnostics détaillés
            if "authentication" in str(e).lower():
                st.warning("🔍 Problème d'authentification - vérifiez votre clé API")
            elif "quota" in str(e).lower():
                st.warning("🔍 Quota dépassé - vérifiez votre compte OpenAI")
            elif "billing" in str(e).lower():
                st.warning("🔍 Problème de facturation - ajoutez des crédits à votre compte")
            else:
                st.warning("🔍 Erreur inconnue - contactez le support OpenAI")

if __name__ == "__main__":
    test_openai_connection()
