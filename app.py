
import streamlit as st
import os
import sys
from datetime import datetime
import uuid

import auth_manager

# Obligatoire : doit être en premier
st.set_page_config(
    page_title="Système de Rédaction Académique",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation minimale
if "page" not in st.session_state:
    st.session_state.page = "home"
if "current_project_id" not in st.session_state:
    st.session_state.current_project_id = None

# Traitement du retour OAuth (paramètre ?code=...)
if "code" in st.query_params:
    try:
        import auth_manager
        code = st.query_params["code"][0]
        st.write("✅ Code OAuth reçu :", code)

        flow = auth_manager.create_oauth_flow()
        st.write("✅ Flux OAuth créé avec succès")

        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Vérification du token
        if not credentials or not credentials.token:
            st.error("❌ Aucun token OAuth récupéré.")
            st.stop()

        st.write("✅ Token récupéré :", credentials.token)

        # Stockage dans la session
        st.session_state.google_credentials = {
            'token': credentials.token,
            'refresh_token': getattr(credentials, 'refresh_token', None),
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
        }

        user_info = auth_manager.get_user_info(credentials)
        st.session_state.user_info = user_info
        st.write("✅ Utilisateur connecté :", user_info.get("email", "inconnu"))

        st.session_state.page = "home"
        st.experimental_set_query_params()
        st.rerun()

    except Exception as e:
        st.error(f"❌ Erreur OAuth2 : {str(e)}")
        st.write("❌ Exception complète :", e)

# Interface minimale
st.title("Système de Rédaction Académique — Accueil")

if auth_manager.is_authenticated():
    st.success(f"Connecté : {st.session_state.user_info.get('email', 'utilisateur inconnu')}")
    st.write("⚙️ Interface académique disponible...")
else:
    st.warning("Non connecté")
    if st.button("Se connecter avec Google"):
        flow = auth_manager.create_oauth_flow()
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.markdown(f"[Cliquez ici pour vous connecter]({auth_url})")
