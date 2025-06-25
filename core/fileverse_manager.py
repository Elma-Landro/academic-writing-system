
"""
Gestionnaire d'intégration Fileverse pour la sédimentation académique.
Permet l'utilisation du traitement de texte intégré pour alimenter les étapes successives.
"""

import streamlit as st
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class FileversePadData:
    """Structure pour les données d'un pad Fileverse."""
    pad_id: str
    title: str
    content: str
    collaborators: List[str]
    last_modified: str
    section_type: str = "intermediate"  # intermediate, draft, final
    sedimentation_phase: str = "storyboard"  # storyboard, redaction, revision, finalisation

class FileVerseManager:
    """
    Gestionnaire d'intégration avec Fileverse pour la création collaborative
    et l'alimentation de la sédimentation académique.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le gestionnaire Fileverse.
        
        Args:
            api_key: Clé API Fileverse (optionnelle, récupérée des secrets)
        """
        self.api_key = api_key or st.secrets.get("FILEVERSE_API_KEY", "")
        self.base_url = "https://api.fileverse.io/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}
        
        # Cache local des pads pour optimiser les performances
        self.pads_cache = {}
    
    def is_available(self) -> bool:
        """Vérifie si l'intégration Fileverse est disponible."""
        return bool(self.api_key)
    
    def create_sedimentation_pad(self, project_id: str, section_title: str, 
                               phase: str, initial_content: str = "") -> Optional[Dict]:
        """
        Crée un pad Fileverse pour une section spécifique d'un projet.
        
        Args:
            project_id: ID du projet
            section_title: Titre de la section
            phase: Phase de sédimentation (storyboard, redaction, etc.)
            initial_content: Contenu initial du pad
            
        Returns:
            Données du pad créé ou None en cas d'erreur
        """
        if not self.is_available():
            st.warning("🔑 Intégration Fileverse non configurée (clé API manquante)")
            return None
        
        try:
            pad_data = {
                "title": f"[{phase.upper()}] {section_title} - Projet {project_id}",
                "content": initial_content or f"# {section_title}\n\n<!-- Phase: {phase} -->\n\n",
                "isPublic": False,
                "metadata": {
                    "project_id": project_id,
                    "section_title": section_title,
                    "sedimentation_phase": phase,
                    "creation_type": "academic_sedimentation"
                }
            }
            
            response = requests.post(
                f"{self.base_url}/pads",
                headers=self.headers,
                json=pad_data,
                timeout=10
            )
            
            if response.status_code == 201:
                pad_info = response.json()
                
                # Cache du pad créé
                self.pads_cache[pad_info["id"]] = FileversePadData(
                    pad_id=pad_info["id"],
                    title=pad_data["title"],
                    content=pad_data["content"],
                    collaborators=[],
                    last_modified=datetime.now().isoformat(),
                    sedimentation_phase=phase
                )
                
                return pad_info
            else:
                st.error(f"Erreur Fileverse: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Erreur lors de la création du pad Fileverse: {str(e)}")
            return None
    
    def get_pad_content(self, pad_id: str) -> Optional[str]:
        """
        Récupère le contenu d'un pad Fileverse.
        
        Args:
            pad_id: ID du pad
            
        Returns:
            Contenu du pad ou None
        """
        if not self.is_available():
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/pads/{pad_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                pad_data = response.json()
                return pad_data.get("content", "")
            else:
                return None
                
        except Exception as e:
            st.error(f"Erreur lors de la récupération du pad: {str(e)}")
            return None
    
    def update_pad_content(self, pad_id: str, content: str) -> bool:
        """
        Met à jour le contenu d'un pad Fileverse.
        
        Args:
            pad_id: ID du pad
            content: Nouveau contenu
            
        Returns:
            True si la mise à jour a réussi
        """
        if not self.is_available():
            return False
        
        try:
            response = requests.patch(
                f"{self.base_url}/pads/{pad_id}",
                headers=self.headers,
                json={"content": content},
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            st.error(f"Erreur lors de la mise à jour du pad: {str(e)}")
            return False
    
    def sync_with_sedimentation(self, project_id: str, sedimentation_manager) -> Dict[str, Any]:
        """
        Synchronise les pads Fileverse avec les données de sédimentation.
        
        Args:
            project_id: ID du projet
            sedimentation_manager: Instance du gestionnaire de sédimentation
            
        Returns:
            Rapport de synchronisation
        """
        if not self.is_available():
            return {"status": "unavailable", "message": "Fileverse non configuré"}
        
        context = sedimentation_manager.get_sedimentation_context(project_id)
        sync_report = {
            "status": "success",
            "synced_sections": 0,
            "created_pads": 0,
            "updated_pads": 0,
            "errors": []
        }
        
        for section in context.sections:
            try:
                # Recherche d'un pad existant pour cette section
                existing_pad = self._find_section_pad(project_id, section.section_id, context.current_phase.value)
                
                if existing_pad:
                    # Mise à jour du pad existant avec les données de sédimentation
                    enhanced_content = self._enhance_content_with_sedimentation(
                        section, context.current_phase.value
                    )
                    
                    if self.update_pad_content(existing_pad["id"], enhanced_content):
                        sync_report["updated_pads"] += 1
                    else:
                        sync_report["errors"].append(f"Échec mise à jour pad {section.title}")
                else:
                    # Création d'un nouveau pad
                    initial_content = self._generate_pad_template(section, context.current_phase.value)
                    
                    pad_info = self.create_sedimentation_pad(
                        project_id=project_id,
                        section_title=section.title,
                        phase=context.current_phase.value,
                        initial_content=initial_content
                    )
                    
                    if pad_info:
                        sync_report["created_pads"] += 1
                        
                        # Mise à jour de la section avec l'ID du pad
                        section.metadata = section.metadata or {}
                        section.metadata["fileverse_pad_id"] = pad_info["id"]
                        section.metadata["fileverse_url"] = pad_info.get("url", "")
                
                sync_report["synced_sections"] += 1
                
            except Exception as e:
                sync_report["errors"].append(f"Erreur section {section.title}: {str(e)}")
        
        # Sauvegarde du contexte mis à jour
        sedimentation_manager.save_sedimentation_context(context)
        
        return sync_report
    
    def create_collaborative_workspace(self, project_id: str, project_title: str, 
                                     collaborators: List[str] = None) -> Optional[Dict]:
        """
        Crée un espace de travail collaboratif Fileverse pour un projet complet.
        
        Args:
            project_id: ID du projet
            project_title: Titre du projet
            collaborators: Liste des emails des collaborateurs
            
        Returns:
            Informations sur l'espace de travail créé
        """
        if not self.is_available():
            return None
        
        try:
            workspace_data = {
                "name": f"Espace Académique - {project_title}",
                "description": f"Espace collaboratif pour le projet académique: {project_title}",
                "isPublic": False,
                "metadata": {
                    "project_id": project_id,
                    "type": "academic_workspace",
                    "sedimentation_enabled": True
                }
            }
            
            if collaborators:
                workspace_data["collaborators"] = collaborators
            
            response = requests.post(
                f"{self.base_url}/workspaces",
                headers=self.headers,
                json=workspace_data,
                timeout=15
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                st.error(f"Erreur création workspace Fileverse: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Erreur lors de la création de l'espace de travail: {str(e)}")
            return None
    
    def extract_sedimentation_insights(self, pad_id: str) -> Dict[str, Any]:
        """
        Extrait les insights de sédimentation depuis un pad Fileverse.
        
        Args:
            pad_id: ID du pad
            
        Returns:
            Insights extraits (thèses, citations, métadonnées)
        """
        content = self.get_pad_content(pad_id)
        if not content:
            return {}
        
        insights = {
            "theses": [],
            "citations": [],
            "keywords": [],
            "structure_notes": [],
            "collaboration_notes": []
        }
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Extraction des thèses (lignes commençant par **Thèse** ou similaire)
            if line.startswith('**Thèse') or line.startswith('## Thèse'):
                insights["theses"].append(line.replace('**', '').replace('##', '').strip())
            
            # Extraction des citations (format markdown ou académique)
            elif '[' in line and ']' in line and ('http' in line or 'doi:' in line):
                insights["citations"].append(line.strip())
            
            # Extraction des mots-clés (lignes avec #tags)
            elif line.startswith('#') and not line.startswith('##'):
                insights["keywords"].extend([tag.strip() for tag in line.split('#') if tag.strip()])
            
            # Notes structurelles (commentaires HTML)
            elif line.startswith('<!-- ') and line.endswith(' -->'):
                note = line.replace('<!--', '').replace('-->', '').strip()
                insights["structure_notes"].append(note)
        
        return insights
    
    def _find_section_pad(self, project_id: str, section_id: str, phase: str) -> Optional[Dict]:
        """Recherche un pad existant pour une section donnée."""
        # Simulation - en production, implémenter la recherche via l'API Fileverse
        return None
    
    def _enhance_content_with_sedimentation(self, section, phase: str) -> str:
        """
        Enrichit le contenu d'un pad avec les données de sédimentation.
        
        Args:
            section: Section de sédimentation
            phase: Phase actuelle
            
        Returns:
            Contenu enrichi
        """
        content = f"# {section.title}\n\n"
        content += f"<!-- Phase: {phase} | Section ID: {section.section_id} -->\n\n"
        
        if section.description:
            content += f"## Description\n{section.description}\n\n"
        
        if section.theses:
            content += "## Thèses identifiées\n\n"
            for i, thesis in enumerate(section.theses, 1):
                content += f"**Thèse {i}:** {thesis}\n\n"
        
        if section.citations:
            content += "## Citations suggérées\n\n"
            for citation in section.citations:
                content += f"- {citation}\n"
            content += "\n"
        
        if section.content:
            content += "## Contenu existant\n\n"
            content += section.content + "\n\n"
        
        # Zone de travail collaboratif
        content += "---\n\n"
        content += "## Zone de travail collaboratif\n\n"
        content += "*Utilisez cet espace pour développer, annoter et enrichir le contenu...*\n\n"
        
        return content
    
    def _generate_pad_template(self, section, phase: str) -> str:
        """Génère un template de pad selon la phase de sédimentation."""
        if phase == "storyboard":
            return f"""# {section.title}

<!-- Phase: Storyboard | Section ID: {section.section_id} -->

## Objectifs de la section
- [ ] Définir les thèses principales
- [ ] Identifier les sources clés
- [ ] Structurer l'argumentation

## Brainstorming collaboratif
*Ajoutez vos idées, références et notes ici...*

## Structure proposée
1. Introduction
2. Développement
3. Conclusion

---
*Espace de travail collaboratif - Modifiez librement*
"""
        
        elif phase == "redaction":
            return f"""# {section.title}

<!-- Phase: Rédaction | Section ID: {section.section_id} -->

## Contenu principal

### Introduction
*Rédigez l'introduction de la section...*

### Développement
*Développez les arguments principaux...*

### Conclusion
*Concluez la section...*

## Notes de rédaction
- [ ] Vérifier la cohérence avec les autres sections
- [ ] Intégrer les citations appropriées
- [ ] Réviser le style et la clarté

---
*Espace de collaboration - Commentaires et suggestions*
"""
        
        elif phase == "revision":
            return f"""# {section.title} - Révision

<!-- Phase: Révision | Section ID: {section.section_id} -->

## Contenu en révision
{section.content if section.content else "*Contenu à réviser...*"}

## Points de révision
- [ ] Clarté des arguments
- [ ] Cohérence stylistique  
- [ ] Exactitude des citations
- [ ] Fluidité des transitions

## Commentaires collaboratifs
*Ajoutez vos commentaires et suggestions d'amélioration...*

---
*Zone de révision collaborative*
"""
        
        else:  # finalisation
            return f"""# {section.title} - Finalisation

<!-- Phase: Finalisation | Section ID: {section.section_id} -->

## Version finale
{section.content if section.content else "*Version finale à valider...*"}

## Checklist de finalisation
- [ ] Mise en forme finale
- [ ] Vérification des références
- [ ] Cohérence avec l'ensemble du document
- [ ] Validation collaborative

## Approbations
- [ ] Auteur principal
- [ ] Collaborateurs
- [ ] Relecteurs

---
*Document prêt pour export*
"""

def render_fileverse_integration(project_id: str, sedimentation_manager, fileverse_manager: FileVerseManager):
    """
    Interface d'intégration Fileverse dans l'application Streamlit.
    
    Args:
        project_id: ID du projet
        sedimentation_manager: Gestionnaire de sédimentation
        fileverse_manager: Gestionnaire Fileverse
    """
    st.markdown("### 📝 Intégration Fileverse - Traitement de texte collaboratif")
    
    if not fileverse_manager.is_available():
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
                sync_report = fileverse_manager.sync_with_sedimentation(project_id, sedimentation_manager)
                
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
                workspace = fileverse_manager.create_collaborative_workspace(
                    project_id=project_id,
                    project_title=project.get("title", "Projet académique")
                )
                
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
                        pad_insights = fileverse_manager.extract_sedimentation_insights(
                            section.metadata["fileverse_pad_id"]
                        )
                        insights_summary["total_theses"] += len(pad_insights.get("theses", []))
                        insights_summary["total_citations"] += len(pad_insights.get("citations", []))
                        insights_summary["total_keywords"] += len(pad_insights.get("keywords", []))
                
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
                            content = fileverse_manager.get_pad_content(section.metadata["fileverse_pad_id"])
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
