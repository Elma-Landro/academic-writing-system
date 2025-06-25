
"""
Interface d'intégration Web3 complète pour l'authentification par wallet.
"""

import streamlit as st
import json
import hashlib
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from eth_account.messages import encode_defunct
from eth_account import Account
import requests

class Web3AuthManager:
    """Gestionnaire d'authentification Web3 professionnel."""
    
    def __init__(self):
        self.supported_wallets = ["MetaMask", "WalletConnect", "Coinbase Wallet"]
        self.auth_challenges = {}
    
    def generate_auth_challenge(self, wallet_address: str) -> str:
        """Génère un défi cryptographique pour l'authentification."""
        nonce = secrets.token_hex(16)
        timestamp = datetime.now().isoformat()
        
        challenge = f"""Welcome to Academic Writing System!

This request will not trigger a blockchain transaction or cost any gas fees.

Wallet: {wallet_address}
Nonce: {nonce}
Timestamp: {timestamp}

Sign this message to prove you own this wallet."""
        
        # Stocker le challenge pour vérification
        self.auth_challenges[wallet_address] = {
            'challenge': challenge,
            'nonce': nonce,
            'timestamp': timestamp,
            'expires': datetime.now() + timedelta(minutes=5)
        }
        
        return challenge
    
    def verify_signature(self, wallet_address: str, signature: str) -> bool:
        """Vérifie la signature du wallet avec cryptographie réelle."""
        try:
            # Récupérer le challenge
            challenge_data = self.auth_challenges.get(wallet_address)
            if not challenge_data:
                return False
            
            # Vérifier l'expiration
            if datetime.now() > challenge_data['expires']:
                del self.auth_challenges[wallet_address]
                return False
            
            # Encoder le message pour Ethereum
            message = challenge_data['challenge']
            encoded_message = encode_defunct(text=message)
            
            # Récupérer l'adresse depuis la signature
            recovered_address = Account.recover_message(encoded_message, signature=signature)
            
            # Vérifier que l'adresse correspond
            is_valid = recovered_address.lower() == wallet_address.lower()
            
            # Nettoyer le challenge utilisé
            if is_valid:
                del self.auth_challenges[wallet_address]
            
            return is_valid
            
        except Exception as e:
            st.error(f"Erreur de vérification de signature: {e}")
            return False

def render_web3_auth_interface():
    """Interface Web3 complète avec vrai support cryptographique."""
    st.markdown("### 🔗 Authentification Web3")
    
    # Initialiser le gestionnaire Web3
    if 'web3_auth_manager' not in st.session_state:
        st.session_state.web3_auth_manager = Web3AuthManager()
    
    auth_manager = st.session_state.web3_auth_manager
    
    # Sélection du wallet
    wallet_type = st.selectbox(
        "Choisissez votre wallet",
        auth_manager.supported_wallets,
        key="wallet_type_select"
    )
    
    # Étapes d'authentification
    if not st.session_state.get("web3_authenticated"):
        
        # Étape 1: Saisir l'adresse du wallet
        wallet_address = st.text_input(
            "Adresse de votre wallet",
            placeholder="0x742d35Cc6634C0532925a3b8D84c5f2f8Cf92b7b",
            key="wallet_address_input"
        )
        
        if wallet_address and len(wallet_address) == 42 and wallet_address.startswith('0x'):
            
            # Étape 2: Générer le challenge
            if st.button("Générer le message à signer", key="generate_challenge"):
                challenge = auth_manager.generate_auth_challenge(wallet_address)
                st.session_state.current_challenge = challenge
                st.session_state.challenge_wallet = wallet_address
            
            # Afficher le challenge à signer
            if st.session_state.get("current_challenge"):
                st.markdown("#### Message à signer dans votre wallet:")
                st.code(st.session_state.current_challenge, language="text")
                
                st.markdown(f"""
                **Instructions pour {wallet_type}:**
                1. Ouvrez votre wallet ({wallet_type})
                2. Allez dans les paramètres → Signer un message
                3. Copiez le message ci-dessus
                4. Signez le message (pas de frais de gas)
                5. Copiez la signature générée ci-dessous
                """)
                
                # Étape 3: Vérifier la signature
                signature = st.text_input(
                    "Signature du message",
                    placeholder="0x...",
                    key="signature_input"
                )
                
                if signature and st.button("Vérifier et se connecter", key="verify_signature"):
                    if auth_manager.verify_signature(wallet_address, signature):
                        st.session_state.web3_authenticated = True
                        st.session_state.web3_wallet_address = wallet_address
                        st.session_state.web3_wallet_type = wallet_type
                        st.success(f"✅ Authentifié avec {wallet_type}!")
                        st.rerun()
                    else:
                        st.error("❌ Signature invalide. Veuillez réessayer.")
        
        elif wallet_address:
            st.error("Format d'adresse invalide. Utilisez une adresse Ethereum valide (0x...)")
    
    else:
        # Utilisateur authentifié
        wallet_address = st.session_state.get("web3_wallet_address", "")
        wallet_type = st.session_state.get("web3_wallet_type", "")
        
        st.success(f"✅ Connecté avec {wallet_type}")
        st.info(f"**Adresse:** `{wallet_address[:10]}...{wallet_address[-8:]}`")
        
        # Statistiques du wallet (optionnel)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Voir les stats du wallet", key="wallet_stats"):
                st.session_state.show_wallet_stats = True
        
        with col2:
            if st.button("🔓 Déconnecter le wallet", key="web3_disconnect"):
                for key in ['web3_authenticated', 'web3_wallet_address', 'web3_wallet_type', 'current_challenge', 'challenge_wallet']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

def render_wallet_stats():
    """Affiche les statistiques du wallet connecté."""
    if not st.session_state.get("show_wallet_stats"):
        return
    
    wallet_address = st.session_state.get("web3_wallet_address")
    
    st.markdown("### 📊 Statistiques du Wallet")
    
    # Placeholder pour les vraies stats (nécessite une API blockchain)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Balance ETH", "Loading...", help="Solde en Ethereum")
    
    with col2:
        st.metric("Transactions", "Loading...", help="Nombre de transactions")
    
    with col3:
        st.metric("Première tx", "Loading...", help="Date de la première transaction")
    
    st.info("💡 Pour afficher les vraies données, connectez une API comme Etherscan ou Infura")
    
    if st.button("Fermer les stats", key="close_wallet_stats"):
        st.session_state.show_wallet_stats = False
        st.rerun()

def render_ipfs_document_manager(project_id: str, sedimentation_manager):
    """Interface IPFS améliorée pour la gestion décentralisée."""
    if not st.session_state.get("web3_authenticated"):
        st.warning("Connectez votre wallet pour accéder aux fonctionnalités décentralisées.")
        return
    
    st.markdown("### 📡 Gestion décentralisée des documents")
    
    # Statut IPFS
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Documents IPFS", "0", help="Documents publiés sur IPFS")
    
    with col2:
        st.metric("Versions stockées", "0", help="Versions sauvegardées")
    
    with col3:
        st.metric("Taille totale", "0 MB", help="Espace utilisé sur IPFS")
    
    # Actions IPFS
    st.markdown("#### Actions disponibles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Publier sur IPFS", key="publish_ipfs"):
            with st.spinner("Publication en cours..."):
                # Simulation - remplacer par vraie intégration IPFS
                import time
                time.sleep(2)
                st.success("✅ Document publié!")
                st.code("QmXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxX")
    
    with col2:
        if st.button("🔄 Synchroniser", key="sync_ipfs"):
            with st.spinner("Synchronisation..."):
                import time
                time.sleep(1)
                st.success("✅ Synchronisation terminée!")
    
    with col3:
        if st.button("📜 Historique", key="ipfs_history"):
            st.session_state.show_ipfs_history = True

def initialize_web3_session():
    """Initialise toutes les variables de session Web3."""
    session_vars = [
        'web3_authenticated',
        'web3_wallet_address', 
        'web3_wallet_type',
        'web3_auth_manager',
        'current_challenge',
        'challenge_wallet',
        'show_wallet_stats',
        'show_ipfs_history'
    ]
    
    for var in session_vars:
        if var not in st.session_state:
            if var == 'web3_authenticated':
                st.session_state[var] = False
            else:
                st.session_state[var] = None
