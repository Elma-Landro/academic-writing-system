"""
Module de timeline interactive pour visualiser l'évolution du document.
Permet de suivre les modifications du document au fil du temps avec comptage de caractères.
"""

def render_document_timeline(project_id, history_manager, project_context):
    """
    Affiche une timeline interactive de l'évolution du document avec comptage de caractères.
    
    Args:
        project_id: ID du projet
        history_manager: Instance de HistoryManager
        project_context: Instance de ProjectContext
    """
    import streamlit as st
    import datetime
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Récupération de l'historique du projet
    versions = history_manager.get_versions(project_id)
    
    if not versions:
        st.info("Aucun historique disponible pour ce projet.")
        return
    
    # Titre de la timeline
    st.subheader("Évolution du document")
    
    # Calcul des statistiques pour chaque version
    version_stats = []
    for version in versions:
        version_data = version.get("data", {})
        sections = version_data.get("sections", [])
        
        # Calcul du nombre total de caractères
        total_chars = 0
        total_words = 0
        for section in sections:
            content = section.get("content", "")
            total_chars += len(content)
            total_words += len(content.split())
        
        # Ajout des statistiques à la liste
        version_stats.append({
            "timestamp": version.get("timestamp", ""),
            "description": version.get("description", "Version sans description"),
            "chars": total_chars,
            "words": total_words
        })
    
    # Graphique d'évolution du nombre de caractères
    if len(version_stats) > 1:
        st.subheader("Évolution quantitative du document")
        
        # Préparation des données pour le graphique
        timestamps = []
        chars = []
        words = []
        
        for stat in reversed(version_stats):
            try:
                date_obj = datetime.datetime.fromisoformat(stat["timestamp"])
                formatted_date = date_obj.strftime("%d/%m %H:%M")
            except:
                formatted_date = stat["timestamp"][:10]
            
            timestamps.append(formatted_date)
            chars.append(stat["chars"])
            words.append(stat["words"])
        
        # Création du graphique
        fig, ax1 = plt.subplots(figsize=(10, 4))
        
        # Axe pour les caractères
        color = 'tab:blue'
        ax1.set_xlabel('Versions')
        ax1.set_ylabel('Nombre de caractères', color=color)
        ax1.plot(timestamps, chars, color=color, marker='o', linestyle='-', linewidth=2, markersize=8)
        ax1.tick_params(axis='y', labelcolor=color)
        
        # Axe secondaire pour les mots
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Nombre de mots', color=color)
        ax2.plot(timestamps, words, color=color, marker='s', linestyle='--', linewidth=2, markersize=6)
        ax2.tick_params(axis='y', labelcolor=color)
        
        # Rotation des labels de l'axe x pour une meilleure lisibilité
        plt.xticks(rotation=45)
        
        # Ajout d'une grille
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Ajustement automatique de la mise en page
        fig.tight_layout()
        
        # Affichage du graphique
        st.pyplot(fig)
        
        # Calcul des taux de croissance
        if len(chars) > 1:
            st.subheader("Taux de croissance")
            
            growth_data = []
            for i in range(1, len(chars)):
                char_growth = ((chars[i] - chars[i-1]) / max(1, chars[i-1])) * 100
                word_growth = ((words[i] - words[i-1]) / max(1, words[i-1])) * 100
                
                growth_data.append({
                    "version": timestamps[i],
                    "char_growth": char_growth,
                    "word_growth": word_growth,
                    "char_diff": chars[i] - chars[i-1],
                    "word_diff": words[i] - words[i-1]
                })
            
            # Affichage des taux de croissance
            for growth in growth_data:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Version {growth['version']}**")
                
                with col2:
                    if growth["char_growth"] > 0:
                        st.markdown(f"<span style='color:green'>+{growth['char_diff']} caractères (+{growth['char_growth']:.1f}%)</span>", unsafe_allow_html=True)
                    elif growth["char_growth"] < 0:
                        st.markdown(f"<span style='color:red'>{growth['char_diff']} caractères ({growth['char_growth']:.1f}%)</span>", unsafe_allow_html=True)
                    else:
                        st.write(f"Pas de changement")
                
                with col3:
                    if growth["word_growth"] > 0:
                        st.markdown(f"<span style='color:green'>+{growth['word_diff']} mots (+{growth['word_growth']:.1f}%)</span>", unsafe_allow_html=True)
                    elif growth["word_growth"] < 0:
                        st.markdown(f"<span style='color:red'>{growth['word_diff']} mots ({growth['word_growth']:.1f}%)</span>", unsafe_allow_html=True)
                    else:
                        st.write(f"Pas de changement")
    
    # Style CSS pour la timeline
    st.markdown("""
    <style>
    .timeline-container {
        position: relative;
        width: 100%;
        margin: 20px 0;
        padding-left: 30px;
    }
    .timeline-line {
        position: absolute;
        left: 10px;
        top: 0;
        bottom: 0;
        width: 2px;
        background-color: #ccc;
    }
    .timeline-item {
        position: relative;
        margin-bottom: 15px;
        padding: 10px;
        border-radius: 5px;
        background-color: #f0f2f6;
        transition: all 0.3s ease;
    }
    .timeline-item:hover {
        background-color: #e0e2e6;
        transform: translateX(5px);
    }
    .timeline-dot {
        position: absolute;
        left: -30px;
        top: 15px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #4CAF50;
    }
    .timeline-date {
        font-size: 0.8em;
        color: #666;
    }
    .timeline-description {
        font-weight: bold;
    }
    .timeline-stats {
        margin-top: 5px;
        font-size: 0.9em;
        color: #333;
    }
    .timeline-current {
        background-color: #e6f7ff;
        border-left: 3px solid #1890ff;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Conteneur de la timeline
    st.markdown('<div class="timeline-container"><div class="timeline-line"></div>', unsafe_allow_html=True)
    
    # Affichage des versions dans la timeline
    for i, (version, stats) in enumerate(zip(reversed(versions), reversed(version_stats))):
        timestamp = version.get("timestamp", "")
        description = version.get("description", "Version sans description")
        
        # Conversion du timestamp en format lisible
        try:
            date_obj = datetime.datetime.fromisoformat(timestamp)
            formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
        except:
            formatted_date = timestamp
        
        # Déterminer si c'est la version actuelle
        is_current = i == 0
        current_class = "timeline-current" if is_current else ""
        
        # Affichage de l'élément de timeline avec statistiques
        st.markdown(f"""
        <div class="timeline-item {current_class}" id="version_{len(versions)-i-1}">
            <div class="timeline-dot"></div>
            <div class="timeline-date">{formatted_date}</div>
            <div class="timeline-description">{description}</div>
            <div class="timeline-stats">
                <span title="Nombre de caractères">📝 {stats['chars']} caractères</span> | 
                <span title="Nombre de mots">📊 {stats['words']} mots</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Bouton pour visualiser cette version
        if st.button(f"Visualiser cette version", key=f"view_version_{len(versions)-i-1}"):
            st.session_state.selected_version = version
            st.session_state.show_historical_preview = True
            st.rerun()
    
    # Fermeture du conteneur de la timeline
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Affichage de la version sélectionnée
    if st.session_state.get("show_historical_preview", False) and "selected_version" in st.session_state:
        selected_version = st.session_state.selected_version
        version_data = selected_version.get("data", {})
        
        st.markdown("---")
        st.subheader(f"Prévisualisation de la version: {selected_version.get('description', '')}")
        
        # Calcul des statistiques pour cette version
        sections = version_data.get("sections", [])
        total_chars = sum(len(section.get("content", "")) for section in sections)
        total_words = sum(len(section.get("content", "").split()) for section in sections)
        
        # Affichage des statistiques
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Nombre de caractères", total_chars)
        with col2:
            st.metric("Nombre de mots", total_words)
        
        # Bouton pour fermer la prévisualisation
        if st.button("Fermer la prévisualisation"):
            st.session_state.show_historical_preview = False
            if "selected_version" in st.session_state:
                del st.session_state.selected_version
            st.rerun()
        
        # Titre du document
        st.markdown(f"# {version_data.get('title', 'Sans titre')}")
        
        # Description/Résumé
        if version_data.get("description"):
            st.markdown("## Résumé")
            st.markdown(version_data.get("description"))
        
        # Sections
        sections = version_data.get("sections", [])
        for i, section in enumerate(sections):
            content = section.get("content", "")
            section_chars = len(content)
            section_words = len(content.split())
            
            st.markdown(f"## {section.get('title', f'Section {i+1}')} ({section_chars} caractères, {section_words} mots)")
            st.markdown(content)
        
        # Bibliographie (si des références sont présentes)
        references = version_data.get("references", {})
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
