
"""
Module d'édition Fileverse intégré - Interface de traitement de texte
pour les itérations successives dans les phases de rédaction.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime
import streamlit.components.v1 as components

def render_fileverse_editor(project_id: str, section_id: str, project_context, 
                           sedimentation_manager, fileverse_manager):
    """
    Rendu de l'interface d'édition Fileverse intégrée.
    
    Args:
        project_id: ID du projet
        section_id: ID de la section
        project_context: Contexte du projet
        sedimentation_manager: Gestionnaire de sédimentation
        fileverse_manager: Gestionnaire Fileverse
    """
    st.subheader("📝 Éditeur Fileverse - Traitement de texte collaboratif")
    
    # Vérification de la disponibilité de Fileverse
    if not fileverse_manager.is_available():
        st.warning("🔑 **Fileverse non configuré**")
        st.info("Ajoutez votre clé API Fileverse dans les secrets pour activer le traitement de texte intégré.")
        return
    
    # Récupération du contexte de sédimentation
    context = sedimentation_manager.get_sedimentation_context(project_id)
    
    # Recherche de la section courante
    current_section = None
    for section in context.sections:
        if section.section_id == section_id:
            current_section = section
            break
    
    if not current_section:
        st.error("Section non trouvée")
        return
    
    # Interface en colonnes : Contrôles + Éditeur
    col1, col2 = st.columns([1, 2])
    
    with col1:
        render_fileverse_controls(current_section, context, fileverse_manager, sedimentation_manager)
    
    with col2:
        render_fileverse_embedded_editor(current_section, fileverse_manager)

def render_fileverse_controls(section, context, fileverse_manager, sedimentation_manager):
    """Panneau de contrôles pour l'éditeur Fileverse."""
    st.markdown("### 🎛️ Contrôles d'édition")
    
    # Statut du pad Fileverse
    pad_id = section.metadata.get('fileverse_pad_id') if section.metadata else None
    
    if pad_id:
        st.success(f"✅ **Pad actif:** {pad_id[:8]}...")
        
        # Informations sur le pad
        with st.expander("ℹ️ Informations du pad"):
            st.write(f"**Titre:** {section.title}")
            st.write(f"**Phase:** {context.current_phase.value}")
            st.write(f"**Dernière MAJ:** {section.metadata.get('last_fileverse_sync', 'Jamais')}")
            
            # URL du pad si disponible
            if section.metadata.get('fileverse_url'):
                st.markdown(f"[🔗 Ouvrir dans Fileverse]({section.metadata['fileverse_url']})")
    else:
        st.warning("⚠️ **Aucun pad associé**")
        
        # Bouton pour créer un pad
        if st.button("🚀 Créer un pad Fileverse", type="primary"):
            create_fileverse_pad_for_section(section, context, fileverse_manager, sedimentation_manager)
            st.rerun()
    
    st.markdown("---")
    
    # Contrôles de synchronisation
    st.markdown("### 🔄 Synchronisation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Importer depuis Fileverse"):
            sync_from_fileverse(section, fileverse_manager, sedimentation_manager)
            st.rerun()
    
    with col2:
        if st.button("📤 Exporter vers Fileverse"):
            sync_to_fileverse(section, fileverse_manager, sedimentation_manager)
            st.rerun()
    
    # Contrôles d'itération
    st.markdown("---")
    st.markdown("### 🔄 Itérations successives")
    
    # Historique des versions
    versions = get_section_versions(section)
    
    if versions:
        st.write(f"**{len(versions)} versions disponibles**")
        
        for i, version in enumerate(versions[-5:], 1):  # 5 dernières versions
            with st.expander(f"Version {i} - {version.get('timestamp', 'Date inconnue')}"):
                st.write(f"**Changements:** {version.get('description', 'Aucune description')}")
                st.write(f"**Mots:** {version.get('word_count', 0)}")
                
                if st.button(f"🔄 Restaurer version {i}", key=f"restore_{i}"):
                    restore_section_version(section, version, sedimentation_manager)
                    st.rerun()
    else:
        st.info("Aucune version sauvegardée")
    
    # Bouton de sauvegarde manuelle
    if st.button("💾 Sauvegarder version actuelle"):
        save_section_version(section, sedimentation_manager)
        st.success("Version sauvegardée!")
    
    # Métriques de progression
    st.markdown("---")
    st.markdown("### 📊 Métriques")
    
    word_count = len(section.content.split()) if section.content else 0
    st.metric("Mots", word_count)
    st.metric("Thèses", len(section.theses))
    st.metric("Citations", len(section.citations))

def render_fileverse_embedded_editor(section, fileverse_manager):
    """Rendu de l'éditeur Fileverse intégré."""
    st.markdown("### ✍️ Éditeur de texte")
    
    pad_id = section.metadata.get('fileverse_pad_id') if section.metadata else None
    
    if pad_id:
        # Récupération du contenu du pad
        pad_content = fileverse_manager.get_pad_content(pad_id)
        
        if pad_content is not None:
            # Interface d'édition avec iframe Fileverse
            render_fileverse_iframe(pad_id, section.metadata.get('fileverse_url'))
            
            # Alternative : Éditeur de texte intégré
            st.markdown("#### 📝 Éditeur alternatif (si iframe non disponible)")
            
            # Éditeur de texte riche
            edited_content = st.text_area(
                "Contenu du document",
                value=pad_content,
                height=400,
                key=f"editor_{section.section_id}",
                help="Modifiez directement le contenu ici, puis synchronisez avec Fileverse"
            )
            
            # Boutons d'action
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 Sauvegarder"):
                    if fileverse_manager.update_pad_content(pad_id, edited_content):
                        st.success("Contenu sauvegardé!")
                        # Mise à jour de la section locale
                        section.content = edited_content
                        section.metadata['last_fileverse_sync'] = datetime.now().isoformat()
                    else:
                        st.error("Erreur de sauvegarde")
            
            with col2:
                if st.button("🔄 Actualiser"):
                    st.rerun()
            
            with col3:
                if st.button("📊 Analyser"):
                    analyze_content_changes(edited_content, section.content)
        else:
            st.error("Impossible de récupérer le contenu du pad")
    else:
        # Éditeur local en attendant la création du pad
        st.info("Créez un pad Fileverse pour activer l'édition collaborative")
        
        # Éditeur local basique
        local_content = st.text_area(
            "Contenu local (temporaire)",
            value=section.content or "",
            height=300,
            help="Contenu local qui sera transféré vers Fileverse lors de la création du pad"
        )
        
        # Mise à jour du contenu local
        if local_content != section.content:
            section.content = local_content

def render_fileverse_iframe(pad_id: str, pad_url: Optional[str]):
    """Rendu de l'iframe Fileverse pour l'édition directe."""
    if pad_url:
        # Iframe avec l'éditeur Fileverse
        iframe_html = f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
            <div style="background: #f8f9fa; padding: 10px; border-bottom: 1px solid #ddd;">
                <strong>🔗 Éditeur Fileverse</strong>
                <a href="{pad_url}" target="_blank" style="float: right; color: #007bff;">
                    Ouvrir en plein écran ↗
                </a>
            </div>
            <iframe 
                src="{pad_url}" 
                width="100%" 
                height="500px" 
                frameborder="0"
                style="border: none;">
            </iframe>
        </div>
        """
        
        components.html(iframe_html, height=580)
    else:
        st.info("URL du pad non disponible - utilisez l'éditeur alternatif ci-dessous")

def create_fileverse_pad_for_section(section, context, fileverse_manager, sedimentation_manager):
    """Crée un pad Fileverse pour une section."""
    try:
        # Génération du contenu initial enrichi
        initial_content = generate_initial_pad_content(section, context)
        
        # Création du pad
        pad_info = fileverse_manager.create_sedimentation_pad(
            project_id=context.project_id,
            section_title=section.title,
            phase=context.current_phase.value,
            initial_content=initial_content
        )
        
        if pad_info:
            # Mise à jour des métadonnées de la section
            if not section.metadata:
                section.metadata = {}
            
            section.metadata['fileverse_pad_id'] = pad_info['id']
            section.metadata['fileverse_url'] = pad_info.get('url', '')
            section.metadata['created_at'] = datetime.now().isoformat()
            section.metadata['last_fileverse_sync'] = datetime.now().isoformat()
            
            # Sauvegarde du contexte
            sedimentation_manager.save_sedimentation_context(context)
            
            st.success(f"✅ Pad Fileverse créé avec succès: {pad_info['id']}")
        else:
            st.error("❌ Erreur lors de la création du pad")
            
    except Exception as e:
        st.error(f"Erreur lors de la création du pad: {str(e)}")

def generate_initial_pad_content(section, context):
    """Génère le contenu initial pour un pad Fileverse."""
    content = f"""# {section.title}

<!-- Éditeur Fileverse - Phase: {context.current_phase.value} -->
<!-- Section ID: {section.section_id} -->
<!-- Créé le: {datetime.now().strftime('%Y-%m-%d %H:%M')} -->

## 📋 Informations de la section

**Description:** {section.description or 'À définir'}

**Phase actuelle:** {context.current_phase.value}

**Objectifs:** 
- [ ] Rédiger le contenu principal
- [ ] Intégrer les thèses identifiées
- [ ] Ajouter les citations appropriées
- [ ] Réviser et améliorer

---

## 💡 Données de sédimentation

"""
    
    # Ajout des thèses
    if section.theses:
        content += "### 🎯 Thèses à développer\n\n"
        for i, thesis in enumerate(section.theses, 1):
            content += f"**Thèse {i}:** {thesis}\n\n"
    
    # Ajout des citations
    if section.citations:
        content += "### 📚 Citations suggérées\n\n"
        for citation in section.citations:
            content += f"- {citation}\n"
        content += "\n"
    
    # Contenu existant
    if section.content:
        content += f"### 📄 Contenu existant\n\n{section.content}\n\n"
    
    # Zone de travail
    content += """---

## ✍️ Zone de rédaction

*Commencez à rédiger ici. Ce contenu sera synchronisé avec votre système de sédimentation.*



---

## 📝 Notes et commentaires

*Ajoutez vos notes, idées et commentaires ici...*



---

## 🔄 Historique des modifications

*Cet espace sera automatiquement mis à jour avec les changements*

"""
    
    return content

def sync_from_fileverse(section, fileverse_manager, sedimentation_manager):
    """Synchronise le contenu depuis Fileverse vers la section locale."""
    pad_id = section.metadata.get('fileverse_pad_id') if section.metadata else None
    
    if not pad_id:
        st.error("Aucun pad Fileverse associé")
        return
    
    try:
        # Récupération du contenu
        pad_content = fileverse_manager.get_pad_content(pad_id)
        
        if pad_content is not None:
            # Extraction des insights
            insights = fileverse_manager.extract_sedimentation_insights(pad_id)
            
            # Mise à jour de la section
            section.content = pad_content
            
            # Enrichissement avec les insights
            if insights.get('theses'):
                section.theses.extend(insights['theses'])
                section.theses = list(set(section.theses))  # Suppression des doublons
            
            if insights.get('citations'):
                section.citations.extend(insights['citations'])
                section.citations = list(set(section.citations))  # Suppression des doublons
            
            # Mise à jour des métadonnées
            section.metadata['last_fileverse_sync'] = datetime.now().isoformat()
            section.metadata['sync_direction'] = 'from_fileverse'
            
            st.success("✅ Contenu synchronisé depuis Fileverse")
        else:
            st.error("❌ Impossible de récupérer le contenu du pad")
            
    except Exception as e:
        st.error(f"Erreur lors de la synchronisation: {str(e)}")

def sync_to_fileverse(section, fileverse_manager, sedimentation_manager):
    """Synchronise le contenu de la section locale vers Fileverse."""
    pad_id = section.metadata.get('fileverse_pad_id') if section.metadata else None
    
    if not pad_id:
        st.error("Aucun pad Fileverse associé")
        return
    
    try:
        # Génération du contenu enrichi
        enhanced_content = generate_enhanced_content_for_fileverse(section)
        
        # Mise à jour du pad
        if fileverse_manager.update_pad_content(pad_id, enhanced_content):
            # Mise à jour des métadonnées
            section.metadata['last_fileverse_sync'] = datetime.now().isoformat()
            section.metadata['sync_direction'] = 'to_fileverse'
            
            st.success("✅ Contenu synchronisé vers Fileverse")
        else:
            st.error("❌ Erreur lors de la mise à jour du pad")
            
    except Exception as e:
        st.error(f"Erreur lors de la synchronisation: {str(e)}")

def generate_enhanced_content_for_fileverse(section):
    """Génère un contenu enrichi pour Fileverse."""
    content = f"""# {section.title}

<!-- Mis à jour le: {datetime.now().strftime('%Y-%m-%d %H:%M')} -->

## 📄 Contenu principal

{section.content or '*Contenu à rédiger...*'}

---

## 💡 Éléments de sédimentation

"""
    
    if section.theses:
        content += "### 🎯 Thèses développées\n\n"
        for i, thesis in enumerate(section.theses, 1):
            content += f"**Thèse {i}:** {thesis}\n\n"
    
    if section.citations:
        content += "### 📚 Citations intégrées\n\n"
        for citation in section.citations:
            content += f"- {citation}\n"
        content += "\n"
    
    content += """---

## 🔄 Zone de travail collaboratif

*Utilisez cet espace pour les itérations et améliorations...*

"""
    
    return content

def get_section_versions(section):
    """Récupère les versions sauvegardées d'une section."""
    # Simulation - en production, récupérer depuis la base de données
    return section.metadata.get('versions', []) if section.metadata else []

def save_section_version(section, sedimentation_manager):
    """Sauvegarde une version de la section."""
    if not section.metadata:
        section.metadata = {}
    
    if 'versions' not in section.metadata:
        section.metadata['versions'] = []
    
    version = {
        'timestamp': datetime.now().isoformat(),
        'content': section.content,
        'word_count': len(section.content.split()) if section.content else 0,
        'theses_count': len(section.theses),
        'citations_count': len(section.citations),
        'description': f"Version automatique - {len(section.content.split()) if section.content else 0} mots"
    }
    
    section.metadata['versions'].append(version)
    
    # Limiter à 10 versions maximum
    if len(section.metadata['versions']) > 10:
        section.metadata['versions'] = section.metadata['versions'][-10:]

def restore_section_version(section, version, sedimentation_manager):
    """Restaure une version spécifique de la section."""
    section.content = version.get('content', '')
    
    # Mise à jour des métadonnées
    if not section.metadata:
        section.metadata = {}
    
    section.metadata['last_restore'] = datetime.now().isoformat()
    section.metadata['restored_from'] = version.get('timestamp')

def analyze_content_changes(new_content, old_content):
    """Analyse les changements dans le contenu."""
    if not old_content:
        old_content = ""
    
    new_words = len(new_content.split())
    old_words = len(old_content.split())
    word_diff = new_words - old_words
    
    st.info(f"📊 **Analyse des changements:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Mots actuels", new_words)
    
    with col2:
        st.metric("Mots précédents", old_words)
    
    with col3:
        st.metric("Différence", word_diff, delta=word_diff)
    
    if word_diff > 0:
        st.success(f"✅ Ajout de {word_diff} mots")
    elif word_diff < 0:
        st.warning(f"⚠️ Suppression de {abs(word_diff)} mots")
    else:
        st.info("ℹ️ Aucun changement de longueur")
