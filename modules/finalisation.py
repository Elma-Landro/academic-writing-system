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
    
    st.title("Finalisation")
    
    # Chargement des données du projet
    project = project_context.load_project(project_id)
    
    # Affichage du titre de l'article
    st.subheader(project.get("title", "Sans titre"))
    
    # Récupération de la structure existante
    existing_structure = project.get("existing_structure", "")
    if existing_structure:
        with st.expander("Structure existante du document", expanded=False):
            st.text(existing_structure)
    
    # Vérification que toutes les sections ont été révisées
    sections = project.get("sections", [])
    total_sections = len(sections)
    revised_sections = sum(1 for section in sections if section.get("revision_status") == "Révisé")
    
    if total_sections == 0:
        st.warning("Aucune section n'a été créée. Veuillez d'abord créer des sections dans le storyboard.")
        
        if st.button("Retour au storyboard"):
            st.session_state.page = "storyboard"
            st.rerun()
            
        return
    
    if revised_sections < total_sections:
        st.warning(f"Toutes les sections n'ont pas été révisées ({revised_sections}/{total_sections}). Il est recommandé de terminer la révision avant de passer à la finalisation.")
        
        if st.button("Retour à la révision"):
            st.session_state.page = "revision"
            st.rerun()
    
    # Onglets pour les différentes fonctionnalités
    tab1, tab2, tab3, tab4 = st.tabs(["Tableau récapitulatif", "Vérifications finales", "Génération de transitions", "Prévisualisation"])
    
    with tab1:
        st.subheader("Tableau récapitulatif des sections")
        
        # Création d'un tableau récapitulatif
        data = []
        
        for i, section in enumerate(sections):
            # Calcul de la densité qualitative
            try:
                from modules.visualization.density_analyzer import analyze_text_density
                density_score = analyze_text_density(section.get("content", ""))
            except ImportError:
                density_score = "N/A"
            
            # Calcul du nombre de mots
            word_count = len(section.get("content", "").split())
            
            # Statut de révision
            revision_status = section.get("revision_status", "Non révisé")
            
            # Ajout des données au tableau
            data.append({
                "Numéro": i + 1,
                "Titre": section.get("title", "Sans titre"),
                "Mots": word_count,
                "Densité": density_score if isinstance(density_score, str) else f"{density_score}/100",
                "Statut": revision_status
            })
        
        # Affichage du tableau
        st.table(data)
        
        # Calcul des statistiques globales
        total_words = sum(item["Mots"] for item in data)
        avg_density = sum(float(item["Densité"].split("/")[0]) for item in data if item["Densité"] != "N/A") / len(data) if len(data) > 0 else 0
        
        # Affichage des statistiques globales
        st.markdown(f"**Nombre total de mots:** {total_words}")
        st.markdown(f"**Densité qualitative moyenne:** {avg_density:.1f}/100")
        
        # Affichage de la progression de révision
        st.progress(revised_sections / total_sections if total_sections > 0 else 0)
        st.markdown(f"**Progression de la révision:** {revised_sections}/{total_sections} sections révisées")
    
    with tab2:
        st.subheader("Vérifications finales")
        
        # Liste des vérifications à effectuer
        checks = [
            "Cohérence de la structure",
            "Transitions entre les sections",
            "Citations et références",
            "Orthographe et grammaire",
            "Respect des contraintes formelles",
            "Conformité au style académique"
        ]
        
        # Affichage des vérifications
        for check in checks:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{check}**")
            
            with col2:
                if st.button("Vérifier", key=f"check_{check.replace(' ', '_')}"):
                    with st.spinner(f"Vérification de {check} en cours..."):
                        # Simulation de vérification (à remplacer par une vérification réelle)
                        import time
                        import random
                        time.sleep(1)
                        
                        # Résultat aléatoire pour la démonstration
                        result = random.choice(["OK", "Attention", "Problème"])
                        
                        if result == "OK":
                            st.success(f"{check}: Aucun problème détecté")
                        elif result == "Attention":
                            st.warning(f"{check}: Quelques points à améliorer")
                        else:
                            st.error(f"{check}: Problèmes détectés")
        
        # Vérification automatique de la densité qualitative
        st.subheader("Analyse de densité qualitative")
        
        if st.button("Analyser la densité qualitative"):
            try:
                from modules.visualization.density_analyzer import analyze_project_density, get_density_recommendations
                
                # Récupération du score de densité global
                density_score = analyze_project_density(project_id, project_context)
                
                # Affichage du score de densité
                st.progress(density_score / 100)
                
                if density_score < 30:
                    st.warning(f"Densité qualitative globale: {density_score}/100 - Texte peu dense")
                elif density_score < 60:
                    st.info(f"Densité qualitative globale: {density_score}/100 - Densité moyenne")
                elif density_score < 80:
                    st.success(f"Densité qualitative globale: {density_score}/100 - Bonne densité")
                else:
                    st.success(f"Densité qualitative globale: {density_score}/100 - Excellente densité")
                
                # Affichage des recommandations
                recommendations = get_density_recommendations(density_score)
                
                st.markdown("**Recommandations d'amélioration:**")
                for recommendation in recommendations:
                    st.markdown(f"- {recommendation}")
            except ImportError:
                st.info("Le module d'analyse de densité n'est pas disponible. Veuillez installer les modules de visualisation.")
    
    with tab3:
        st.subheader("Génération de transitions")
        
        # Sélection des sections pour la transition
        st.markdown("Sélectionnez deux sections consécutives pour générer une transition:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            section1_index = st.selectbox(
                "Section de départ",
                range(len(sections)),
                format_func=lambda i: f"{i+1}. {sections[i].get('title', 'Sans titre')}"
            )
        
        with col2:
            section2_index = st.selectbox(
                "Section d'arrivée",
                range(len(sections)),
                format_func=lambda i: f"{i+1}. {sections[i].get('title', 'Sans titre')}",
                index=min(section1_index + 1, len(sections) - 1)
            )
        
        # Vérification que les sections sont différentes
        if section1_index == section2_index:
            st.error("Veuillez sélectionner deux sections différentes.")
        else:
            # Récupération des sections
            section1 = sections[section1_index]
            section2 = sections[section2_index]
            
            # Affichage des extraits des sections
            with st.expander("Extrait de la section de départ", expanded=True):
                content1 = section1.get("content", "")
                st.markdown(content1[-500:] if len(content1) > 500 else content1)
            
            with st.expander("Extrait de la section d'arrivée", expanded=True):
                content2 = section2.get("content", "")
                st.markdown(content2[:500] if len(content2) > 500 else content2)
            
            # Génération de la transition
            if st.button("Générer une transition"):
                with st.spinner("Génération de la transition en cours..."):
                    # Construction du prompt
                    prompt = f"""
                    Générer une transition entre ces deux sections:
                    
                    Section 1 ({section1.get('title', '')}): {content1[-300:] if len(content1) > 300 else content1}
                    
                    Section 2 ({section2.get('title', '')}): {content2[:300] if len(content2) > 300 else content2}
                    """
                    
                    # Génération du texte
                    result = generate_academic_text(
                        prompt=prompt,
                        style=project.get("preferences", {}).get("style", "Académique"),
                        length=100  # Transition courte
                    )
                    
                    # Affichage du résultat
                    st.subheader("Transition générée")
                    st.write(result.get("text", ""))
                    
                    # Bouton pour insérer la transition
                    if st.button("Insérer la transition"):
                        # Ajout de la transition à la fin de la première section
                        new_content1 = content1 + "\n\n" + result.get("text", "")
                        
                        # Mise à jour de la section
                        project_context.update_section(
                            project_id=project_id,
                            section_id=section1.get("section_id", ""),
                            title=section1.get("title", ""),
                            content=new_content1
                        )
                        
                        # Mise à jour des métadonnées
                        project_context.update_project_metadata(project_id)
                        
                        # Sauvegarde de la version dans l'historique
                        project_data = project_context.load_project(project_id)
                        history_manager.save_version(
                            project_id=project_id,
                            project_data=project_data,
                            description=f"Ajout d'une transition entre les sections {section1_index+1} et {section2_index+1}"
                        )
                        
                        st.success("Transition insérée avec succès!")
                        st.rerun()
    
    with tab4:
        st.subheader("Prévisualisation du document complet")
        
        # Importation du module de prévisualisation
        try:
            from modules.visualization.document_preview import render_document_preview
            render_document_preview(project_id, project_context)
        except ImportError:
            # Affichage manuel du document complet
            st.markdown(f"# {project.get('title', 'Sans titre')}")
            
            for section in sections:
                st.markdown(f"## {section.get('title', 'Sans titre')}")
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
    
    # Options d'exportation
    st.markdown("---")
    st.subheader("Exportation du document")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox(
            "Format d'exportation",
            ["Markdown", "PDF", "Word", "HTML"]
        )
    
    with col2:
        if st.button("Exporter"):
            with st.spinner(f"Exportation en {export_format} en cours..."):
                # Construction du document complet
                document = f"# {project.get('title', 'Sans titre')}\n\n"
                
                for section in sections:
                    document += f"## {section.get('title', 'Sans titre')}\n\n"
                    document += f"{section.get('content', '')}\n\n"
                
                # Exportation selon le format
                if export_format == "Markdown":
                    # Sauvegarde en Markdown
                    file_path = f"/tmp/{project.get('title', 'document').replace(' ', '_')}.md"
                    with open(file_path, "w") as f:
                        f.write(document)
                    
                    # Téléchargement du fichier
                    with open(file_path, "r") as f:
                        st.download_button(
                            label="Télécharger le document Markdown",
                            data=f.read(),
                            file_name=f"{project.get('title', 'document').replace(' ', '_')}.md",
                            mime="text/markdown"
                        )
                elif export_format == "PDF":
                    st.info("Exportation PDF à implémenter.")
                elif export_format == "Word":
                    st.info("Exportation Word à implémenter.")
                elif export_format == "HTML":
                    st.info("Exportation HTML à implémenter.")
    
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
            
            # Sauvegarde de la version dans l'historique
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
    
    # Suggestions du moteur adaptatif
    st.markdown("---")
    st.subheader("Suggestions pour la finalisation")
    
    # Suggestions basées sur le type de projet
    project_type = project.get("type", "Article académique")
    
    if project_type == "Article académique":
        st.info("""
        💡 **Conseils pour la finalisation:**
        
        - Vérifiez la cohérence globale de votre argumentation
        - Assurez-vous que l'introduction et la conclusion se répondent
        - Vérifiez que toutes les citations sont correctement référencées
        - Relisez une dernière fois pour détecter les erreurs typographiques
        - Demandez à un collègue de relire votre document
        """)
