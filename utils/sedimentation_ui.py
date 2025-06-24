
"""
Composants d'interface pour la gestion de la sédimentation
"""

import streamlit as st
from typing import Dict, Any, Optional
from sedimentation_manager import SedimentationManager, SedimentationPhase

def render_sedimentation_progress(sedimentation_manager: SedimentationManager, project_id: str):
    """Affiche la progression de sédimentation d'un projet."""
    context = sedimentation_manager.get_sedimentation_context(project_id)
    
    # Barre de progression visuelle
    phases = [
        ("📋 Storyboard", SedimentationPhase.STORYBOARD),
        ("✍️ Rédaction", SedimentationPhase.REDACTION),
        ("🔍 Révision", SedimentationPhase.REVISION),
        ("📄 Finalisation", SedimentationPhase.FINALISATION)
    ]
    
    cols = st.columns(len(phases))
    current_phase_index = [p[1] for p in phases].index(context.current_phase)
    
    for i, ((name, phase), col) in enumerate(zip(phases, cols)):
        with col:
            if i <= current_phase_index:
                if i == current_phase_index:
                    st.markdown(f"**🎯 {name}**")
                    st.markdown("*Phase actuelle*")
                else:
                    st.markdown(f"✅ {name}")
                    st.markdown("*Terminé*")
            else:
                st.markdown(f"⏳ {name}")
                st.markdown("*À venir*")
    
    # Barre de progression continue
    progress = (current_phase_index + 1) / len(phases)
    st.progress(progress)
    
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
    """Affiche le flux de données de sédimentation."""
    if not transition_data:
        return
    
    st.subheader("📊 Données de transition")
    
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
    """Affiche un aperçu des sections du projet."""
    if not context.sections:
        st.info("📝 Aucune section créée. Commencez par créer la structure de votre document.")
        return
    
    st.subheader(f"📚 Structure du document ({len(context.sections)} sections)")
    
    for i, section in enumerate(context.sections, 1):
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{i}. {section.title}**")
                if section.description:
                    st.caption(section.description[:100] + "..." if len(section.description) > 100 else section.description)
            
            with col2:
                # Indicateurs de progression
                indicators = []
                if section.content:
                    word_count = len(section.content.split())
                    indicators.append(f"📝 {word_count} mots")
                if section.theses:
                    indicators.append(f"💡 {len(section.theses)} thèses")
                if section.citations:
                    indicators.append(f"📚 {len(section.citations)} citations")
                
                if indicators:
                    st.write(" | ".join(indicators))
                else:
                    st.caption("Vide")
            
            with col3:
                # Statut de la section
                if section.content and len(section.content.split()) > 100:
                    st.success("✅ Complète")
                elif section.content:
                    st.warning("🟡 En cours")
                else:
                    st.info("⏳ À faire")
            
            st.markdown("---")
