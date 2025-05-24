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
    
    st.title("Rédaction")
    
    # Chargement des données du projet
    project = project_context.load_project(project_id)
    
    # Affichage du titre de l'article
    st.subheader(project.get("title", "Sans titre"))
    
    # Récupération de la structure existante
    existing_structure = project.get("existing_structure", "")
    if existing_structure:
        with st.expander("Structure existante du document", expanded=True):
            st.text(existing_structure)
    
    # Récupération de la section actuelle
    current_section_id = st.session_state.get("current_section_id", None)
    
    if not current_section_id:
        # Sélection d'une section à éditer
        st.subheader("Sélectionner une section à éditer")
        
        sections = project.get("sections", [])
        
        if not sections:
            st.warning("Aucune section n'a été créée. Veuillez d'abord créer des sections dans le storyboard.")
            
            if st.button("Retour au storyboard"):
                st.session_state.page = "storyboard"
                st.rerun()
                
            return
        
        # Affichage des sections disponibles
        for i, section in enumerate(sections):
            if st.button(f"{i+1}. {section.get('title', 'Sans titre')}", key=f"select_{section.get('section_id', '')}"):
                st.session_state.current_section_id = section.get("section_id", "")
                st.rerun()
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
        st.subheader(f"Édition: {section.get('title', 'Sans titre')}")
        
        # Récupération des thèses et citations du storyboard si disponibles
        storyboard_data = project.get("storyboard_data", {})
        section_theses = []
        
        for thesis_section in storyboard_data.get("sections", []):
            if thesis_section.get("title") == section.get("title"):
                section_theses = thesis_section.get("theses", [])
                break
        
        # Affichage des thèses et citations associées à cette section
        if section_theses:
            with st.expander("Thèses et citations du storyboard", expanded=True):
                for i, thesis in enumerate(section_theses):
                    st.markdown(f"**Thèse {i+1}:** {thesis.get('text', '')}")
                    
                    citations = thesis.get("citations", [])
                    if citations:
                        st.markdown("**Citations:**")
                        for j, citation in enumerate(citations):
                            st.markdown(f"- {citation}")
                    
                    st.markdown("---")
        
        # Onglets pour les différentes fonctionnalités
        tab1, tab2, tab3 = st.tabs(["Édition", "Assistance IA", "Prévisualisation"])
        
        with tab1:
            # Formulaire d'édition
            with st.form("edit_section_form"):
                # Titre de la section
                title = st.text_input("Titre de la section", value=section.get("title", ""))
                
                # Contenu de la section
                content = st.text_area(
                    "Contenu de la section",
                    value=section.get("content", ""),
                    height=400
                )
                
                # Analyse de densité qualitative
                try:
                    from modules.visualization.density_analyzer import analyze_text_density
                    density_score = analyze_text_density(content)
                    
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
                        description=f"Mise à jour de la section: {title}"
                    )
                    
                    st.success("Section mise à jour avec succès!")
                    st.rerun()
            
            if cancel_button:
                st.session_state.current_section_id = None
                st.rerun()
        
        with tab2:
            st.subheader("Assistance à la rédaction")
            
            # Options d'assistance
            assistance_type = st.selectbox(
                "Type d'assistance",
                [
                    "Développer un paragraphe",
                    "Reformuler un passage",
                    "Ajouter une transition",
                    "Créer une introduction",
                    "Créer une conclusion",
                    "Améliorer le style"
                ]
            )
            
            # Formulaire d'assistance
            with st.form("assistance_form"):
                if assistance_type in ["Développer un paragraphe", "Reformuler un passage"]:
                    text_input = st.text_area(
                        "Texte à traiter",
                        placeholder="Entrez le texte à développer ou reformuler..."
                    )
                elif assistance_type == "Ajouter une transition":
                    text_input = st.text_area(
                        "Contexte",
                        placeholder="Décrivez les deux parties à relier par une transition..."
                    )
                elif assistance_type in ["Créer une introduction", "Créer une conclusion"]:
                    text_input = st.text_area(
                        "Points clés",
                        placeholder="Listez les points clés à inclure..."
                    )
                else:
                    text_input = st.text_area(
                        "Texte à améliorer",
                        placeholder="Entrez le texte dont vous souhaitez améliorer le style..."
                    )
                
                # Style d'écriture
                style = st.selectbox(
                    "Style d'écriture",
                    ["Standard", "Académique", "CRÉSUS-NAKAMOTO", "AcademicWritingCrypto"],
                    index=["Standard", "Académique", "CRÉSUS-NAKAMOTO", "AcademicWritingCrypto"].index(
                        project.get("preferences", {}).get("style", "Standard")
                    )
                )
                
                # Longueur approximative
                if assistance_type != "Reformuler un passage":
                    length = st.slider(
                        "Longueur approximative (mots)",
                        min_value=50,
                        max_value=500,
                        value=200,
                        step=50
                    )
                
                # Bouton de génération
                generate_button = st.form_submit_button("Générer")
            
            # Traitement de la génération
            if generate_button:
                if not text_input:
                    st.error("Le texte d'entrée est obligatoire.")
                else:
                    with st.spinner("Génération en cours..."):
                        # Construction du prompt
                        prompt = f"{assistance_type}: {text_input}"
                        
                        # Génération du texte
                        result = generate_academic_text(
                            prompt=prompt,
                            style=style,
                            length=length if assistance_type != "Reformuler un passage" else None
                        )
                        
                        # Affichage du résultat
                        st.subheader("Résultat")
                        st.write(result.get("text", ""))
                        
                        # Bouton pour insérer le résultat dans le contenu
                        if st.button("Insérer dans le contenu"):
                            # Récupération du contenu actuel
                            current_content = section.get("content", "")
                            
                            # Ajout du résultat à la fin du contenu
                            new_content = current_content + "\n\n" + result.get("text", "")
                            
                            # Mise à jour de la section
                            project_context.update_section(
                                project_id=project_id,
                                section_id=current_section_id,
                                title=section.get("title", ""),
                                content=new_content
                            )
                            
                            # Mise à jour des métadonnées
                            project_context.update_project_metadata(project_id)
                            
                            # Sauvegarde de la version dans l'historique
                            project_data = project_context.load_project(project_id)
                            history_manager.save_version(
                                project_id=project_id,
                                project_data=project_data,
                                description=f"Ajout de contenu assisté par IA: {assistance_type}"
                            )
                            
                            st.success("Contenu inséré avec succès!")
                            st.rerun()
        
        with tab3:
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
            if st.button("Passer à la révision"):
                st.session_state.page = "revision"
                st.session_state.current_section_id = current_section_id
                st.rerun()
        
        with col3:
            if st.button("Retour au projet"):
                st.session_state.page = "project_overview"
                st.session_state.current_section_id = None
                st.rerun()
    
    # Suggestions du moteur adaptatif
    st.markdown("---")
    st.subheader("Suggestions pour votre rédaction")
    
    # Suggestions basées sur le type de projet
    project_type = project.get("type", "Article académique")
    
    if project_type == "Article académique":
        st.info("""
        💡 **Conseils pour la rédaction académique:**
        
        - Utilisez un langage précis et spécifique
        - Évitez les affirmations non étayées
        - Citez vos sources de manière appropriée
        - Structurez vos paragraphes avec une idée principale
        - Utilisez des transitions entre les paragraphes
        """)
    
    # Analyse de la densité qualitative globale
    try:
        from modules.visualization.density_analyzer import analyze_project_density
        
        # Récupération du score de densité global
        density_score = analyze_project_density(project_id, project_context)
        
        # Affichage du score de densité
        st.subheader("Analyse de la densité qualitative")
        st.progress(density_score / 100)
        
        if density_score < 30:
            st.warning(f"Densité qualitative globale: {density_score}/100 - Texte peu dense")
            st.markdown("""
            **Suggestions d'amélioration:**
            - Ajoutez plus d'arguments et d'exemples
            - Développez vos idées avec plus de détails
            - Utilisez des citations pour appuyer vos propos
            """)
        elif density_score < 60:
            st.info(f"Densité qualitative globale: {density_score}/100 - Densité moyenne")
            st.markdown("""
            **Suggestions d'amélioration:**
            - Renforcez les connexions entre vos idées
            - Ajoutez des nuances à vos arguments
            - Utilisez un vocabulaire plus précis
            """)
        elif density_score < 80:
            st.success(f"Densité qualitative globale: {density_score}/100 - Bonne densité")
            st.markdown("""
            **Suggestions d'amélioration:**
            - Peaufinez les transitions entre les paragraphes
            - Vérifiez la cohérence de votre argumentation
            - Assurez-vous que chaque section contribue à votre thèse principale
            """)
        else:
            st.success(f"Densité qualitative globale: {density_score}/100 - Excellente densité")
            st.markdown("""
            **Suggestions:**
            - Vérifiez la clarté de votre argumentation
            - Assurez-vous que votre texte reste accessible malgré sa densité
            - Envisagez de passer à l'étape de révision
            """)
    except ImportError:
        pass
