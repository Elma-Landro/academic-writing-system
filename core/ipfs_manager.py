
"""
Gestionnaire IPFS pour l'intégration décentralisée de documents académiques.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
import os

class IPFSManager:
    """Gestionnaire d'intégration IPFS pour documents académiques."""
    
    def __init__(self):
        """Initialise le gestionnaire IPFS."""
        self.pinata_api_key = os.environ.get("PINATA_API_KEY")
        self.pinata_secret = os.environ.get("PINATA_SECRET")
        self.ipfs_gateway = "https://gateway.pinata.cloud/ipfs/"
        
    def pin_document_to_ipfs(self, project_id: str, document_data: Dict[str, Any]) -> Optional[str]:
        """
        Épingle un document sur IPFS via Pinata.
        
        Args:
            project_id: ID du projet
            document_data: Données du document à épingler
            
        Returns:
            Hash IPFS du document ou None si échec
        """
        if not self.pinata_api_key or not self.pinata_secret:
            return None
            
        # Préparer les métadonnées
        metadata = {
            "name": f"academic_doc_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "keyvalues": {
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "type": "academic_document",
                "version": document_data.get("version", "1.0")
            }
        }
        
        # Données à épingler
        pin_data = {
            "pinataContent": document_data,
            "pinataMetadata": metadata
        }
        
        headers = {
            "pinata_api_key": self.pinata_api_key,
            "pinata_secret_api_key": self.pinata_secret,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                "https://api.pinata.cloud/pinning/pinJSONToIPFS",
                json=pin_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("IpfsHash")
            
            return None
            
        except Exception as e:
            print(f"Erreur lors de l'épinglage IPFS: {e}")
            return None
    
    def retrieve_document_from_ipfs(self, ipfs_hash: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un document depuis IPFS.
        
        Args:
            ipfs_hash: Hash IPFS du document
            
        Returns:
            Données du document ou None si échec
        """
        try:
            response = requests.get(
                f"{self.ipfs_gateway}{ipfs_hash}",
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            print(f"Erreur lors de la récupération IPFS: {e}")
            return None
    
    def create_document_version_chain(self, project_id: str, 
                                    versions: List[Dict[str, Any]]) -> List[str]:
        """
        Crée une chaîne de versions sur IPFS.
        
        Args:
            project_id: ID du projet
            versions: Liste des versions du document
            
        Returns:
            Liste des hashes IPFS des versions
        """
        version_hashes = []
        
        for i, version in enumerate(versions):
            # Ajouter la référence à la version précédente
            if version_hashes:
                version["previous_version"] = version_hashes[-1]
            
            version["version_number"] = i + 1
            version["chain_position"] = i
            
            # Épingler cette version
            ipfs_hash = self.pin_document_to_ipfs(project_id, version)
            if ipfs_hash:
                version_hashes.append(ipfs_hash)
        
        return version_hashes
    
    def get_document_history(self, latest_hash: str) -> List[Dict[str, Any]]:
        """
        Récupère l'historique complet d'un document via sa chaîne IPFS.
        
        Args:
            latest_hash: Hash de la version la plus récente
            
        Returns:
            Liste des versions dans l'ordre chronologique
        """
        history = []
        current_hash = latest_hash
        
        while current_hash:
            document = self.retrieve_document_from_ipfs(current_hash)
            if not document:
                break
                
            history.append({
                "hash": current_hash,
                "document": document,
                "timestamp": document.get("timestamp"),
                "version": document.get("version_number", 1)
            })
            
            # Passer à la version précédente
            current_hash = document.get("previous_version")
        
        # Retourner dans l'ordre chronologique
        return list(reversed(history))

class Web3AuthManager:
    """Gestionnaire d'authentification Web3 pour les wallets."""
    
    def __init__(self):
        """Initialise le gestionnaire d'authentification Web3."""
        self.supported_wallets = ["metamask", "walletconnect", "coinbase"]
        
    def generate_auth_challenge(self, wallet_address: str) -> str:
        """
        Génère un défi d'authentification pour un wallet.
        
        Args:
            wallet_address: Adresse du wallet
            
        Returns:
            Défi à signer
        """
        timestamp = datetime.now().isoformat()
        nonce = hashlib.sha256(f"{wallet_address}{timestamp}".encode()).hexdigest()[:16]
        
        challenge = f"""
        Authentification sur le Système de Rédaction Académique
        
        Adresse: {wallet_address}
        Horodatage: {timestamp}
        Nonce: {nonce}
        
        Signez ce message pour prouver la propriété de votre wallet.
        """
        
        return challenge.strip()
    
    def verify_signature(self, wallet_address: str, message: str, signature: str) -> bool:
        """
        Vérifie une signature de wallet.
        
        Args:
            wallet_address: Adresse du wallet
            message: Message original signé
            signature: Signature à vérifier
            
        Returns:
            True si la signature est valide
        """
        # Implémentation simplifiée - en production, utiliser une librairie crypto
        # comme eth_account pour vérifier les signatures Ethereum
        try:
            # Placeholder pour la vérification réelle
            # En production: utiliser eth_account.recover_message
            return len(signature) > 100 and wallet_address.startswith("0x")
        except Exception:
            return False

class DecentralizedContextManager:
    """Gestionnaire de contexte décentralisé pour l'IA."""
    
    def __init__(self, ipfs_manager: IPFSManager):
        """Initialise le gestionnaire de contexte décentralisé."""
        self.ipfs_manager = ipfs_manager
        
    def store_ai_context(self, project_id: str, context_data: Dict[str, Any]) -> Optional[str]:
        """
        Stocke un contexte d'IA sur IPFS.
        
        Args:
            project_id: ID du projet
            context_data: Données du contexte IA
            
        Returns:
            Hash IPFS du contexte stocké
        """
        context_package = {
            "project_id": project_id,
            "context_type": "ai_interaction",
            "timestamp": datetime.now().isoformat(),
            "data": context_data,
            "schema_version": "1.0"
        }
        
        return self.ipfs_manager.pin_document_to_ipfs(project_id, context_package)
    
    def retrieve_ai_context(self, context_hash: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un contexte d'IA depuis IPFS.
        
        Args:
            context_hash: Hash IPFS du contexte
            
        Returns:
            Données du contexte ou None
        """
        context_package = self.ipfs_manager.retrieve_document_from_ipfs(context_hash)
        
        if context_package and context_package.get("context_type") == "ai_interaction":
            return context_package.get("data")
        
        return None
    
    def link_contexts(self, project_id: str, context_hashes: List[str]) -> Optional[str]:
        """
        Crée un lien entre plusieurs contextes d'IA.
        
        Args:
            project_id: ID du projet
            context_hashes: Liste des hashes de contexte à lier
            
        Returns:
            Hash du lien créé
        """
        link_data = {
            "project_id": project_id,
            "context_type": "ai_context_chain",
            "linked_contexts": context_hashes,
            "timestamp": datetime.now().isoformat(),
            "chain_length": len(context_hashes)
        }
        
        return self.ipfs_manager.pin_document_to_ipfs(project_id, link_data)
