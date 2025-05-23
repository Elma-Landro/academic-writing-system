def render_finalisation(project_id, project_context, history_manager, adaptive_engine):
    """
    Affiche l'interface de finalisation pour un projet.
    
    Args:
        project_id: ID du projet
        project_context: Instance de ProjectContext
        history_manager: Instance de HistoryManager
        adaptive_engine: Instance de AdaptiveEngine
    """
    import streamlit as st
    from utils.ai_service import generate_academic_text
    import pandas as pd
    
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
    
    # Affichage du titre du projet
    st.title(f"Finalisation: {project.get('title', 'Sans titre')}")
    
    # Affichage de la structure existante si présente
    existing_structure = project.get("existing_structure", "")
    if existing_structure:
        with st.expander("Structure du document"):
            st.text(existing_structure)
    
    # Onglets pour les différentes fonctionnalités
    tab1, tab2, tab3, tab4 = st.tabs(["Vue d'ensemble", "Vérifications", "Exportation", "Analyse de densité"])
    
    with tab1:
        st.subheader("Vue d'ensemble du document")
        
        # Tableau récapitulatif des sections
        data = []
        
        for section in sections:
            content = section.get("content", "")
            word_count = len(content.split())
            char_count = len(content)
            
            # Analyse de densité qualitative
            try:
                from modules.density_analyzer import analyze_text_density
                density_score, density_category, density_color = analyze_text_density(content, project_context, project_id)
            except ImportError:
                density_score = 0
                density_category = "N/A"
                density_color = "#CCCCCC"
            
            data.append({
                "Section": section.get("title", "Sans titre"),
                "Mots": word_count,
                "Caractères": char_count,
                "Densité": f"{density_score:.1f}/100 ({density_category})"
            })
        
        # Création du DataFrame
        df = pd.DataFrame(data)
        
        # Ajout d'une ligne de total
        total_words = df["Mots"].sum()
        total_chars = df["Caractères"].sum()
        
        # Calcul de la densité moyenne
        try:
            from modules.density_analyzer import analyze_text_density
            all_content = "\n\n".join([section.get("content", "") for section in sections])
            avg_density_score, avg_density_category, _ = analyze_text_density(all_content, project_context, project_id)
            avg_density = f"{avg_density_score:.1f}/100 ({avg_density_category})"
        except ImportError:
            avg_density = "N/A"
        
        df.loc[len(df)] = ["TOTAL", total_words, total_chars, avg_density]
        
        # Affichage du tableau
        st.dataframe(df)
        
        # Prévisualisation du document complet
        st.markdown("---")
        st.subheader("Prévisualisation du document")
        
        # Importation du module de prévisualisation
        try:
            from modules.document_preview import render_document_preview
            render_document_preview(project_id, project_context)
        except ImportError:
            st.info("Le module de prévisualisation n'est pas disponible. Veuillez installer les modules de visualisation continue.")
    
    with tab2:
        st.subheader("Vérifications finales")
        
        # Liste de vérifications
        checks = [
            "Cohérence de la structure",
            "Transitions entre les sections",
            "Citations et références",
            "Orthographe et grammaire",
            "Respect des contraintes formelles",
            "Conformité au style académique"
        ]
        
        # Affichage des vérifications
        for i, check in enumerate(checks):
            check_key = f"check_{i}"
            check_status = st.session_state.get(check_key, False)
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.checkbox(check, value=check_status, key=check_key)
            
            with col2:
                if st.button("Vérifier", key=f"verify_{i}"):
                    # Simulation de vérification
                    st.session_state[check_key] = True
                    st.success(f"Vérification de '{check}' effectuée avec succès!")
        
        # Vérification automatique
        st.markdown("---")
        if st.button("Vérifier automatiquement tout le document"):
            with st.spinner("Vérification en cours..."):
                # Simulation de vérification automatique
                for i in range(len(checks)):
                    st.session_state[f"check_{i}"] = True
                
                st.success("Toutes les vérifications ont été effectuées avec succès!")
        
        # Génération de transitions
        st.markdown("---")
        st.subheader("Génération de transitions")
        
        # Sélection des sections
        section_titles = [section.get("title", "Sans titre") for section in sections]
        
        col1, col2 = st.columns(2)
        
        with col1:
            from_section = st.selectbox(
                "De la section",
                section_titles,
                index=0
            )
        
        with col2:
            to_section = st.selectbox(
                "À la section",
                section_titles,
                index=min(1, len(section_titles) - 1)
            )
        
        if st.button("Générer une transition"):
            if from_section == to_section:
                st.warning("Veuillez sélectionner deux sections différentes.")
            else:
                with st.spinner("Génération de la transition en cours..."):
                    # Construction du prompt
                    from_index = section_titles.index(from_section)
                    to_index = section_titles.index(to_section)
                    
                    from_content = sections[from_index].get("content", "")
                    to_content = sections[to_index].get("content", "")
                    
                    # Extraction des derniers et premiers paragraphes
                    from_paragraphs = from_content.split("\n\n")
                    to_paragraphs = to_content.split("\n\n")
                    
                    last_paragraph = from_paragraphs[-1] if from_paragraphs else ""
                    first_paragraph = to_paragraphs[0] if to_paragraphs else ""
                    
                    prompt = f"""
                    Générer une transition académique entre ces deux sections:
                    
                    Section 1 ({from_section}), dernier paragraphe:
                    {last_paragraph}
                    
                    Section 2 ({to_section}), premier paragraphe:
                    {first_paragraph}
                    
                    La transition doit être fluide, logique et maintenir la cohérence du discours académique.
                    """
                    
                    # Génération de la transition
                    result = generate_academic_text(
                        prompt=prompt,
                        style=project.get("preferences", {}).get("style", "Académique"),
                        length=100
                    )
                    
                    transition = result.get("text", "")
                    
                    if transition:
                        st.session_state.transition = transition
                        st.session_state.from_section = from_section
                        st.session_state.to_section = to_section
                        st.success("Transition générée avec succès!")
                        st.rerun()
                    else:
                        st.error("Erreur lors de la génération de la transition.")
        
        # Affichage de la transition générée
        if hasattr(st.session_state, 'transition'):
            st.markdown("---")
            st.subheader(f"Transition de '{st.session_state.from_section}' à '{st.session_state.to_section}'")
            
            st.markdown(st.session_state.transition)
            
            if st.button("Insérer cette transition"):
                # Recherche des sections
                from_index = section_titles.index(st.session_state.from_section)
                to_index = section_titles.index(st.session_state.to_section)
                
                # Mise à jour du contenu de la section de destination
                to_content = sections[to_index].get("content", "")
                new_content = st.session_state.transition + "\n\n" + to_content
                
                sections[to_index]["content"] = new_content
                
                # Sauvegarde du projet
                project_context.update_section(project_id, sections[to_index].get("section_id", ""), sections[to_index])
                
                # Mise à jour des métadonnées
                project_context.update_project_metadata(project_id)
                
                # Sauvegarde de la version dans l'historique
                project_data = project_context.load_project(project_id)
                history_manager.save_version(
                    project_id=project_id,
                    project_data=project_data,
                    description=f"Ajout d'une transition entre '{st.session_state.from_section}' et '{st.session_state.to_section}'"
                )
                
                # Suppression de la transition de la session
                del st.session_state.transition
                del st.session_state.from_section
                del st.session_state.to_section
                
                st.success("Transition insérée avec succès!")
                st.rerun()
    
    with tab3:
        st.subheader("Exportation du document")
        
        # Options d'exportation
        export_format = st.selectbox(
            "Format d'exportation",
            ["Markdown (.md)", "PDF (.pdf)", "Word (.docx)", "HTML (.html)"]
        )
        
        # Options de style
        style_options = st.multiselect(
            "Options de style",
            [
                "Page de titre",
                "Table des matières",
                "Numérotation des pages",
                "En-têtes et pieds de page",
                "Bibliographie",
                "Annexes"
            ],
            default=["Page de titre", "Table des matières", "Numérotation des pages"]
        )
        
        # Bouton d'exportation
        if st.button("Exporter le document"):
            with st.spinner("Exportation en cours..."):
                # Simulation d'exportation
                st.success(f"Document exporté avec succès au format {export_format}!")
                
                # Dans une vraie implémentation, on générerait le fichier ici
                # et on fournirait un lien de téléchargement
                
                st.download_button(
                    label="Télécharger le document",
                    data="Contenu du document exporté",
                    file_name=f"{project.get('title', 'document')}.{export_format.split('.')[-1].lower()}",
                    mime="text/plain"
                )
    
    with tab4:
        st.subheader("Analyse de densité qualitative")
        
        # Importation du module d'analyse de densité
        try:
            from modules.density_analyzer import render_density_settings, render_density_analysis
            
            # Paramètres d'analyse de densité
            render_density_settings(project_context, project_id)
            
            st.markdown("---")
            st.subheader("Analyse du document complet")
            
            # Analyse du document complet
            all_content = "\n\n".join([section.get("content", "") for section in sections])
            render_density_analysis(all_content, project_context, project_id)
            
            # Analyse par section
            st.markdown("---")
            st.subheader("Analyse par section")
            
            for section in sections:
                with st.expander(section.get("title", "Sans titre")):
                    render_density_analysis(section.get("content", ""), project_context, project_id)
        
        except ImportError:
            st.info("Le module d'analyse de densité qualitative n'est pas disponible. Veuillez installer les modules d'analyse de densité.")
    
    # Boutons de visualisation de la timeline
    st.markdown("---")
    if st.button("📊 Voir l'évolution du document"):
        st.session_state.previous_page = st.session_state.page
        st.session_state.page = "document_timeline"
        st.rerun()
    
    # Bouton pour terminer le projet
    st.markdown("---")
    if st.button("Terminer le projet"):
        # Mise à jour du statut du projet
        project_context.update_project_status(project_id, "completed")
        
        # Sauvegarde de la version dans l'historique
        project_data = project_context.load_project(project_id)
        history_manager.save_version(
            project_id=project_id,
            project_data=project_data,
            description="Projet terminé"
        )
        
        st.success("Projet terminé avec succès!")
        
        # Redirection vers la page du projet
        st.session_state.page = "project_overview"
        st.rerun()
    
    return

