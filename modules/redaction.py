def render_redaction(project_id, project_context, history_manager, adaptive_engine):
    """
    Affiche l'interface de rédaction pour un projet.
    
    Args:
        project_id: ID du projet
        project_context: Instance de ProjectContext
        history_manager: Instance de HistoryManager
        adaptive_engine: Instance de AdaptiveEngine
    """
    import streamlit as st
    from utils.ai_service import generate_academic_text
    
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
    st.title(f"Rédaction: {project.get('title', 'Sans titre')}")
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
    
    # Création de deux colonnes pour l'interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Récupération du contenu actuel
        current_content = current_section.get("content", "")
        
        # Champ d'édition du contenu
        new_content = st.text_area(
            "Contenu de la section",
            value=current_content,
            height=500
        )
        
        # Bouton d'enregistrement
        if st.button("Enregistrer"):
            # Mise à jour du contenu
            current_section["content"] = new_content
            
            # Sauvegarde du projet
            project_context.update_section(project_id, current_section_id, current_section)
            
            # Mise à jour des métadonnées
            project_context.update_project_metadata(project_id)
            
            # Mise à jour du statut du projet
            if project.get("status") == "storyboard_ready":
                project_context.update_project_status(project_id, "redaction_in_progress")
            
            # Sauvegarde de la version dans l'historique
            project_data = project_context.load_project(project_id)
            history_manager.save_version(
                project_id=project_id,
                project_data=project_data,
                description=f"Mise à jour de la section: {current_section.get('title', 'Sans titre')}"
            )
            
            st.success("Contenu enregistré avec succès!")
    
    with col2:
        # Affichage des éléments du storyboard
        st.subheader("Éléments du storyboard")
        
        # Récupération des thèses et citations associées à cette section
        theses = current_section.get("theses", [])
        
        if theses:
            for i, thesis in enumerate(theses):
                with st.expander(f"Thèse {i+1}"):
                    st.write(thesis.get("content", ""))
                    
                    # Affichage des citations
                    citations = thesis.get("citations", [])
                    
                    if citations:
                        st.write("Citations associées:")
                        
                        for j, citation in enumerate(citations):
                            st.markdown(f"*\"{citation}\"*")
                            
                            if st.button(f"Insérer cette citation", key=f"citation_{i}_{j}"):
                                # Ajout de la citation au contenu
                                if new_content:
                                    new_content += f"\n\n> {citation}\n\n"
                                else:
                                    new_content = f"> {citation}\n\n"
                                
                                st.session_state.new_content = new_content
                                st.rerun()
        else:
            st.info("Aucune thèse n'est associée à cette section.")
        
        # Génération assistée
        st.markdown("---")
        st.subheader("Génération assistée")
        
        # Construction du prompt à partir des thèses
        default_prompt = ""
        if theses:
            default_prompt = "Rédiger une section académique sur les points suivants:\n\n"
            for i, thesis in enumerate(theses):
                default_prompt += f"{i+1}. {thesis.get('content', '')}\n"
        
        prompt = st.text_area(
            "Prompt pour la génération",
            value=default_prompt,
            height=150
        )
        
        style = st.selectbox(
            "Style d'écriture",
            ["Standard", "Académique", "CRÉSUS-NAKAMOTO", "AcademicWritingCrypto"],
            index=["Standard", "Académique", "CRÉSUS-NAKAMOTO", "AcademicWritingCrypto"].index(
                project.get("preferences", {}).get("style", "Standard")
            )
        )
        
        length = st.slider(
            "Longueur approximative (mots)",
            min_value=100,
            max_value=1000,
            value=300,
            step=100
        )
        
        if st.button("Générer"):
            with st.spinner("Génération en cours..."):
                result = generate_academic_text(
                    prompt=prompt,
                    style=style,
                    length=length
                )
                
                generated_content = result.get("text", "")
                
                if generated_content:
                    st.session_state.generated_content = generated_content
                    st.success("Contenu généré avec succès!")
                    st.rerun()
                else:
                    st.error("Erreur lors de la génération du contenu.")
        
        # Affichage du contenu généré
        if hasattr(st.session_state, 'generated_content'):
            st.markdown("---")
            st.subheader("Contenu généré")
            
            st.markdown(st.session_state.generated_content)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Insérer ce contenu"):
                    new_content = st.session_state.generated_content
                    
                    # Mise à jour du contenu
                    current_section["content"] = new_content
                    
                    # Sauvegarde du projet
                    project_context.update_section(project_id, current_section_id, current_section)
                    
                    # Mise à jour des métadonnées
                    project_context.update_project_metadata(project_id)
                    
                    # Sauvegarde de la version dans l'historique
                    project_data = project_context.load_project(project_id)
                    history_manager.save_version(
                        project_id=project_id,
                        project_data=project_data,
                        description=f"Génération de contenu pour la section: {current_section.get('title', 'Sans titre')}"
                    )
                    
                    # Suppression du contenu généré de la session
                    del st.session_state.generated_content
                    
                    st.success("Contenu inséré avec succès!")
                    st.rerun()
            
            with col2:
                if st.button("Ajouter à la fin"):
                    if current_content:
                        new_content = current_content + "\n\n" + st.session_state.generated_content
                    else:
                        new_content = st.session_state.generated_content
                    
                    # Mise à jour du contenu
                    current_section["content"] = new_content
                    
                    # Sauvegarde du projet
                    project_context.update_section(project_id, current_section_id, current_section)
                    
                    # Mise à jour des métadonnées
                    project_context.update_project_metadata(project_id)
                    
                    # Sauvegarde de la version dans l'historique
                    project_data = project_context.load_project(project_id)
                    history_manager.save_version(
                        project_id=project_id,
                        project_data=project_data,
                        description=f"Ajout de contenu généré pour la section: {current_section.get('title', 'Sans titre')}"
                    )
                    
                    # Suppression du contenu généré de la session
                    del st.session_state.generated_content
                    
                    st.success("Contenu ajouté avec succès!")
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
        if current_section_index < len(sections) - 1:
            if st.button("Section suivante →"):
                st.session_state.current_section_id = sections[current_section_index + 1].get("section_id", "")
                st.rerun()
    
    with col3:
        if st.button("Passer à la révision de cette section"):
            st.session_state.current_section_id = current_section_id
            st.session_state.page = "revision"
            st.rerun()
    
    # Analyse de densité qualitative
    st.markdown("---")
    st.subheader("Analyse de densité qualitative")
    
    try:
        from modules.density_analyzer import render_density_analysis
        render_density_analysis(current_section.get("content", ""), project_context, project_id)
    except ImportError:
        st.info("Le module d'analyse de densité qualitative n'est pas disponible. Veuillez installer les modules d'analyse de densité.")
    
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
    
    return

