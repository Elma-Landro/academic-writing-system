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
    
    st.title("Révision")
    
    # Chargement des données du projet
    project = project_context.load_project(project_id)
    
    # Affichage du titre de l'article
    st.subheader(project.get("title", "Sans titre"))
    
    # Récupération de la structure existante
    existing_structure = project.get("existing_structure", "")
    if existing_structure:
        with st.expander("Structure existante du document", expanded=False):
            st.text(existing_structure)
    
    # Récupération de la section actuelle
    current_section_id = st.session_state.get("current_section_id", None)
    
    if not current_section_id:
        # Sélection d'une section à réviser
        st.subheader("Sélectionner une section à réviser")
        
        sections = project.get("sections", [])
        
        if not sections:
            st.warning("Aucune section n'a été créée. Veuillez d'abord créer des sections dans le storyboard.")
            
            if st.button("Retour au storyboard"):
                st.session_state.page = "storyboard"
                st.rerun()
                
            return
        
        # Affichage des sections disponibles
        for i, section in enumerate(sections):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if st.button(f"{i+1}. {section.get('title', 'Sans titre')}", key=f"select_{section.get('section_id', '')}"):
                    st.session_state.current_section_id = section.get("section_id", "")
                    st.rerun()
            
            with col2:
                # Affichage du statut de révision
                revision_status = section.get("revision_status", "Non révisé")
                
                if revision_status == "Révisé":
                    st.success("Révisé")
                elif revision_status == "En cours":
                    st.info("En cours")
                else:
                    st.warning("Non révisé")
    else:
        # Édition de la section sélectionnée
        section = project_context.get_section(project_id, current_section_id)
        
        if not section:
            st.error("Section introuvable.")
            
            if st.button("Retour à la sélection"):
                st.session_state.current_section_id = None
                st.rerun()
                
            return
        
        # Affichage du titre de la section
        st.subheader(f"Révision: {section.get('title', 'Sans titre')}")
        
        # Onglets pour les différentes fonctionnalités
        tab1, tab2, tab3, tab4 = st.tabs(["Révision par paragraphe", "Révision complète", "Analyse de densité", "Prévisualisation"])
        
        with tab1:
            st.subheader("Révision par paragraphe")
            
            # Découpage du contenu en paragraphes
            content = section.get("content", "")
            paragraphs = content.split("\n\n")
            
            # Affichage et édition des paragraphes
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():  # Ignorer les paragraphes vides
                    with st.expander(f"Paragraphe {i+1}", expanded=i == 0):
                        # Affichage du paragraphe original
                        st.markdown("**Paragraphe original:**")
                        st.write(paragraph)
                        
                        # Analyse de densité qualitative du paragraphe
                        try:
                            from modules.visualization.density_analyzer import analyze_text_density
                            density_score = analyze_text_density(paragraph)
                            
                            # Affichage du score de densité
                            st.progress(density_score / 100)
                            
                            if density_score < 30:
                                st.warning(f"Densité qualitative: {density_score}/100 - Texte peu dense")
                            elif density_score < 60:
                                st.info(f"Densité qualitative: {density_score}/100 - Densité moyenne")
                            elif density_score < 80:
                                st.success(f"Densité qualitative: {density_score}/100 - Bonne densité")
                            else:
                                st.success(f"Densité qualitative: {density_score}/100 - Excellente densité")
                        except ImportError:
                            pass
                        
                        # Formulaire d'édition du paragraphe
                        with st.form(f"edit_paragraph_{i}"):
                            # Édition du paragraphe
                            new_paragraph = st.text_area(
                                "Paragraphe révisé",
                                value=paragraph,
                                height=200
                            )
                            
                            # Options de révision assistée
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.form_submit_button("Enregistrer les modifications"):
                                    # Mise à jour du paragraphe
                                    paragraphs[i] = new_paragraph
                                    
                                    # Reconstruction du contenu
                                    new_content = "\n\n".join(paragraphs)
                                    
                                    # Mise à jour de la section
                                    project_context.update_section(
                                        project_id=project_id,
                                        section_id=current_section_id,
                                        title=section.get("title", ""),
                                        content=new_content
                                    )
                                    
                                    # Mise à jour du statut de révision
                                    section["revision_status"] = "En cours"
                                    project_context.save_project(project)
                                    
                                    # Mise à jour des métadonnées
                                    project_context.update_project_metadata(project_id)
                                    
                                    # Sauvegarde de la version dans l'historique
                                    project_data = project_context.load_project(project_id)
                                    history_manager.save_version(
                                        project_id=project_id,
                                        project_data=project_data,
                                        description=f"Révision du paragraphe {i+1} de la section: {section.get('title', '')}"
                                    )
                                    
                                    st.success("Paragraphe mis à jour avec succès!")
                                    st.rerun()
                            
                            with col2:
                                revision_type = st.selectbox(
                                    "Type de révision assistée",
                                    [
                                        "Aucune",
                                        "Améliorer la clarté",
                                        "Renforcer l'argumentation",
                                        "Corriger la grammaire",
                                        "Densifier le contenu",
                                        "Simplifier le langage"
                                    ],
                                    key=f"revision_type_{i}"
                                )
                                
                                if st.form_submit_button("Appliquer la révision assistée"):
                                    if revision_type != "Aucune":
                                        with st.spinner("Génération de la révision en cours..."):
                                            # Construction du prompt
                                            prompt = f"{revision_type} du paragraphe suivant: {paragraph}"
                                            
                                            # Génération du texte
                                            result = generate_academic_text(
                                                prompt=prompt,
                                                style=project.get("preferences", {}).get("style", "Académique"),
                                                length=len(paragraph.split()) + 20  # Légèrement plus long que l'original
                                            )
                                            
                                            # Mise à jour du paragraphe
                                            paragraphs[i] = result.get("text", paragraph)
                                            
                                            # Reconstruction du contenu
                                            new_content = "\n\n".join(paragraphs)
                                            
                                            # Mise à jour de la section
                                            project_context.update_section(
                                                project_id=project_id,
                                                section_id=current_section_id,
                                                title=section.get("title", ""),
                                                content=new_content
                                            )
                                            
                                            # Mise à jour du statut de révision
                                            section["revision_status"] = "En cours"
                                            project_context.save_project(project)
                                            
                                            # Mise à jour des métadonnées
                                            project_context.update_project_metadata(project_id)
                                            
                                            # Sauvegarde de la version dans l'historique
                                            project_data = project_context.load_project(project_id)
                                            history_manager.save_version(
                                                project_id=project_id,
                                                project_data=project_data,
                                                description=f"Révision assistée ({revision_type}) du paragraphe {i+1} de la section: {section.get('title', '')}"
                                            )
                                            
                                            st.success(f"Révision assistée ({revision_type}) appliquée avec succès!")
                                            st.rerun()
                                    else:
                                        st.info("Veuillez sélectionner un type de révision assistée.")
        
        with tab2:
            st.subheader("Révision complète")
            
            # Formulaire d'édition complète
            with st.form("edit_complete_section"):
                # Titre de la section
                title = st.text_input("Titre de la section", value=section.get("title", ""))
                
                # Contenu de la section
                content = st.text_area(
                    "Contenu de la section",
                    value=section.get("content", ""),
                    height=400
                )
                
                # Boutons de soumission
                col1, col2 = st.columns(2)
                
                with col1:
                    submit_button = st.form_submit_button("Enregistrer les modifications")
                
                with col2:
                    cancel_button = st.form_submit_button("Annuler")
            
            # Traitement de la soumission
            if submit_button:
                if not title:
                    st.error("Le titre est obligatoire.")
                else:
                    # Mise à jour de la section
                    project_context.update_section(
                        project_id=project_id,
                        section_id=current_section_id,
                        title=title,
                        content=content
                    )
                    
                    # Mise à jour du statut de révision
                    section["revision_status"] = "Révisé"
                    project_context.save_project(project)
                    
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
                        description=f"Révision complète de la section: {title}"
                    )
                    
                    st.success("Section mise à jour avec succès!")
                    st.rerun()
            
            if cancel_button:
                st.session_state.current_section_id = None
                st.rerun()
            
            # Options de révision assistée
            st.subheader("Révision assistée de la section complète")
            
            col1, col2 = st.columns(2)
            
            with col1:
                revision_type = st.selectbox(
                    "Type de révision assistée",
                    [
                        "Améliorer la clarté",
                        "Renforcer l'argumentation",
                        "Corriger la grammaire",
                        "Densifier le contenu",
                        "Simplifier le langage",
                        "Révision complète"
                    ]
                )
            
            with col2:
                if st.button("Appliquer la révision assistée à toute la section"):
                    with st.spinner("Génération de la révision en cours..."):
                        # Construction du prompt
                        prompt = f"{revision_type} de la section suivante: {section.get('content', '')}"
                        
                        # Génération du texte
                        result = generate_academic_text(
                            prompt=prompt,
                            style=project.get("preferences", {}).get("style", "Académique"),
                            length=len(section.get("content", "").split()) + 50  # Légèrement plus long que l'original
                        )
                        
                        # Mise à jour de la section
                        project_context.update_section(
                            project_id=project_id,
                            section_id=current_section_id,
                            title=section.get("title", ""),
                            content=result.get("text", "")
                        )
                        
                        # Mise à jour du statut de révision
                        section["revision_status"] = "Révisé"
                        project_context.save_project(project)
                        
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
                            description=f"Révision assistée ({revision_type}) de la section: {section.get('title', '')}"
                        )
                        
                        st.success(f"Révision assistée ({revision_type}) appliquée avec succès!")
                        st.rerun()
        
        with tab3:
            st.subheader("Analyse de densité qualitative")
            
            # Analyse de densité qualitative
            try:
                from modules.visualization.density_analyzer import analyze_text_density, get_density_recommendations
                
                # Récupération du contenu
                content = section.get("content", "")
                
                # Calcul du score de densité
                density_score = analyze_text_density(content)
                
                # Affichage du score de densité
                st.markdown(f"**Score de densité qualitative:** {density_score}/100")
                st.progress(density_score / 100)
                
                # Affichage des recommandations
                recommendations = get_density_recommendations(density_score)
                
                st.markdown("**Recommandations d'amélioration:**")
                for recommendation in recommendations:
                    st.markdown(f"- {recommendation}")
                
                # Analyse par paragraphe
                st.subheader("Analyse par paragraphe")
                
                # Découpage du contenu en paragraphes
                paragraphs = content.split("\n\n")
                
                # Analyse de chaque paragraphe
                for i, paragraph in enumerate(paragraphs):
                    if paragraph.strip():  # Ignorer les paragraphes vides
                        with st.expander(f"Paragraphe {i+1}", expanded=False):
                            # Calcul du score de densité du paragraphe
                            paragraph_density = analyze_text_density(paragraph)
                            
                            # Affichage du score de densité
                            st.markdown(f"**Score de densité:** {paragraph_density}/100")
                            st.progress(paragraph_density / 100)
                            
                            # Affichage du paragraphe
                            st.markdown("**Contenu:**")
                            st.write(paragraph)
                            
                            # Affichage des recommandations
                            paragraph_recommendations = get_density_recommendations(paragraph_density)
                            
                            st.markdown("**Recommandations:**")
                            for recommendation in paragraph_recommendations:
                                st.markdown(f"- {recommendation}")
            except ImportError:
                st.info("Le module d'analyse de densité n'est pas disponible. Veuillez installer les modules de visualisation.")
        
        with tab4:
            st.subheader("Prévisualisation de la section")
            
            # Affichage du contenu formaté
            st.markdown(section.get("content", ""))
            
            # Boutons d'accès à la visualisation complète et à la timeline
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Visualisation complète du document"):
                    st.session_state.page = "document_preview"
                    st.rerun()
            
            with col2:
                if st.button("Timeline d'évolution du document"):
                    st.session_state.page = "document_timeline"
                    st.rerun()
        
        # Boutons de navigation
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Retour à la sélection"):
                st.session_state.current_section_id = None
                st.rerun()
        
        with col2:
            if st.button("Marquer comme révisé"):
                # Mise à jour du statut de révision
                section["revision_status"] = "Révisé"
                project_context.save_project(project)
                
                # Mise à jour du statut du projet
                if project.get("status") == "redaction_in_progress":
                    project_context.update_project_status(project_id, "revision_in_progress")
                
                # Sauvegarde de la version dans l'historique
                project_data = project_context.load_project(project_id)
                history_manager.save_version(
                    project_id=project_id,
                    project_data=project_data,
                    description=f"Section marquée comme révisée: {section.get('title', '')}"
                )
                
                st.success("Section marquée comme révisée!")
                st.session_state.current_section_id = None
                st.rerun()
        
        with col3:
            if st.button("Passer à la finalisation"):
                st.session_state.page = "finalisation"
                st.rerun()
    
    # Si aucune section n'est sélectionnée, afficher le statut global de révision
    if not current_section_id:
        st.markdown("---")
        st.subheader("Statut global de révision")
        
        sections = project.get("sections", [])
        total_sections = len(sections)
        revised_sections = sum(1 for section in sections if section.get("revision_status") == "Révisé")
        
        if total_sections > 0:
            progress = revised_sections / total_sections
            st.progress(progress)
            st.write(f"**{revised_sections}/{total_sections}** sections révisées")
            
            if revised_sections == total_sections:
                st.success("Toutes les sections ont été révisées!")
                
                if st.button("Passer à la finalisation"):
                    st.session_state.page = "finalisation"
                    st.rerun()
            else:
                st.info(f"Il reste {total_sections - revised_sections} sections à réviser.")
        
        # Boutons d'accès à la visualisation complète et à la timeline
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Visualisation complète du document"):
                st.session_state.page = "document_preview"
                st.rerun()
        
        with col2:
            if st.button("Timeline d'évolution du document"):
                st.session_state.page = "document_timeline"
                st.rerun()
    
    # Suggestions du moteur adaptatif
    st.markdown("---")
    st.subheader("Suggestions pour votre révision")
    
    # Suggestions basées sur le type de projet
    project_type = project.get("type", "Article académique")
    
    if project_type == "Article académique":
        st.info("""
        💡 **Conseils pour la révision académique:**
        
        - Vérifiez la cohérence de votre argumentation
        - Assurez-vous que chaque paragraphe contribue à votre thèse principale
        - Vérifiez la précision de vos citations et références
        - Éliminez les répétitions et les redondances
        - Assurez-vous que vos transitions entre les paragraphes sont fluides
        """)
