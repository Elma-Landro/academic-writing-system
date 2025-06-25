
"""
Module de finalisation enrichi pour le système de rédaction académique.
Permet de finaliser un projet avec amélioration IA ligne par ligne et export avancé.
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
import json

# Try to import optional dependencies
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    st.warning("pandas not available. Some features may be limited.")

from utils.ai_service import call_ai_safe, generate_academic_text

def render_finalisation(project_id: str, project_context, history_manager, adaptive_engine=None, sedimentation_manager=None):
    """
    Interface de finalisation enrichie d'un projet.

    Args:
        project_id: ID du projet
        project_context: Instance de ProjectContext
        history_manager: Instance de HistoryManager
        adaptive_engine: Instance de AdaptiveEngine (optionnel)
        sedimentation_manager: Instance de SedimentationManager (optionnel)
    """
    if not project_id:
        st.error("Aucun projet sélectionné.")
        return

    # Chargement du projet
    project = project_context.load_project(project_id)
    if not project:
        st.error("Projet non trouvé.")
        return

    st.title("📄 Finalisation du projet")
    st.subheader(project.get("title", "Sans titre"))

    # Affichage des métriques de progression
    sections = project.get("sections", [])
    if sections:
        total_words = sum(len(section.get("content", "").split()) for section in sections)
        completed_sections = sum(1 for section in sections if section.get("content", "").strip())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sections", f"{completed_sections}/{len(sections)}")
        with col2:
            st.metric("Mots totaux", total_words)
        with col3:
            completion = (completed_sections / len(sections) * 100) if sections else 0
            st.metric("Progression", f"{completion:.0f}%")

    # Visualisation de la progression de sédimentation
    if sedimentation_manager:
        from utils.sedimentation_ui import render_sedimentation_progress, render_sedimentation_data_flow
        
        st.markdown("### 🌱 Progression de la sédimentation")
        context = render_sedimentation_progress(sedimentation_manager, project_id)
        
        # Affichage des métriques de qualité de sédimentation
        transition_data = context.global_metadata.get('transition_data', {}) if hasattr(context, 'global_metadata') else {}
        if transition_data:
            render_sedimentation_data_flow(context, transition_data)

    # Onglets de finalisation enrichis
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📖 Aperçu & Amélioration", 
        "🔍 Contrôle qualité", 
        "📊 Analyse de densité",
        "📤 Export avancé", 
        "🎯 Suggestions IA"
    ])

    with tab1:
        render_document_improvement_tab(project, project_context, project_id)

    with tab2:
        render_quality_control_tab(project, sections, sedimentation_manager, project_id)

    with tab3:
        render_density_analysis_tab(project, sections)

    with tab4:
        render_advanced_export_tab(project, sections, project_id)

    with tab5:
        render_ai_suggestions_tab(project, sections, project_context, project_id)

    # Boutons de navigation
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅️ Retour à la révision"):
            st.session_state.page = "revision"
            st.rerun()

    with col2:
        if st.button("🔄 Sauvegarder état"):
            project_context.update_project_metadata(project_id)
            history_manager.save_version(
                project_id=project_id,
                project_data=project_context.load_project(project_id),
                description="Sauvegarde étape finalisation"
            )
            st.success("État sauvegardé !")

    with col3:
        if st.button("✅ Terminer le projet"):
            # Mise à jour du statut du projet
            project_context.update_project_status(project_id, "completed")

            # Sauvegarde finale dans l'historique
            project_data = project_context.load_project(project_id)
            history_manager.save_version(
                project_id=project_id,
                project_data=project_data,
                description="Finalisation complète du projet"
            )

            st.success("🎉 Projet terminé avec succès!")
            
            # Affichage des statistiques finales
            display_completion_stats(project_data)

            # Redirection vers la page du projet
            if st.button("🏠 Retour à l'accueil"):
                st.session_state.page = "project_overview"
                st.rerun()

def render_document_improvement_tab(project, project_context, project_id):
    """Onglet d'amélioration du document avec IA ligne par ligne."""
    st.subheader("📖 Aperçu et amélioration du document")
    
    sections = project.get("sections", [])
    preferences = project.get("preferences", {})
    
    if not sections:
        st.warning("Ce projet ne contient aucune section.")
        return

    # Construction du texte complet
    full_text = ""
    for section in sections:
        full_text += f"# {section.get('title', 'Sans titre')}\n\n"
        full_text += section.get("content", "") + "\n\n"

    # Aperçu du document complet
    with st.expander("📋 Aperçu du document complet", expanded=False):
        st.text_area("Document assemblé", value=full_text.strip(), height=300, disabled=True)

    # Section d'amélioration IA ligne par ligne
    st.markdown("### 🧠 Amélioration IA ligne par ligne")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        improve_style = st.selectbox(
            "Style d'amélioration",
            ["Standard", "Académique", "CRÉSUS-NAKAMOTO", "AcademicWritingCrypto"],
            index=0
        )
    with col2:
        auto_apply = st.checkbox("Appliquer automatiquement les améliorations", value=False)

    if st.button("🚀 Lancer l'amélioration IA"):
        with st.spinner("Amélioration IA en cours..."):
            improved_document = improve_document_with_ai(
                full_text, improve_style, preferences, auto_apply
            )
            
            if auto_apply:
                # Mise à jour des sections avec le texte amélioré
                update_sections_with_improved_text(
                    project_context, project_id, sections, improved_document
                )
                st.success("✅ Document amélioré et mis à jour automatiquement!")
                st.rerun()
            else:
                # Affichage du texte amélioré pour validation
                st.markdown("### 📝 Version améliorée (pour validation)")
                st.text_area("Document amélioré", value=improved_document, height=400)
                
                if st.button("✅ Appliquer les améliorations"):
                    update_sections_with_improved_text(
                        project_context, project_id, sections, improved_document
                    )
                    st.success("✅ Améliorations appliquées!")
                    st.rerun()

def render_quality_control_tab(project, sections, sedimentation_manager, project_id):
    """Onglet de contrôle qualité avancé."""
    st.subheader("🔍 Contrôle qualité avancé")

    # Vérifications automatiques avec IA
    checks = [
        {
            "name": "Cohérence globale",
            "description": "Vérification de la logique argumentative",
            "prompt": "Analyse la cohérence globale de ce document académique"
        },
        {
            "name": "Structure narrative",
            "description": "Évaluation de la progression logique",
            "prompt": "Évalue la structure narrative et la progression des idées"
        },
        {
            "name": "Citations et références",
            "description": "Contrôle des citations académiques",
            "prompt": "Vérifie la qualité et pertinence des citations"
        },
        {
            "name": "Style et registre",
            "description": "Uniformité du style académique",
            "prompt": "Analyse l'uniformité du style et du registre académique"
        }
    ]

    st.markdown("### 🤖 Vérifications automatiques avec IA")
    
    for check in checks:
        with st.expander(f"🔍 {check['name']}", expanded=False):
            st.write(check["description"])
            
            if st.button(f"Analyser", key=f"check_{check['name'].replace(' ', '_')}"):
                with st.spinner(f"Analyse de {check['name']} en cours..."):
                    full_text = get_full_document_text(sections)
                    
                    analysis = call_ai_safe(
                        prompt=f"{check['prompt']}:\n\n{full_text[:3000]}...",
                        max_tokens=800,
                        temperature=0.3
                    )
                    
                    st.markdown("**Résultat de l'analyse:**")
                    st.write(analysis.get("text", "Erreur dans l'analyse"))

    # Statistiques avancées du document
    st.markdown("### 📊 Métriques de qualité")
    
    if sections:
        display_advanced_document_metrics(sections)

    # Intégration avec la sédimentation
    if sedimentation_manager:
        st.markdown("### 🌱 Qualité de la sédimentation")
        display_sedimentation_quality_metrics(sedimentation_manager, project_id)

def render_density_analysis_tab(project, sections):
    """Onglet d'analyse de densité du contenu."""
    st.subheader("📊 Analyse de densité du contenu")
    
    if not sections:
        st.warning("Aucune section à analyser.")
        return

    # Calcul des métriques de densité
    density_metrics = calculate_content_density(sections)
    
    # Visualisation des métriques
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Densité par section")
        if HAS_PANDAS:
            df_density = pd.DataFrame([
                {
                    "Section": section.get("title", "Sans titre"),
                    "Mots": len(section.get("content", "").split()),
                    "Phrases": section.get("content", "").count('.'),
                    "Densité": len(section.get("content", "").split()) / max(1, section.get("content", "").count('.'))
                }
                for section in sections
            ])
            st.dataframe(df_density)
        
    with col2:
        st.markdown("#### 🎯 Recommandations")
        for section in sections:
            word_count = len(section.get("content", "").split())
            if word_count < 100:
                st.warning(f"Section '{section.get('title', 'Sans titre')}' : Contenu insuffisant ({word_count} mots)")
            elif word_count > 1000:
                st.info(f"Section '{section.get('title', 'Sans titre')}' : Section longue ({word_count} mots)")

def render_advanced_export_tab(project, sections, project_id):
    """Onglet d'export avancé multi-format."""
    st.subheader("📤 Export avancé du document")

    # Options d'export
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox(
            "Format d'export",
            ["Markdown", "PDF (via HTML)", "Word (simulé)", "HTML", "LaTeX", "JSON complet"]
        )
        
        include_metadata = st.checkbox("Inclure les métadonnées", value=True)
        
    with col2:
        include_history = st.checkbox("Inclure l'historique de révision", value=False)
        include_stats = st.checkbox("Inclure les statistiques", value=True)

    # Aperçu du format d'export
    st.markdown("### 👀 Aperçu de l'export")
    
    if export_format == "Markdown":
        preview = generate_markdown_export(project, sections, include_metadata, include_stats)
        st.code(preview[:1000] + "..." if len(preview) > 1000 else preview, language="markdown")
    
    elif export_format == "HTML":
        preview = generate_html_export(project, sections, include_metadata)
        st.code(preview[:1000] + "..." if len(preview) > 1000 else preview, language="html")
    
    elif export_format == "LaTeX":
        preview = generate_latex_export(project, sections, include_metadata)
        st.code(preview[:1000] + "..." if len(preview) > 1000 else preview, language="latex")

    # Bouton d'export
    if st.button("📥 Générer et télécharger"):
        with st.spinner("Génération du document..."):
            exported_content = generate_export_content(
                project, sections, export_format, include_metadata, include_stats, include_history
            )
            
            file_extension = get_file_extension(export_format)
            filename = f"{project.get('title', 'document').replace(' ', '_')}{file_extension}"
            
            st.download_button(
                label=f"💾 Télécharger {export_format}",
                data=exported_content,
                file_name=filename,
                mime=get_mime_type(export_format)
            )

def render_ai_suggestions_tab(project, sections, project_context, project_id):
    """Onglet de suggestions IA avancées."""
    st.subheader("🎯 Suggestions IA personnalisées")
    
    if not sections:
        st.warning("Aucune section pour générer des suggestions.")
        return

    # Types de suggestions
    suggestion_types = [
        "Amélioration stylistique",
        "Enrichissement du contenu",
        "Restructuration",
        "Citations supplémentaires",
        "Conclusion plus forte"
    ]
    
    selected_suggestions = st.multiselect(
        "Types de suggestions souhaitées",
        suggestion_types,
        default=["Amélioration stylistique", "Enrichissement du contenu"]
    )
    
    if st.button("🧠 Générer les suggestions"):
        with st.spinner("Génération des suggestions IA..."):
            full_text = get_full_document_text(sections)
            
            for suggestion_type in selected_suggestions:
                with st.expander(f"💡 {suggestion_type}", expanded=True):
                    suggestion = generate_ai_suggestion(full_text, suggestion_type, project.get("preferences", {}))
                    st.write(suggestion.get("text", "Erreur dans la génération"))

# Fonctions utilitaires

def improve_document_with_ai(full_text: str, style: str, preferences: Dict, auto_apply: bool = False) -> str:
    """Améliore le document ligne par ligne avec l'IA."""
    lines = full_text.strip().split("\n")
    improved_lines = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, line in enumerate(lines):
        progress_bar.progress((i + 1) / len(lines))
        status_text.text(f"Amélioration ligne {i + 1}/{len(lines)}")
        
        if line.strip() == "" or line.startswith("#"):
            improved_lines.append(line)
            continue
            
        response = call_ai_safe(
            prompt=f"Améliore cette phrase pour plus de clarté et un style {style.lower()} :\n\n{line.strip()}",
            max_tokens=250,
            temperature=0.6,
            use_cache=True
        )
        
        improved_line = response.get("text", line).strip()
        improved_lines.append(improved_line)
    
    progress_bar.empty()
    status_text.empty()
    
    return "\n".join(improved_lines)

def update_sections_with_improved_text(project_context, project_id, sections, improved_text):
    """Met à jour les sections avec le texte amélioré."""
    improved_sections = parse_improved_text_to_sections(improved_text)
    
    for i, section in enumerate(sections):
        if i < len(improved_sections):
            project_context.update_section(
                project_id=project_id,
                section_id=section["section_id"],
                content=improved_sections[i]["content"]
            )

def get_full_document_text(sections: List[Dict]) -> str:
    """Récupère le texte complet du document."""
    full_text = ""
    for section in sections:
        full_text += f"# {section.get('title', 'Sans titre')}\n\n"
        full_text += section.get("content", "") + "\n\n"
    return full_text

def display_advanced_document_metrics(sections: List[Dict]):
    """Affiche les métriques avancées du document."""
    total_words = sum(len(section.get("content", "").split()) for section in sections)
    total_sentences = sum(section.get("content", "").count('.') for section in sections)
    total_paragraphs = sum(section.get("content", "").count('\n\n') for section in sections)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Mots totaux", total_words)
    with col2:
        st.metric("Phrases", total_sentences)
    with col3:
        st.metric("Paragraphes", total_paragraphs)
    with col4:
        avg_words_per_sentence = total_words / max(1, total_sentences)
        st.metric("Mots/phrase", f"{avg_words_per_sentence:.1f}")

def calculate_content_density(sections: List[Dict]) -> Dict:
    """Calcule les métriques de densité du contenu."""
    return {
        "total_sections": len(sections),
        "average_words_per_section": sum(len(s.get("content", "").split()) for s in sections) / len(sections),
        "content_distribution": [len(s.get("content", "").split()) for s in sections]
    }

def generate_markdown_export(project, sections, include_metadata, include_stats):
    """Génère l'export Markdown."""
    content = f"# {project.get('title', 'Document')}\n\n"
    
    if include_metadata:
        content += f"**Description:** {project.get('description', '')}\n\n"
        content += f"**Date de création:** {project.get('created_date', '')}\n\n"
    
    for section in sections:
        content += f"## {section.get('title', 'Section')}\n\n"
        content += f"{section.get('content', '')}\n\n"
    
    if include_stats:
        total_words = sum(len(s.get("content", "").split()) for s in sections)
        content += f"\n---\n**Statistiques:** {total_words} mots, {len(sections)} sections\n"
    
    return content

def generate_html_export(project, sections, include_metadata):
    """Génère l'export HTML."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{project.get('title', 'Document')}</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>{project.get('title', 'Document')}</h1>
"""
    
    if include_metadata:
        html += f"    <p><strong>Description:</strong> {project.get('description', '')}</p>\n"
    
    for section in sections:
        html += f"    <h2>{section.get('title', 'Section')}</h2>\n"
        html += f"    <div>{section.get('content', '').replace(chr(10), '<br>')}</div>\n"
    
    html += "</body>\n</html>"
    return html

def generate_latex_export(project, sections, include_metadata):
    """Génère l'export LaTeX."""
    latex = f"""\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\title{{{project.get('title', 'Document')}}}
\\begin{{document}}
\\maketitle
"""
    
    for section in sections:
        latex += f"\\section{{{section.get('title', 'Section')}}}\n"
        latex += f"{section.get('content', '')}\n\n"
    
    latex += "\\end{document}"
    return latex

def generate_export_content(project, sections, export_format, include_metadata, include_stats, include_history):
    """Génère le contenu d'export selon le format."""
    if export_format == "Markdown":
        return generate_markdown_export(project, sections, include_metadata, include_stats)
    elif export_format == "HTML":
        return generate_html_export(project, sections, include_metadata)
    elif export_format == "LaTeX":
        return generate_latex_export(project, sections, include_metadata)
    elif export_format == "JSON complet":
        return json.dumps(project, indent=2, ensure_ascii=False)
    else:
        return generate_markdown_export(project, sections, include_metadata, include_stats)

def get_file_extension(export_format):
    """Retourne l'extension de fichier selon le format."""
    extensions = {
        "Markdown": ".md",
        "HTML": ".html",
        "LaTeX": ".tex",
        "JSON complet": ".json",
        "PDF (via HTML)": ".html",
        "Word (simulé)": ".html"
    }
    return extensions.get(export_format, ".txt")

def get_mime_type(export_format):
    """Retourne le type MIME selon le format."""
    mime_types = {
        "Markdown": "text/markdown",
        "HTML": "text/html",
        "LaTeX": "text/plain",
        "JSON complet": "application/json"
    }
    return mime_types.get(export_format, "text/plain")

def generate_ai_suggestion(full_text, suggestion_type, preferences):
    """Génère une suggestion IA selon le type."""
    prompts = {
        "Amélioration stylistique": "Suggère 3 améliorations stylistiques pour ce document académique",
        "Enrichissement du contenu": "Identifie 3 points où le contenu pourrait être enrichi ou développé",
        "Restructuration": "Propose une restructuration alternative pour améliorer la logique",
        "Citations supplémentaires": "Suggère où ajouter des citations pour renforcer l'argumentation",
        "Conclusion plus forte": "Propose une conclusion plus percutante basée sur le développement"
    }
    
    prompt = f"{prompts.get(suggestion_type, 'Analyse ce document')}:\n\n{full_text[:2000]}..."
    
    return call_ai_safe(
        prompt=prompt,
        max_tokens=600,
        temperature=0.7
    )

def parse_improved_text_to_sections(improved_text):
    """Parse le texte amélioré en sections."""
    sections = []
    current_section = {"title": "", "content": ""}
    
    for line in improved_text.split("\n"):
        if line.startswith("# "):
            if current_section["content"]:
                sections.append(current_section)
            current_section = {"title": line[2:], "content": ""}
        else:
            current_section["content"] += line + "\n"
    
    if current_section["content"]:
        sections.append(current_section)
    
    return sections

def display_completion_stats(project_data):
    """Affiche les statistiques de complétion du projet."""
    sections = project_data.get("sections", [])
    total_words = sum(len(s.get("content", "").split()) for s in sections)
    
    st.balloons()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Sections complétées", len(sections))
    with col2:
        st.metric("📊 Mots totaux", total_words)
    with col3:
        st.metric("⏱️ Durée", "Calculé automatiquement")

def display_sedimentation_quality_metrics(sedimentation_manager, project_id):
    """Affiche les métriques de qualité de la sédimentation."""
    try:
        if hasattr(sedimentation_manager, 'get_project_quality_metrics'):
            metrics = sedimentation_manager.get_project_quality_metrics(project_id)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Richesse contextuelle", f"{metrics.get('context_richness', 0):.1f}%")
            with col2:
                st.metric("Cohérence narrative", f"{metrics.get('narrative_coherence', 0):.1f}%")
    except Exception as e:
        st.info("Métriques de sédimentation non disponibles")
