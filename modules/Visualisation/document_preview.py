"""
Module de prévisualisation du document en construction.
Permet une visualisation continue du document à chaque étape du processus.
"""

def render_document_preview(project_id, project_context, current_section_id=None, highlight_changes=False):
    """
    Affiche une prévisualisation du document en construction.
    
    Args:
        project_id: ID du projet
        project_context: Instance de ProjectContext
        current_section_id: ID de la section actuellement éditée (optionnel)
        highlight_changes: Mettre en évidence les modifications récentes
    """
    import streamlit as st
    
    # Chargement des données du projet
    project = project_context.load_project(project_id)
    sections = project.get("sections", [])
    
    if not sections:
        st.info("Aucune section n'a été créée. La prévisualisation n'est pas disponible.")
        return
    
    # Titre du document
    st.markdown(f"# {project.get('title', 'Sans titre')}")
    
    # Description/Résumé
    if project.get("description"):
        st.markdown("## Résumé")
        st.markdown(project.get("description"))
    
    # Sections
    for i, section in enumerate(sections):
        # Déterminer si cette section est celle en cours d'édition
        is_current = section.get("section_id") == current_section_id
        
        # Style pour la section en cours d'édition
        if is_current:
            st.markdown(f"## 📝 {section.get('title', f'Section {i+1}')} (en cours d'édition)")
        else:
            st.markdown(f"## {section.get('title', f'Section {i+1}')}")
        
        # Contenu de la section
        content = section.get("content", "")
        
        if content:
            # Si on doit mettre en évidence les modifications récentes
            if highlight_changes and "previous_versions" in section:
                previous_content = section["previous_versions"][-1].get("content", "")
                
                # Comparaison simplifiée (à remplacer par une bibliothèque de diff)
                if previous_content != content:
                    st.markdown(content)
                    st.info("Cette section a été modifiée récemment.")
            else:
                st.markdown(content)
        else:
            st.info("Cette section n'a pas encore de contenu.")
    
    # Bibliographie (si des références sont présentes)
    references = project.get("references", {})
    if references:
        st.markdown("## Bibliographie")
        
        for ref_key, ref_data in references.items():
            title = ref_data.get('title', 'Sans titre')
            creators = ref_data.get('creators', [])
            author_str = ""
            if creators:
                author_names = []
                for author in creators:
                    if 'lastName' in author and 'firstName' in author:
                        author_names.append(f"{author['lastName']}, {author['firstName'][0]}.")
                author_str = ", ".join(author_names)
            
            year = ref_data.get('date', '').split('-')[0] if ref_data.get('date') else "n.d."
            journal = ref_data.get('publicationTitle', '')
            
            entry = f"- {author_str} ({year}). **{title}**."
            if journal:
                entry += f" *{journal}*."
            
            st.markdown(entry)
