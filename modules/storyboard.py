def render_storyboard(project_id, project_context, history_manager, adaptive_engine):
    """
    Affiche l'interface de storyboard pour un projet avec génération automatique
    et gestion de la structure narrative.
    
    Args:
        project_id: ID du projet
        project_context: Instance de ProjectContext
        history_manager: Instance de HistoryManager
        adaptive_engine: Instance de AdaptiveEngine
    """
    import streamlit as st
    from utils.ai_service import generate_academic_text, call_ai_safe
    
    st.title("Storyboard")
    
    # Chargement des données du projet
    project = project_context.load_project(project_id)
    
    st.subheader(project.get("title", "Sans titre"))
    
    # Création des onglets pour les différentes fonctionnalités
    storyboard_tabs = st.tabs(["Gestion des sections", "Génération automatique (STORYBOARD ENGINE v1)"])
    
    # Onglet 1: Gestion des sections
    with storyboard_tabs[0]:
        # Affichage des sections existantes
        sections = project.get("sections", [])
        
        if sections:
            st.write("Structure actuelle du document:")
            
            for i, section in enumerate(sections):
                with st.expander(f"{i+1}. {section.get('title', 'Sans titre')}"):
                    st.write(section.get("content", ""))
                    
                    # Affichage des thèses associées à cette section
                    theses = section.get("theses", [])
                    if theses:
                        st.write("**Thèses principales:**")
                        for thesis in theses:
                            st.write(f"- {thesis.get('content', '')}")
                            
                            # Affichage des citations associées
                            citations = thesis.get("citations", [])
                            if citations:
                                with st.expander("Citations associées"):
                                    for citation in citations:
                                        st.write(f"• *\"{citation.get('text', '')}\"* (p. {citation.get('page', 'N/A')})")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Éditer", key=f"edit_{section.get('section_id', '')}"):
                            st.session_state.current_section_id = section.get("section_id", "")
                            st.session_state.page = "redaction"
                            st.rerun()
                    
                    with col2:
                        if st.button("Supprimer", key=f"delete_{section.get('section_id', '')}"):
                            if project_context.delete_section(project_id, section.get("section_id", "")):
                                # Mise à jour des métadonnées
                                project_context.update_project_metadata(project_id)
                                
                                # Sauvegarde de la version dans l'historique
                                project_data = project_context.load_project(project_id)
                                history_manager.save_version(
                                    project_id=project_id,
                                    project_data=project_data,
                                    description=f"Suppression de la section: {section.get('title', 'Sans titre')}"
                                )
                                
                                st.success("Section supprimée avec succès!")
                                st.rerun()
                            else:
                                st.error("Erreur lors de la suppression de la section.")
        
        # Formulaire d'ajout de section
        st.markdown("---")
        st.subheader("Ajouter une nouvelle section")
        
        with st.form("add_section_form"):
            title = st.text_input("Titre de la section")
            
            # Options pour la génération de contenu
            generate_content = st.checkbox("Générer un contenu initial")
            
            if generate_content:
                content_prompt = st.text_area(
                    "Description du contenu à générer",
                    placeholder="Décrivez le contenu que vous souhaitez générer pour cette section..."
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
            
            submitted = st.form_submit_button("Ajouter la section")
            
            if submitted:
                if not title:
                    st.error("Le titre est obligatoire.")
                else:
                    content = ""
                    
                    # Génération du contenu si demandé
                    if generate_content and content_prompt:
                        with st.spinner("Génération du contenu en cours..."):
                            result = generate_academic_text(
                                prompt=content_prompt,
                                style=style,
                                length=length
                            )
                            
                            content = result.get("text", "")
                    
                    # Ajout de la section
                    section_id = project_context.add_section(
                        project_id=project_id,
                        title=title,
                        content=content
                    )
                    
                    # Mise à jour des métadonnées
                    project_context.update_project_metadata(project_id)
                    
                    # Mise à jour du statut du projet
                    if project.get("status") == "created":
                        project_context.update_project_status(project_id, "storyboard_ready")
                    
                    # Sauvegarde de la version dans l'historique
                    project_data = project_context.load_project(project_id)
                    history_manager.save_version(
                        project_id=project_id,
                        project_data=project_data,
                        description=f"Ajout de la section: {title}"
                    )
                    
                    st.success("Section ajoutée avec succès!")
                    st.rerun()
        
        # Réorganisation des sections
        if sections:
            st.markdown("---")
            st.subheader("Réorganiser les sections")
            
            st.write("Faites glisser les sections pour les réorganiser:")
            
            # Simulation d'interface de réorganisation
            section_titles = [section.get("title", "Sans titre") for section in sections]
            
            # Dans une vraie implémentation, on utiliserait une bibliothèque de drag-and-drop
            # Pour cette démonstration, on utilise une liste de sélection
            selected_indices = []
            for i, title in enumerate(section_titles):
                if st.checkbox(f"{i+1}. {title}", key=f"reorder_{i}"):
                    selected_indices.append(i)
            
            new_order = st.selectbox(
                "Nouvelle position pour les sections sélectionnées",
                range(1, len(sections) + 1)
            )
            
            if st.button("Appliquer la réorganisation") and selected_indices:
                st.info("Fonctionnalité de réorganisation à implémenter.")
                # Dans une vraie implémentation, on réorganiserait les sections ici
    
    # Onglet 2: Génération automatique (STORYBOARD ENGINE v1)
    with storyboard_tabs[1]:
        st.subheader("STORYBOARD ENGINE v1")
        st.write("""
        Générez automatiquement un storyboard académique à partir d'un document source, en suivant le pipeline de traitement en 5 étapes :
        
        1. Identification des thèses à partir du document source
        2. Association de citations marquantes pour chaque thèse
        3. Fusion et articulation logique des thèses
        4. Proposition d'un enchaînement de sections avec titres narratifs
        5. Intégration des thèses dans les sections types
        """)
        
        # Formulaire de génération automatique
        with st.form("storyboard_generation_form"):
            # Titre de l'article
            article_title = st.text_input(
                "Titre de l'article",
                value=project.get("title", ""),
                help="Le titre principal de votre document"
            )
            
            # Document source
            document_source = st.text_area(
                "Document source",
                placeholder="Collez ici le texte de votre document source (thèse, article, etc.)"
            )
            
            # Problématique / Objectif
            problem_statement = st.text_area(
                "Problématique / Objectif",
                placeholder="Décrivez la problématique ou l'objectif de votre article"
            )
            
            # Structure existante
            existing_structure = st.text_area(
                "Structure existante (si disponible)",
                placeholder="Entrez vos titres de sections et sous-sections, un par ligne. Exemple:\n\nIntroduction\n1. Contexte historique\n   1.1 Origines\n   1.2 Évolution\n2. Cadre théorique\n...",
                help="Si vous avez déjà une structure en tête, entrez vos titres de sections et sous-sections"
            )
            
            # Niveau de titre pour l'extraction des thèses
            heading_level = st.slider(
                "Niveau de titre pour l'extraction des thèses",
                min_value=1,
                max_value=6,
                value=3,
                help="Niveau de titre à partir duquel extraire les thèses (1=grands titres, 6=petits titres)"
            )
            
            # Contraintes formelles
            formal_constraints = st.text_input(
                "Contraintes formelles",
                placeholder="Ex: 5000 caractères, 10 pages, etc.",
                help="Contraintes de format pour votre document final"
            )
            
            # Nombre de citations par thèse
            citations_per_thesis = st.slider(
                "Nombre de citations par thèse",
                min_value=1,
                max_value=10,
                value=3,
                help="Combien de citations extraire pour chaque thèse identifiée"
            )
            
            # Bouton de génération
            generate_button = st.form_submit_button("Générer le storyboard")
            
            if generate_button:
                if not document_source:
                    st.error("Le document source est obligatoire.")
                elif not problem_statement:
                    st.error("La problématique ou l'objectif est obligatoire.")
                else:
                    with st.spinner("Génération du storyboard en cours..."):
                        # Construction du prompt pour la génération du storyboard
                        storyboard_prompt = f"""
                        # STORYBOARD ENGINE v1
                        
                        ## Objectif
                        Construire l'ossature narrative d'un article académique à partir du document source fourni, en identifiant et fusionnant les thèses principales, sous-thèses, et matériaux exemplaires.
                        
                        ## Inputs
                        - Titre de l'article: {article_title}
                        - Problématique/Objectif: {problem_statement}
                        - Contraintes formelles: {formal_constraints}
                        - Niveau de titre pour extraction: {heading_level}
                        - Nombre de citations par thèse: {citations_per_thesis}
                        
                        ## Structure existante (si fournie)
                        {existing_structure if existing_structure else "Aucune structure existante fournie."}
                        
                        ## Document source
                        {document_source[:10000]}  # Limitation pour éviter de dépasser les contraintes de tokens
                        
                        ## Instructions
                        1. Identifie les thèses principales à partir du document source
                        2. Associe {citations_per_thesis} citations marquantes à chaque thèse (avec numéro de page si disponible)
                        3. Fusionne et articule logiquement les thèses pour créer une ossature cohérente
                        4. Propose un enchaînement de sections avec titres narratifs provisoires
                        5. Intègre les thèses dans les sections types (intro, méthodo, etc.)
                        
                        ## Format de sortie
                        Fournis un tableau synthétique avec:
                        1. Les thèses et l'arc narratif
                        2. Les citations associées (avec pages)
                        3. Les sections de rattachement
                        
                        Puis propose une structuration narrative complète avec:
                        1. Titre de l'article (amélioré si nécessaire)
                        2. Plan argumentatif détaillé
                        """
                        
                        # Appel à l'API pour générer le storyboard
                        result = call_ai_safe(
                            prompt=storyboard_prompt,
                            max_tokens=4000,
                            temperature=0.7,
                            model="gpt-4o"
                        )
                        
                        generated_storyboard = result.get("text", "")
                        
                        if generated_storyboard:
                            # Sauvegarde du storyboard généré dans la session
                            st.session_state.generated_storyboard = generated_storyboard
                            st.session_state.storyboard_metadata = {
                                "article_title": article_title,
                                "problem_statement": problem_statement,
                                "existing_structure": existing_structure,
                                "formal_constraints": formal_constraints
                            }
                            
                            st.success("Storyboard généré avec succès!")
                        else:
                            st.error("Erreur lors de la génération du storyboard.")
        
        # Affichage du storyboard généré
        if "generated_storyboard" in st.session_state:
            st.markdown("---")
            st.subheader("Storyboard généré")
            
            # Affichage des métadonnées utilisées
            with st.expander("Structure utilisée pour la génération"):
                metadata = st.session_state.storyboard_metadata
                st.write(f"**Titre de l'article:** {metadata.get('article_title', '')}")
                st.write(f"**Problématique:** {metadata.get('problem_statement', '')}")
                
                if metadata.get('existing_structure'):
                    st.write("**Structure existante fournie:**")
                    st.text(metadata.get('existing_structure', ''))
                
                st.write(f"**Contraintes formelles:** {metadata.get('formal_constraints', '')}")
            
            # Affichage du storyboard
            st.markdown(st.session_state.generated_storyboard)
            
            # Bouton pour importer le storyboard dans le projet
            if st.button("Importer dans le projet"):
                # Analyse du storyboard généré pour extraire les sections, thèses et citations
                # Cette partie serait idéalement implémentée avec un parser plus sophistiqué
                
                # Pour cette démonstration, on utilise une approche simplifiée
                # qui extrait les sections à partir des titres de niveau 2 (##)
                import re
                
                # Mise à jour du titre du projet si nécessaire
                if metadata.get('article_title') and metadata.get('article_title') != project.get('title'):
                    project["title"] = metadata.get('article_title')
                    project_context.save_project(project)
                
                # Extraction des sections à partir du storyboard généré
                sections_pattern = r"##\s+(.*?)\n(.*?)(?=##|\Z)"
                sections_matches = re.findall(sections_pattern, st.session_state.generated_storyboard, re.DOTALL)
                
                # Suppression des sections existantes si demandé
                if sections and st.session_state.get("clear_existing_sections", False):
                    for section in sections:
                        project_context.delete_section(project_id, section.get("section_id", ""))
                
                # Création des nouvelles sections
                for title, content in sections_matches:
                    # Nettoyage du titre et du contenu
                    title = title.strip()
                    content = content.strip()
                    
                    # Extraction des thèses et citations (approche simplifiée)
                    theses = []
                    thesis_pattern = r"- (.*?)(?=\n-|\n\n|\Z)"
                    thesis_matches = re.findall(thesis_pattern, content, re.DOTALL)
                    
                    for thesis_content in thesis_matches:
                        thesis = {"content": thesis_content.strip()}
                        
                        # Extraction des citations pour cette thèse (approche simplifiée)
                        citations = []
                        citation_pattern = r"\*\"(.*?)\"\*\s*\(p\.\s*(\d+)\)"
                        citation_matches = re.findall(citation_pattern, thesis_content, re.DOTALL)
                        
                        for citation_text, page in citation_matches:
                            citations.append({
                                "text": citation_text.strip(),
                                "page": page.strip()
                            })
                        
                        thesis["citations"] = citations
                        theses.append(thesis)
                    
                    # Ajout de la section
                    section_id = project_context.add_section(
                        project_id=project_id,
                        title=title,
                        content=""  # Contenu vide, sera rempli lors de la rédaction
                    )
                    
                    # Mise à jour de la section avec les thèses et citations
                    section = project_context.get_section(project_id, section_id)
                    section["theses"] = theses
                    project_context.update_section_data(project_id, section_id, section)
                
                # Mise à jour des métadonnées
                project_context.update_project_metadata(project_id)
                
     
