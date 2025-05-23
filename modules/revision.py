def render_revision(project_id, project_context, history_manager, adaptive_engine):
    """
    Affiche l'interface de révision pour un projet.
    
    Args:
        project_id: ID du projet
        project_context: Instance de ProjectContext
        history_manager: Instance de HistoryManager
        adaptive_engine: Instance de AdaptiveEngine
    """
    import streamlit as st
    from utils.ai_service import generate_academic_text
    import re
    
    # Chargement des données du projet
    project = project_context.load_project(project_id)
    
    # Récupération des sections
    sections = project.get("sections", [])
    
    # Vérification qu'il y a des sections
    if not sections:
        st.warning("Aucune section n'a été créée. Veuillez d'abord créer des sections dans le storyboard.")
        
        if st.button("Retour au storyboard"):
            st.session_state.page = "storyboard"
            st.rerun()
        
        return
    
    # Récupération de la section actuelle
    current_section_id = st.session_state.get("current_section_id")
    
    # Si aucune section n'est sélectionnée, prendre la première
    if not current_section_id and sections:
        current_section_id = sections[0].get("section_id", "")
        st.session_state.current_section_id = current_section_id
    
    # Recherche de la section actuelle
    current_section = None
    current_section_index = 0
    
    for i, section in enumerate(sections):
        if section.get("section_id", "") == current_section_id:
            current_section = section
            current_section_index = i
            break
    
    # Vérification que la section existe
    if not current_section:
        st.warning("La section sélectionnée n'existe pas.")
        
        if st.button("Retour au storyboard"):
            st.session_state.page = "storyboard"
            st.rerun()
        
        return
    
    # Affichage du titre du projet et de la section
    st.title(f"Révision: {project.get('title', 'Sans titre')}")
    st.subheader(f"Section: {current_section.get('title', 'Sans titre')}")
    
    # Affichage de la structure existante si présente
    existing_structure = project.get("existing_structure", "")
    if existing_structure:
        with st.expander("Structure du document"):
            st.text(existing_structure)
            
            # Mise en évidence de la section actuelle dans la structure
            section_title = current_section.get("title", "")
            if section_title in existing_structure:
                st.info(f"Section actuelle: {section_title}")
    
    # Récupération du contenu actuel
    current_content = current_section.get("content", "")
    
    # Vérification que la section a du contenu
    if not current_content:
        st.warning("Cette section n'a pas de contenu. Veuillez d'abord rédiger du contenu.")
        
        if st.button("Aller à la rédaction"):
            st.session_state.page = "redaction"
            st.rerun()
        
        return
    
    # Division du contenu en paragraphes
    paragraphs = re.split(r'\n\s*\n', current_content)
    
    # Sélection du mode de révision
    revision_mode = st.radio(
        "Mode de révision",
        ["Par paragraphe", "Section complète"],
        horizontal=True
    )
    
    if revision_mode == "Par paragraphe":
        # Sélection du paragraphe à réviser
        paragraph_index = st.session_state.get("paragraph_index", 0)
        
        # Vérification que l'index est valide
        if paragraph_index >= len(paragraphs):
            paragraph_index = 0
            st.session_state.paragraph_index = 0
        
        # Navigation entre les paragraphes
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            if paragraph_index > 0:
                if st.button("← Paragraphe précédent"):
                    st.session_state.paragraph_index = paragraph_index - 1
                    st.rerun()
        
        with col2:
            st.write(f"Paragraphe {paragraph_index + 1} sur {len(paragraphs)}")
        
        with col3:
            if paragraph_index < len(paragraphs) - 1:
                if st.button("Paragraphe suivant →"):
                    st.session_state.paragraph_index = paragraph_index + 1
                    st.rerun()
        
        # Affichage du paragraphe actuel
        st.markdown("---")
        st.subheader("Paragraphe à réviser")
        
        current_paragraph = paragraphs[paragraph_index]
        
        # Champ d'édition du paragraphe
        new_paragraph = st.text_area(
            "Contenu du paragraphe",
            value=current_paragraph,
            height=200
        )
        
        # Analyse de densité qualitative du paragraphe
        st.markdown("---")
        st.subheader("Analyse de densité qualitative")
        
        try:
            from modules.density_analyzer import render_density_analysis
            render_density_analysis(new_paragraph, project_context, project_id)
        except ImportError:
            st.info("Le module d'analyse de densité qualitative n'est pas disponible. Veuillez installer les modules d'analyse de densité.")
        
        # Options de révision assistée
        st.markdown("---")
        st.subheader("Révision assistée")
        
        revision_options = st.multiselect(
            "Options de révision",
            [
                "Améliorer la clarté",
                "Renforcer l'argumentation",
                "Ajouter des connecteurs logiques",
                "Enrichir le vocabulaire académique",
                "Corriger la grammaire et l'orthographe",
                "Améliorer la structure des phrases",
                "Densifier le contenu"
            ],
            default=["Améliorer la clarté", "Renforcer l'argumentation"]
        )
        
        # Construction du prompt de révision
        revision_prompt = f"Réviser le paragraphe suivant en {', '.join(revision_options).lower()}:\n\n{current_paragraph}"
        
        if st.button("Générer une révision"):
            with st.spinner("Génération de la révision en cours..."):
                result = generate_academic_text(
                    prompt=revision_prompt,
                    style=project.get("preferences", {}).get("style", "Académique"),
                    length=len(current_paragraph.split())
                )
                
                revised_paragraph = result.get("text", "")
                
                if revised_paragraph:
                    st.session_state.revised_paragraph = revised_paragraph
                    st.success("Révision générée avec succès!")
                    st.rerun()
                else:
                    st.error("Erreur lors de la génération de la révision.")
        
        # Affichage de la révision générée
        if hasattr(st.session_state, 'revised_paragraph'):
            st.markdown("---")
            st.subheader("Révision proposée")
            
            st.markdown(st.session_state.revised_paragraph)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Accepter cette révision"):
                    # Mise à jour du paragraphe
                    paragraphs[paragraph_index] = st.session_state.revised_paragraph
                    
                    # Reconstruction du contenu
                    new_content = "\n\n".join(paragraphs)
                    
                    # Mise à jour de la section
                    current_section["content"] = new_content
                    
                    # Sauvegarde du projet
                    project_context.update_section(project_id, current_section_id, current_section)
                    
                    # Mise à jour des métadonnées
                    project_context.update_project_metadata(project_id)
                    
                    # Mise à jour du statut du projet
                    if project.get("status") == "redaction_in_progress":
                        project_context.update_project_status(project_id, "revision_in_progress")
                    
                    # Sauvegarde de la version dans l'historique
                    project_data = project_context.load_project(project_id)
                    history_manager.save_version(
                        project_id=project_id,
                        project_data=project_data,
                        description=f"Révision du paragraphe {paragraph_index + 1} de la section: {current_section.get('title', 'Sans titre')}"
                    )
                    
                    # Suppression de la révision de la session
                    del st.session_state.revised_paragraph
                    
                    st.success("Révision acceptée avec succès!")
                    st.rerun()
            
            with col2:
                if st.button("Rejeter cette révision"):
                    # Suppression de la révision de la session
                    del st.session_state.revised_paragraph
                    st.rerun()
        
        # Bouton d'enregistrement manuel
        st.markdown("---")
        if st.button("Enregistrer les modifications"):
            # Mise à jour du paragraphe
            paragraphs[paragraph_index] = new_paragraph
            
            # Reconstruction du contenu
            new_content = "\n\n".join(paragraphs)
            
            # Mise à jour de la section
            current_section["content"] = new_content
            
            # Sauvegarde du projet
            project_context.update_section(project_id, current_section_id, current_section)
            
            # Mise à jour des métadonnées
            project_context.update_project_metadata(project_id)
            
            # Mise à jour du statut du projet
            if project.get("status") == "redaction_in_progress":
                project_context.update_project_status(project_id, "revision_in_progress")
            
            # Sauvegarde de la version dans l'historique
            project_data = project_context.load_project(project_id)
            history_manager.save_version(
                project_id=project_id,
                project_data=project_data,
                description=f"Modification manuelle du paragraphe {paragraph_index + 1} de la section: {current_section.get('title', 'Sans titre')}"
            )
            
            st.success("Modifications enregistrées avec succès!")
            st.rerun()
    
    else:  # Mode "Section complète"
        # Affichage de la section complète
        st.markdown("---")
        st.subheader("Section complète")
        
        # Champ d'édition du contenu
        new_content = st.text_area(
            "Contenu de la section",
            value=current_content,
            height=500
        )
        
        # Analyse de densité qualitative de la section
        st.markdown("---")
        st.subheader("Analyse de densité qualitative")
        
        try:
            from modules.density_analyzer import render_density_analysis
            render_density_analysis(new_content, project_context, project_id)
        except ImportError:
            st.info("Le module d'analyse de densité qualitative n'est pas disponible. Veuillez installer les modules d'analyse de densité.")
        
        # Options de révision assistée
        st.markdown("---")
        st.subheader("Révision assistée")
        
        revision_options = st.multiselect(
            "Options de révision",
            [
                "Améliorer la clarté",
                "Renforcer l'argumentation",
                "Ajouter des connecteurs logiques",
                "Enrichir le vocabulaire académique",
                "Corriger la grammaire et l'orthographe",
                "Améliorer la structure des phrases",
                "Densifier le contenu"
            ],
            default=["Améliorer la clarté", "Renforcer l'argumentation"]
        )
        
        # Construction du prompt de révision
        revision_prompt = f"Réviser la section suivante en {', '.join(revision_options).lower()}:\n\n{current_content}"
        
        if st.button("Générer une révision"):
            with st.spinner("Génération de la révision en cours..."):
                result = generate_academic_text(
                    prompt=revision_prompt,
                    style=project.get("preferences", {}).get("style", "Académique"),
                    length=len(current_content.split())
                )
                
                revised_content = result.get("text", "")
                
                if revised_content:
                    st.session_state.revised_content = revised_content
                    st.success("Révision générée avec succès!")
                    st.rerun()
                else:
                    st.error("Erreur lors de la génération de la révision.")
        
        # Affichage de la révision générée
        if hasattr(st.session_state, 'revised_content'):
            st.markdown("---")
            st.subheader("Révision proposée")
            
            st.markdown(st.session_state.revised_content)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Accepter cette révision"):
                    # Mise à jour du contenu
                    current_section["content"] = st.session_state.revised_content
                    
                    # Sauvegarde du projet
                    project_context.update_section(project_id, current_section_id, current_section)
                    
                    # Mise à jour des métadonnées
                    project_context.update_project_metadata(project_id)
                    
                    # Mise à jour du statut du projet
                    if project.get("status") == "redaction_in_progress":
                        project_context.update_project_status(project_id, "revision_in_progress")
                    
                    # Sauvegarde de la version dans l'historique
                    project_data = project_context.load_project(project_id)
                    history_manager.save_version(
                        project_id=project_id,
                        project_data=project_data,
                        description=f"Révision complète de la section: {current_section.get('title', 'Sans titre')}"
                    )
                    
                    # Suppression de la révision de la session
                    del st.session_state.revised_content
                    
                    st.success("Révision acceptée avec succès!")
                    st.rerun()
            
            with col2:
                if st.button("Rejeter cette révision"):
                    # Suppression de la révision de la session
                    del st.session_state.revised_content
                    st.rerun()
        
        # Bouton d'enregistrement manuel
        st.markdown("---")
        if st.button("Enregistrer les modifications"):
            # Mise à jour du contenu
            current_section["content"] = new_content
            
            # Sauvegarde du projet
            project_context.update_section(project_id, current_section_id, current_section)
            
            # Mise à jour des métadonnées
            project_context.update_project_metadata(project_id)
            
            # Mise à jour du statut du projet
            if project.get("status") == "redaction_in_progress":
                project_context.update_project_status(project_id, "revision_in_progress")
            
            # Sauvegarde de la version dans l'historique
            project_data = project_context.load_project(project_id)
            history_manager.save_version(
                project_id=project_id,
                project_data=project_data,
                description=f"Modification manuelle de la section: {current_section.get('title', 'Sans titre')}"
            )
            
            st.success("Modifications enregistrées avec succès!")
            st.rerun()
    
    # Navigation entre les sections
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if current_section_index > 0:
            if st.button("← Section précédente"):
                st.session_state.current_section_id = sections[current_section_index - 1].get("section_id", "")
                st.rerun()
    
    with col2:
        if st.button("Retour à la rédaction"):
            st.session_state.page = "redaction"
            st.rerun()
    
    with col3:
        if current_section_index < len(sections) - 1:
            if st.button("Section suivante →"):
                st.session_state.current_section_id = sections[current_section_index + 1].get("section_id", "")
                st.rerun()
    
    # Boutons de visualisation du document et de la timeline
    st.markdown("---")
    preview_col1, preview_col2 = st.columns(2)
    
    with preview_col1:
        if st.button("📄 Prévisualiser le document complet"):
            st.session_state.previous_page = st.session_state.page
            st.session_state.page = "document_preview"
            st.rerun()
    
    with preview_col2:
        if st.button("📊 Voir l'évolution du document"):
            st.session_state.previous_page = st.session_state.page
            st.session_state.page = "document_timeline"
            st.rerun()
    
    # Bouton pour passer à la finalisation
    st.markdown("---")
    if st.button("Passer à la finalisation"):
        # Mise à jour du statut du projet
        project_context.update_project_status(project_id, "revision_complete")
        
        # Sauvegarde de la version dans l'historique
        project_data = project_context.load_project(project_id)
        history_manager.save_version(
            project_id=project_id,
            project_data=project_data,
            description="Révision terminée"
        )
        
        st.session_state.page = "finalisation"
        st.rerun()
    
    return

