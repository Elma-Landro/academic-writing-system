
"""
Interface d'intégration Web3 pour l'authentification par wallet.
"""

import streamlit as st
import json
from typing import Dict, Any, Optional

def render_web3_auth_interface():
    """Affiche l'interface d'authentification Web3."""
    st.markdown("### 🔗 Authentification Web3")
    
    # Sélection du type de wallet
    wallet_type = st.selectbox(
        "Choisissez votre wallet",
        ["MetaMask", "WalletConnect", "Coinbase Wallet"],
        key="wallet_type_select"
    )
    
    # Simulation d'authentification (en production, intégrer avec Web3.js)
    if st.button(f"Se connecter avec {wallet_type}", key="web3_connect"):
        # Simulation - en production, déclencher la connexion réelle
        st.session_state.web3_wallet_address = "0x742d35Cc6634C0532925a3b8D84c5f2f8Cf92b7b"
        st.session_state.web3_authenticated = True
        st.success(f"Connecté avec {wallet_type}!")
        st.rerun()
    
    # Affichage du statut
    if st.session_state.get("web3_authenticated"):
        wallet_address = st.session_state.get("web3_wallet_address", "")
        st.success(f"✅ Wallet connecté: {wallet_address[:10]}...{wallet_address[-8:]}")
        
        if st.button("Déconnecter le wallet", key="web3_disconnect"):
            st.session_state.web3_authenticated = False
            st.session_state.web3_wallet_address = None
            st.rerun()

def render_ipfs_document_manager(project_id: str, sedimentation_manager):
    """Affiche l'interface de gestion des documents IPFS."""
    st.markdown("### 📡 Gestion décentralisée des documents")
    
    # Statut IPFS
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Documents sur IPFS", "0")  # À connecter avec les vraies données
    
    with col2:
        st.metric("Versions stockées", "0")  # À connecter avec les vraies données
    
    # Actions IPFS
    st.markdown("#### Actions disponibles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Publier sur IPFS", key="publish_ipfs"):
            # Simulation de publication
            with st.spinner("Publication en cours..."):
                # En production: intégrer avec IPFSManager
                st.success("Document publié sur IPFS!")
                st.info("Hash: QmXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx")
    
    with col2:
        if st.button("🔄 Synchroniser", key="sync_ipfs"):
            with st.spinner("Synchronisation..."):
                st.success("Synchronisation terminée!")
    
    with col3:
        if st.button("📜 Historique IPFS", key="ipfs_history"):
            st.session_state.show_ipfs_history = True

def render_ipfs_history_viewer():
    """Affiche l'historique des versions IPFS."""
    if not st.session_state.get("show_ipfs_history"):
        return
    
    st.markdown("### 📜 Historique des versions IPFS")
    
    # Simulation de données d'historique
    history_data = [
        {
            "version": "v1.2.1",
            "hash": "QmXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxX1",
            "timestamp": "2024-01-15 14:30:00",
            "changes": "Révision finale",
            "size": "45.2 KB"
        },
        {
            "version": "v1.2.0",
            "hash": "QmXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxX2",
            "timestamp": "2024-01-14 16:45:00",
            "changes": "Ajout de nouvelles sections",
            "size": "42.1 KB"
        }
    ]
    
    for i, version in enumerate(history_data):
        with st.expander(f"Version {version['version']} - {version['timestamp']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Hash IPFS:** `{version['hash']}`")
                st.write(f"**Taille:** {version['size']}")
            
            with col2:
                st.write(f"**Modifications:** {version['changes']}")
                if st.button(f"Restaurer cette version", key=f"restore_{i}"):
                    st.info("Fonctionnalité de restauration à implémenter")
    
    if st.button("Fermer l'historique", key="close_ipfs_history"):
        st.session_state.show_ipfs_history = False
        st.rerun()

def initialize_web3_session():
    """Initialise les variables de session Web3."""
    if "web3_authenticated" not in st.session_state:
        st.session_state.web3_authenticated = False
    if "web3_wallet_address" not in st.session_state:
        st.session_state.web3_wallet_address = None
    if "show_ipfs_history" not in st.session_state:
        st.session_state.show_ipfs_history = False
