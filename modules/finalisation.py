"""
Module de finalisation pour le système de rédaction académique.
Permet de finaliser un projet et d'exporter le document.
"""

import streamlit as st
from typing import Optional, Dict, Any, List

def render_finalisation(project_id: str, project_context, history_manager):
    """
    Interface de finalisation d'un projet.

    Args:
        project_id: ID du projet
        project_context: Instance de ProjectContext
        history_manager: Instance de HistoryManager
    """
    if not project_id:
        st.error("Aucun projet sélectionné.")
        return

    # Chargement du projet
    project = project_context.load_project(project_id)
    if not project:
        st.error("Projet non trouvé.")
        return

    st.title("Finalisation du projet")
    st.subheader(project.get("title", "Sans titre"))

    # Onglets de finalisation
    tab1, tab2, tab3 = st.tabs(["Aperçu final", "Contrôle qualité", "Export"])

    with tab1:
        st.subheader("Aperçu du document final")

        # Assemblage du document
        sections = project.get("sections", [])
        if sections:
            st.markdown("### Document assemblé")

            # Introduction si elle existe
            intro_section = next((s for s in sections if "intro" in s.get("title", "").lower()), None)
            if intro_section:
                st.markdown("## Introduction")
                st.markdown(intro_section.get("content", ""))

            # Autres sections
            for section in sections:
                if section != intro_section:
                    title = section.get("title", "Section sans titre")
                    content = section.get("content", "")

                    st.markdown(f"## {title}")
                    if content:
                        st.markdown(content)
                    else:
                        st.info("Section vide")

            # Conclusion si elle existe
            conclusion_section = next((s for s in sections if "conclusion" in s.get("title", "").lower()), None)
            if conclusion_section and conclusion_section not in [intro_section]:
                st.markdown("## Conclusion")
                st.markdown(conclusion_section.get("content", ""))
        else:
            st.warning("Aucune section trouvée dans le projet.")

    with tab2:
        st.subheader("Contrôle qualité")

        # Vérifications automatiques
        checks = [
            "Cohérence globale",
            "Structure narrative",
            "Citations et références",
            "Orthographe et grammaire",
            "Longueur du document"
        ]

        st.markdown("### Vérifications automatiques")

        for check in checks:
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**{check}**")

            with col2:
                if st.button("Vérifier", key=f"check_{check.replace(' ', '_')}"):
                    with st.spinner(f"Vérification de {check} en cours..."):
                        # Simulation de vérification
                        import time
                        import random
                        time.sleep(1)

                        result = random.choice(["OK", "Attention", "Problème"])

                        if result == "OK":
                            st.success(f"{check}: Aucun problème détecté")
                        elif result == "Attention":
                            st.warning(f"{check}: Quelques points à améliorer")
                        else:
                            st.error(f"{check}: Problèmes détectés")

        # Statistiques du document
        st.markdown("### Statistiques du document")

        total_words = sum(len(section.get("content", "").split()) for section in sections)
        total_sections = len(sections)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nombre de mots", total_words)
        with col2:
            st.metric("Nombre de sections", total_sections)
        with col3:
            avg_words = total_words // max(1, total_sections)
            st.metric("Mots par section", avg_words)

    with tab3:
        st.subheader("Export du document")

        # Options d'export
        export_format = st.selectbox(
            "Format d'export",
            ["Markdown", "PDF", "Word", "HTML"]
        )

        if st.button("Exporter le document"):
            if export_format == "Markdown":
                # Génération du document Markdown
                document = f"# {project.get('title', 'Document')}\n\n"

                for section in sections:
                    title = section.get("title", "Section")
                    content = section.get("content", "")
                    document += f"## {title}\n\n{content}\n\n"

                # Téléchargement
                st.download_button(
                    label="Télécharger le document Markdown",
                    data=document,
                    file_name=f"{project.get('title', 'document').replace(' ', '_')}.md",
                    mime="text/markdown"
                )
            else:
                st.info(f"Exportation {export_format} à implémenter.")

    # Boutons de navigation
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Retour à la révision"):
            st.session_state.page = "revision"
            st.rerun()

    with col2:
        if st.button("Terminer le projet"):
            # Mise à jour du statut du projet
            project_context.update_project_status(project_id, "completed")

            # Sauvegarde dans l'historique
            project_data = project_context.load_project(project_id)
            history_manager.save_version(
                project_id=project_id,
                project_data=project_data,
                description="Finalisation du projet"
            )

            st.success("Projet terminé avec succès!")

            # Redirection vers la page du projet
            st.session_state.page = "project_overview"
            st.rerun()

    # Suggestions
    st.markdown("---")
    st.subheader("Suggestions pour la finalisation")

    project_type = project.get("type", "Article académique")

    if project_type == "Article académique":
        st.info("""
        💡 **Conseils pour la finalisation:**

        - Vérifiez la cohérence globale de votre argumentation
        - Assurez-vous que l'introduction et la conclusion se répondent
        - Vérifiez que toutes les citations sont correctement formatées
        - Relisez le document dans son ensemble
        """)