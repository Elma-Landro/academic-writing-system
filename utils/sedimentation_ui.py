
"""
Composants d'interface pour la gestion de la sédimentation
"""

import streamlit as st
from typing import Dict, Any, Optional
from sedimentation_manager import SedimentationManager, SedimentationPhase

def render_sedimentation_progress(sedimentation_manager: SedimentationManager, project_id: str):
    """Affiche la progression de sédimentation d'un projet avec visualisations enrichies."""
    context = sedimentation_manager.get_sedimentation_context(project_id)
    
    # Barre de progression visuelle enrichie
    phases = [
        ("📋 Storyboard", SedimentationPhase.STORYBOARD, "#FF6B6B"),
        ("✍️ Rédaction", SedimentationPhase.REDACTION, "#4ECDC4"),
        ("🔍 Révision", SedimentationPhase.REVISION, "#45B7D1"),
        ("📄 Finalisation", SedimentationPhase.FINALISATION, "#96CEB4")
    ]
    
    current_phase_index = [p[1] for p in phases].index(context.current_phase)
    
    # Affichage horizontal avec indicateurs visuels
    cols = st.columns(len(phases))
    
    for i, ((name, phase, color), col) in enumerate(zip(phases, cols)):
        with col:
            if i <= current_phase_index:
                if i == current_phase_index:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px; border: 2px solid {color}; border-radius: 10px; background-color: rgba(255,255,255,0.1);">
                        <h4 style="color: {color};">🎯 {name}</h4>
                        <p style="color: {color}; font-style: italic;">Phase actuelle</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px; border: 1px solid {color}; border-radius: 10px; background-color: rgba(150,206,180,0.2);">
                        <h4 style="color: {color};">✅ {name}</h4>
                        <p style="color: {color};">Terminé</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; border: 1px dashed #cccccc; border-radius: 10px; background-color: rgba(200,200,200,0.1);">
                    <h4 style="color: #999;">⏳ {name}</h4>
                    <p style="color: #999;">À venir</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Barre de progression continue avec pourcentage
    progress = (current_phase_index + 1) / len(phases)
    st.progress(progress)
    
    # Métriques de progression
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Progression", f"{progress:.0%}")
    
    with col2:
        sections_total = len(context.sections)
        st.metric("📚 Sections", sections_total)
    
    with col3:
        sections_with_content = sum(1 for s in context.sections if s.content)
        completion = sections_with_content / max(1, sections_total)
        st.metric("✅ Complétées", f"{completion:.0%}")
    
    with col4:
        total_words = sum(len(s.content.split()) if s.content else 0 for s in context.sections)
        st.metric("📝 Mots", total_words)
    
    # Timeline de transitions si disponible
    if context.transitions_log:
        with st.expander("📊 Historique des transitions", expanded=False):
            for transition in context.transitions_log[-5:]:  # 5 dernières transitions
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**{transition['from_phase']}** → **{transition['to_phase']}**")
                with col2:
                    from datetime import datetime
                    timestamp = datetime.fromisoformat(transition['timestamp'])
                    st.write(timestamp.strftime("%d/%m/%Y %H:%M"))
                with col3:
                    st.write(f"{transition.get('sections_count', 0)} sections")
    
    return context

def render_phase_transition_widget(sedimentation_manager: SedimentationManager, project_id: str):
    """Widget pour gérer les transitions entre phases."""
    context = sedimentation_manager.get_sedimentation_context(project_id)
    
    st.subheader("🔄 Gestion des phases")
    
    # Déterminer les transitions possibles
    possible_transitions = {
        SedimentationPhase.STORYBOARD: [("Passer à la rédaction", SedimentationPhase.REDACTION)],
        SedimentationPhase.REDACTION: [
            ("Passer à la révision", SedimentationPhase.REVISION),
            ("Retour au storyboard", SedimentationPhase.STORYBOARD)
        ],
        SedimentationPhase.REVISION: [
            ("Passer à la finalisation", SedimentationPhase.FINALISATION),
            ("Retour à la rédaction", SedimentationPhase.REDACTION)
        ],
        SedimentationPhase.FINALISATION: [
            ("Retour à la révision", SedimentationPhase.REVISION)
        ]
    }
    
    transitions = possible_transitions.get(context.current_phase, [])
    
    for transition_label, target_phase in transitions:
        # Vérifier la préparation pour cette transition
        readiness = sedimentation_manager.get_transition_readiness(project_id, target_phase)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if readiness['ready']:
                st.success(f"✅ Prêt pour: {transition_label}")
                if readiness['requirements_met']:
                    st.caption("✓ " + " | ".join(readiness['requirements_met']))
            else:
                st.warning(f"⚠️ Pas encore prêt: {transition_label}")
                if readiness['requirements_missing']:
                    st.caption("❌ " + " | ".join(readiness['requirements_missing']))
        
        with col2:
            button_disabled = not readiness['ready']
            if st.button(
                "Passer" if readiness['ready'] else "Pas prêt",
                key=f"transition_{target_phase.value}",
                disabled=button_disabled,
                type="primary" if readiness['ready'] else "secondary"
            ):
                # Effectuer la transition
                result = sedimentation_manager.transition_to_phase(project_id, target_phase)
                
                if result['success']:
                    st.success(f"🎉 Transition réussie vers {target_phase.value}!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ Erreur de transition: {result.get('error', 'Erreur inconnue')}")

def render_sedimentation_data_flow(context, transition_data: Optional[Dict[str, Any]] = None):
    """Affiche le flux de données de sédimentation enrichi par Fileverse."""
    if not transition_data:
        return
    
    st.subheader("📊 Données de transition")
    
    # Indicateur d'intégration Fileverse
    if transition_data.get('fileverse_integration'):
        st.success("🔗 **Intégration Fileverse active** - Données enrichies par le traitement de texte collaboratif")
        
        if 'fileverse_sync' in transition_data:
            sync_data = transition_data['fileverse_sync']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Pads créés", sync_data.get('created_pads', 0))
            with col2:
                st.metric("Pads mis à jour", sync_data.get('updated_pads', 0))
            with col3:
                st.metric("Sections sync", sync_data.get('synced_sections', 0))
    
    # Afficher les données selon la phase
    if context.current_phase == SedimentationPhase.REDACTION and 'pre_filled_sections' in transition_data:
        st.write("**Sections pré-remplies pour la rédaction:**")
        for section_data in transition_data['pre_filled_sections']:
            with st.expander(f"📝 {section_data['title']}"):
                if section_data.get('theses'):
                    st.write("**Thèses identifiées:**")
                    for thesis in section_data['theses']:
                        st.write(f"• {thesis}")
                
                if section_data.get('citations'):
                    st.write("**Citations suggérées:**")
                    for citation in section_data['citations']:
                        st.write(f"• {citation}")
                
                if section_data.get('writing_prompts'):
                    st.write("**Prompts d'écriture:**")
                    for prompt in section_data['writing_prompts']:
                        st.write(f"💡 {prompt}")
    
    elif context.current_phase == SedimentationPhase.REVISION and 'content_analysis' in transition_data:
        st.write("**Analyse du contenu pour révision:**")
        
        # Statistiques globales
        if 'global_stats' in transition_data:
            stats = transition_data['global_stats']
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Mots totaux", stats.get('total_words', 0))
            with col2:
                st.metric("Sections rédigées", stats.get('sections_with_content', 0))
            with col3:
                completion = stats.get('completion_rate', 0)
                st.metric("Taux de completion", f"{completion:.1%}")
        
        # Analyse par section
        for section_id, analysis in transition_data.get('content_analysis', {}).items():
            st.write(f"**{section_id}:** {analysis['word_count']} mots - {analysis['completion_status']}")
    
    elif context.current_phase == SedimentationPhase.FINALISATION and 'quality_metrics' in transition_data:
        st.write("**Métriques de qualité pour finalisation:**")
        
        metrics = transition_data['quality_metrics']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mots totaux", metrics.get('total_words', 0))
        with col2:
            st.metric("Sections", metrics.get('total_sections', 0))
        with col3:
            st.metric("Thèses", metrics.get('total_theses', 0))
        with col4:
            st.metric("Citations", metrics.get('total_citations', 0))

def render_sections_overview(context):
    """Affiche un aperçu enrichi des sections du projet."""
    if not context.sections:
        st.info("📝 Aucune section créée. Commencez par créer la structure de votre document.")
        return
    
    st.subheader(f"📚 Structure du document ({len(context.sections)} sections)")
    
    # Métriques globales
    total_words = sum(len(s.content.split()) if s.content else 0 for s in context.sections)
    total_theses = sum(len(s.theses) for s in context.sections)
    total_citations = sum(len(s.citations) for s in context.sections)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Mots total", total_words)
    with col2:
        st.metric("💡 Thèses", total_theses)
    with col3:
        st.metric("📚 Citations", total_citations)
    with col4:
        avg_words = total_words // max(1, len(context.sections))
        st.metric("📊 Moy/section", avg_words)
    
    st.markdown("---")
    
    # Affichage détaillé des sections avec barres de progression
    for i, section in enumerate(context.sections, 1):
        # Calculs pour les indicateurs visuels
        word_count = len(section.content.split()) if section.content else 0
        completion_score = min(100, (word_count / max(1, avg_words)) * 100) if avg_words > 0 else 0
        
        # Couleur basée sur le statut
        if word_count > 100:
            status_color = "#28a745"  # Vert
            status_text = "✅ Complète"
        elif word_count > 0:
            status_color = "#ffc107"  # Jaune
            status_text = "🟡 En cours"
        else:
            status_color = "#6c757d"  # Gris
            status_text = "⏳ À faire"
        
        # Container avec bordure colorée
        st.markdown(f"""
        <div style="border-left: 4px solid {status_color}; padding-left: 15px; margin-bottom: 20px;">
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([4, 2, 1])
        
        with col1:
            st.markdown(f"### {i}. {section.title}")
            if section.description:
                st.caption(f"📝 {section.description[:150]}{'...' if len(section.description) > 150 else ''}")
            
            # Barre de progression de completion
            if word_count > 0:
                st.progress(min(1.0, completion_score / 100))
                st.caption(f"Progression: {completion_score:.0f}%")
        
        with col2:
            # Métriques de la section
            st.markdown("**📊 Métriques**")
            st.write(f"📝 {word_count} mots")
            st.write(f"💡 {len(section.theses)} thèses")
            st.write(f"📚 {len(section.citations)} citations")
            
            # Détail des thèses si disponibles
            if section.theses:
                with st.expander(f"💡 Voir les {len(section.theses)} thèses"):
                    for j, thesis in enumerate(section.theses, 1):
                        st.write(f"{j}. {thesis[:100]}{'...' if len(thesis) > 100 else ''}")
        
        with col3:
            st.markdown("**📈 Statut**")
            st.markdown(f"<p style='color: {status_color}; font-weight: bold;'>{status_text}</p>", unsafe_allow_html=True)
            
            # Indicateur de densité qualitative si calculable
            if word_count > 0:
                density = min(100, (len(section.theses) * 20 + len(section.citations) * 10 + word_count / 10))
                st.write(f"🎯 Densité: {density:.0f}%")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Séparateur
        st.markdown("---")
