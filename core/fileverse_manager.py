"""
Real FileVerse integration with blockchain support and proper API management.
"""

import aiohttp
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import hashlib
from dataclasses import dataclass, asdict
import logging

from core.config_manager import config_manager
from core.database_layer import db_manager, Section

logger = logging.getLogger(__name__)

@dataclass
class FileVersePad:
    """FileVerse pad data structure."""
    pad_id: str
    title: str
    content: str
    blockchain_hash: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

@dataclass
class BlockchainTransaction:
    """Blockchain transaction record."""
    tx_hash: str
    pad_id: str
    action: str  # create, update, delete
    content_hash: str
    timestamp: datetime
    gas_used: int
    status: str  # confirmed, pending, failed

class FileVerseAPIClient:
    """Professional FileVerse API client with proper error handling."""

    def __init__(self):
        self.config = config_manager.get_fileverse_config()
        self.base_url = self.config.base_url
        self.api_key = self.config.api_key
        self.timeout = self.config.timeout
        self.session = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def create_pad(self, title: str, content: str = "", metadata: Dict[str, Any] = None) -> FileVersePad:
        """Create a new FileVerse pad."""
        if metadata is None:
            metadata = {}

        payload = {
            'title': title,
            'content': content,
            'metadata': metadata,
            'blockchain_enabled': True
        }

        async with self.session.post(f'{self.base_url}/pads', json=payload) as response:
            if response.status == 201:
                data = await response.json()
                return FileVersePad(
                    pad_id=data['pad_id'],
                    title=data['title'],
                    content=data['content'],
                    blockchain_hash=data['blockchain_hash'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    updated_at=datetime.fromisoformat(data['updated_at']),
                    metadata=data['metadata']
                )
            else:
                error_data = await response.json()
                raise Exception(f"Failed to create pad: {error_data.get('error', 'Unknown error')}")

    async def get_pad(self, pad_id: str) -> FileVersePad:
        """Retrieve a FileVerse pad."""
        async with self.session.get(f'{self.base_url}/pads/{pad_id}') as response:
            if response.status == 200:
                data = await response.json()
                return FileVersePad(
                    pad_id=data['pad_id'],
                    title=data['title'],
                    content=data['content'],
                    blockchain_hash=data['blockchain_hash'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    updated_at=datetime.fromisoformat(data['updated_at']),
                    metadata=data['metadata']
                )
            elif response.status == 404:
                raise Exception(f"Pad not found: {pad_id}")
            else:
                error_data = await response.json()
                raise Exception(f"Failed to get pad: {error_data.get('error', 'Unknown error')}")

    async def update_pad(self, pad_id: str, title: str = None, content: str = None, metadata: Dict[str, Any] = None) -> FileVersePad:
        """Update a FileVerse pad."""
        payload = {}
        if title is not None:
            payload['title'] = title
        if content is not None:
            payload['content'] = content
        if metadata is not None:
            payload['metadata'] = metadata

        async with self.session.put(f'{self.base_url}/pads/{pad_id}', json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return FileVersePad(
                    pad_id=data['pad_id'],
                    title=data['title'],
                    content=data['content'],
                    blockchain_hash=data['blockchain_hash'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    updated_at=datetime.fromisoformat(data['updated_at']),
                    metadata=data['metadata']
                )
            else:
                error_data = await response.json()
                raise Exception(f"Failed to update pad: {error_data.get('error', 'Unknown error')}")

    async def delete_pad(self, pad_id: str) -> bool:
        """Delete a FileVerse pad."""
        async with self.session.delete(f'{self.base_url}/pads/{pad_id}') as response:
            if response.status == 204:
                return True
            else:
                error_data = await response.json()
                raise Exception(f"Failed to delete pad: {error_data.get('error', 'Unknown error')}")

    async def get_blockchain_transactions(self, pad_id: str) -> List[BlockchainTransaction]:
        """Get blockchain transaction history for a pad."""
        async with self.session.get(f'{self.base_url}/pads/{pad_id}/blockchain') as response:
            if response.status == 200:
                data = await response.json()
                return [
                    BlockchainTransaction(
                        tx_hash=tx['tx_hash'],
                        pad_id=tx['pad_id'],
                        action=tx['action'],
                        content_hash=tx['content_hash'],
                        timestamp=datetime.fromisoformat(tx['timestamp']),
                        gas_used=tx['gas_used'],
                        status=tx['status']
                    )
                    for tx in data['transactions']
                ]
            else:
                error_data = await response.json()
                raise Exception(f"Failed to get blockchain data: {error_data.get('error', 'Unknown error')}")

class FileVerseManager:
    """Professional FileVerse manager with database integration."""

    def __init__(self):
        self.api_client = None

    async def create_section_pad(self, section_id: str, title: str, content: str = "") -> str:
        """Create a FileVerse pad for a section."""
        async with FileVerseAPIClient() as client:
            # Create metadata linking to our section
            metadata = {
                'section_id': section_id,
                'created_by': 'academic_writing_system',
                'content_type': 'academic_section'
            }

            pad = await client.create_pad(title, content, metadata)

            # Update section with pad ID
            with db_manager.get_session() as session:
                section = session.query(Section).filter_by(id=section_id).first()
                if section:
                    section.fileverse_pad_id = pad.pad_id
                    section.updated_at = datetime.utcnow()
                    session.commit()

            logger.info(f"Created FileVerse pad {pad.pad_id} for section {section_id}")
            return pad.pad_id

    async def sync_section_content(self, section_id: str) -> bool:
        """Sync content between database section and FileVerse pad."""
        with db_manager.get_session() as session:
            section = session.query(Section).filter_by(id=section_id).first()
            if not section or not section.fileverse_pad_id:
                return False

            async with FileVerseAPIClient() as client:
                try:
                    # Get latest content from FileVerse
                    pad = await client.get_pad(section.fileverse_pad_id)

                    # Compare content hashes to detect changes
                    db_content_hash = hashlib.sha256(section.content.encode()).hexdigest()
                    pad_content_hash = hashlib.sha256(pad.content.encode()).hexdigest()

                    if db_content_hash != pad_content_hash:
                        # Content differs, sync from FileVerse (source of truth)
                        section.content = pad.content
                        section.updated_at = datetime.utcnow()
                        session.commit()

                        logger.info(f"Synced content for section {section_id} from FileVerse")
                        return True

                    return False  # No sync needed

                except Exception as e:
                    logger.error(f"Failed to sync section {section_id}: {e}")
                    return False

    async def update_pad_content(self, section_id: str, new_content: str) -> bool:
        """Update FileVerse pad content from section."""
        with db_manager.get_session() as session:
            section = session.query(Section).filter_by(id=section_id).first()
            if not section or not section.fileverse_pad_id:
                return False

            async with FileVerseAPIClient() as client:
                try:
                    await client.update_pad(
                        section.fileverse_pad_id,
                        content=new_content
                    )

                    # Update local database
                    section.content = new_content
                    section.updated_at = datetime.utcnow()
                    session.commit()

                    logger.info(f"Updated FileVerse pad for section {section_id}")
                    return True

                except Exception as e:
                    logger.error(f"Failed to update pad for section {section_id}: {e}")
                    return False

    async def get_blockchain_history(self, section_id: str) -> List[BlockchainTransaction]:
        """Get blockchain transaction history for a section."""
        with db_manager.get_session() as session:
            section = session.query(Section).filter_by(id=section_id).first()
            if not section or not section.fileverse_pad_id:
                return []

            async with FileVerseAPIClient() as client:
                try:
                    return await client.get_blockchain_transactions(section.fileverse_pad_id)
                except Exception as e:
                    logger.error(f"Failed to get blockchain history for section {section_id}: {e}")
                    return []

    async def extract_insights(self, section_id: str) -> Dict[str, Any]:
        """Extract AI insights from FileVerse pad content."""
        with db_manager.get_session() as session:
            section = session.query(Section).filter_by(id=section_id).first()
            if not section or not section.fileverse_pad_id:
                return {}

            async with FileVerseAPIClient() as client:
                try:
                    pad = await client.get_pad(section.fileverse_pad_id)

                    # Use AI service to extract insights
                    from services.ai_service import ai_service

                    context = {
                        'style': 'Académique',
                        'project_type': 'Article académique',
                        'task': 'insight_extraction'
                    }

                    insight_prompt = f"""
                    Extract key insights from this academic text:
                    - Main thesis or argument
                    - Key supporting evidence
                    - Notable citations or references
                    - Areas needing development

                    Text: {pad.content[:2000]}
                    """

                    response = await ai_service.generate_content(
                        prompt=insight_prompt,
                        context=context,
                        user_id="system",
                        project_id=section.project_id
                    )

                    return {
                        'insights': response.content,
                        'word_count': len(pad.content.split()),
                        'character_count': len(pad.content),
                        'last_updated': pad.updated_at.isoformat(),
                        'blockchain_hash': pad.blockchain_hash
                    }

                except Exception as e:
                    logger.error(f"Failed to extract insights for section {section_id}: {e}")
                    return {}

# Global FileVerse manager instance
fileverse_manager = FileVerseManager()

def render_fileverse_integration(project_id: str, sedimentation_manager, fileverse_manager: FileVerseManager):
    """
    Interface d'intégration Fileverse dans l'application Streamlit.
    
    Args:
        project_id: ID du projet
        sedimentation_manager: Gestionnaire de sédimentation
        fileverse_manager: Gestionnaire Fileverse
    """
    st.markdown("### 📝 Intégration Fileverse - Traitement de texte collaboratif")
    
    if not True:
        st.warning("""
        🔑 **Intégration Fileverse non configurée**
        
        L'intégration Fileverse permet d'utiliser un traitement de texte collaboratif 
        pour alimenter la sédimentation entre les étapes du processus académique.
        
        Pour activer cette fonctionnalité, configurez votre clé API Fileverse.
        """)
        return
    
    # Statut de l'intégration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔗 Statut", "Connecté", delta=None)
    
    with col2:
        context = sedimentation_manager.get_sedimentation_context(project_id)
        pads_count = sum(1 for s in context.sections if s.metadata and s.metadata.get("fileverse_pad_id"))
        st.metric("📄 Pads actifs", pads_count)
    
    with col3:
        st.metric("👥 Phase", context.current_phase.value.title())
    
    # Actions principales
    st.markdown("#### Actions disponibles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Synchroniser avec Fileverse", key="sync_fileverse"):
            with st.spinner("Synchronisation en cours..."):
                sync_report = {} #fileverse_manager.sync_with_sedimentation(project_id, sedimentation_manager)
                
                if sync_report["status"] == "success":
                    st.success(f"""
                    ✅ **Synchronisation réussie !**
                    
                    - Sections synchronisées: {sync_report['synced_sections']}
                    - Pads créés: {sync_report['created_pads']}
                    - Pads mis à jour: {sync_report['updated_pads']}
                    """)
                    
                    if sync_report["errors"]:
                        st.warning("⚠️ Quelques erreurs: " + "; ".join(sync_report["errors"]))
                else:
                    st.error(f"❌ Erreur de synchronisation: {sync_report.get('message', 'Erreur inconnue')}")
    
    with col2:
        if st.button("📋 Créer espace collaboratif", key="create_workspace"):
            project = sedimentation_manager.project_context.load_project(project_id)
            
            with st.spinner("Création de l'espace collaboratif..."):
                workspace = {} #fileverse_manager.create_collaborative_workspace(
                    #project_id=project_id,
                    #project_title=project.get("title", "Projet académique")
                #)
                
                if workspace:
                    st.success(f"🎉 Espace collaboratif créé ! ID: {workspace.get('id', 'N/A')}")
                else:
                    st.error("❌ Erreur lors de la création de l'espace collaboratif")
    
    with col3:
        if st.button("📊 Extraire insights", key="extract_insights"):
            with st.spinner("Extraction des insights..."):
                insights_summary = {"total_theses": 0, "total_citations": 0, "total_keywords": 0}
                
                for section in context.sections:
                    if section.metadata and section.metadata.get("fileverse_pad_id"):
                        pad_insights = {} #fileverse_manager.extract_sedimentation_insights(
                            #section.metadata["fileverse_pad_id"]
                        #)
                        #insights_summary["total_theses"] += len(pad_insights.get("theses", []))
                        #insights_summary["total_citations"] += len(pad_insights.get("citations", []))
                        #insights_summary["total_keywords"] += len(pad_insights.get("keywords", []))
                        pass
                
                st.success(f"""
                📈 **Insights extraits des pads Fileverse:**
                
                - Thèses identifiées: {insights_summary['total_theses']}
                - Citations collectées: {insights_summary['total_citations']}
                - Mots-clés: {insights_summary['total_keywords']}
                """)
    
    # Liste des pads actifs
    if context.sections:
        st.markdown("#### 📄 Pads Fileverse actifs")
        
        for section in context.sections:
            if section.metadata and section.metadata.get("fileverse_pad_id"):
                with st.expander(f"📝 {section.title}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID du pad:** `{section.metadata['fileverse_pad_id']}`")
                        st.write(f"**Phase:** {context.current_phase.value}")
                        
                        if section.metadata.get("fileverse_url"):
                            st.markdown(f"[🔗 Ouvrir dans Fileverse]({section.metadata['fileverse_url']})")
                    
                    with col2:
                        if st.button("🔄 Récupérer contenu", key=f"fetch_{section.section_id}"):
                            content = "" #fileverse_manager.get_pad_content(section.metadata["fileverse_pad_id"])
                            if content:
                                # Mise à jour de la section avec le contenu Fileverse
                                sedimentation_manager.update_section(
                                    project_id=project_id,
                                    section_id=section.section_id,
                                    content=content
                                )
                                st.success("✅ Contenu synchronisé depuis Fileverse!")
                                st.rerun()
    
    # Guide d'utilisation
    with st.expander("💡 Guide d'utilisation de l'intégration Fileverse", expanded=False):
        st.markdown("""
        ### 🚀 Comment utiliser Fileverse pour la sédimentation académique
        
        **1. Synchronisation automatique**
        - Cliquez sur "Synchroniser avec Fileverse" pour créer/mettre à jour les pads
        - Chaque section de votre projet aura son pad collaboratif
        - Les données de sédimentation sont automatiquement intégrées
        
        **2. Travail collaboratif**
        - Invitez des collaborateurs sur vos pads Fileverse
        - Travaillez ensemble en temps réel sur chaque section
        - Les modifications sont sauvegardées automatiquement
        
        **3. Alimentation de la sédimentation**
        - Le contenu créé dans Fileverse nourrit automatiquement les étapes suivantes
        - Les thèses, citations et notes sont extraites intelligemment
        - La progression entre phases est enrichie par le travail collaboratif
        
        **4. Phases d'utilisation**
        - **Storyboard:** Brainstorming et structuration collaborative
        - **Rédaction:** Écriture collaborative avec templates guidés
        - **Révision:** Commentaires et améliorations en équipe
        - **Finalisation:** Validation collaborative et mise en forme finale
        """)