"""
Module d'intégration de la visualisation dans le système de rédaction académique.

Ce module fournit des fonctions pour intégrer les fonctionnalités de visualisation
dans les différents modules du système.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def add_visualization_buttons(col1=None, col2=None):
    """
    Ajoute des boutons de visualisation dans les colonnes spécifiées.
    
    Args:
        col1: Première colonne Streamlit (optionnel)
        col2: Deuxième colonne Streamlit (optionnel)
    """
    if col1 is None and col2 is None:
        col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Prévisualiser le document complet"):
            st.session_state.previous_page = st.session_state.page
            st.session_state.page = "document_preview"
            st.rerun()
    
    with col2:
        if st.button("📊 Voir l'évolution du document"):
            st.session_state.previous_page = st.session_state.page
            st.session_state.page = "document_timeline"
            st.rerun()

def render_document_stats(project_id, project_context):
    """
    Affiche les statistiques du document.
    
    Args:
        project_id: ID du projet
        project_context: Instance de ProjectContext
    """
    # Chargement des données du projet
    project = project_context.load_project(project_id)
    
    # Récupération des sections
    sections = project.get("sections", [])
    
    # Vérification qu'il y a des sections
    if not sections:
        st.info("Aucune section n'a été créée. Les statistiques ne sont pas disponibles.")
        return
    
    # Calcul des statistiques
    data = []
    
    for section in sections:
        content = section.get("content", "")
        word_count = len(content.split())
        char_count = len(content)
        
        # Analyse de densité qualitative
        try:
            from modules.visualization.density_analyzer import analyze_text_density
            density_score, density_category, density_color = analyze_text_density(content, project_context, project_id)
        except ImportError:
            density_score = 0
            density_category = "N/A"
            density_color = "#CCCCCC"
        
        data.append({
            "Section": section.get("title", "Sans titre"),
            "Mots": word_count,
            "Caractères": char_count,
            "Densité": density_score,
            "Catégorie": density_category,
            "Couleur": density_color
        })
    
    # Création du DataFrame
    df = pd.DataFrame(data)
    
    # Ajout d'une ligne de total
    total_words = df["Mots"].sum()
    total_chars = df["Caractères"].sum()
    avg_density = df["Densité"].mean() if len(df) > 0 else 0
    
    # Détermination de la catégorie moyenne
    if avg_density >= 80:
        avg_category = "Très haute"
        avg_color = "#28a745"
    elif avg_density >= 60:
        avg_category = "Haute"
        avg_color = "#5cb85c"
    elif avg_density >= 40:
        avg_category = "Moyenne"
        avg_color = "#ffc107"
    elif avg_density >= 20:
        avg_category = "Faible"
        avg_color = "#fd7e14"
    else:
        avg_category = "Très faible"
        avg_color = "#dc3545"
    
    df.loc[len(df)] = ["TOTAL", total_words, total_chars, avg_density, avg_category, avg_color]
    
    # Affichage du tableau
    st.subheader("Statistiques du document")
    
    # Création d'un tableau stylisé
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["Section", "Mots", "Caractères", "Densité", "Catégorie"],
            fill_color="#075985",
            align="left",
            font=dict(color="white", size=12)
        ),
        cells=dict(
            values=[
                df["Section"],
                df["Mots"],
                df["Caractères"],
                [f"{d:.1f}/100" for d in df["Densité"]],
                df["Catégorie"]
            ],
            fill_color=[["#f8fafc"] * (len(df) - 1) + ["#e2e8f0"], 
                       ["#f8fafc"] * (len(df) - 1) + ["#e2e8f0"],
                       ["#f8fafc"] * (len(df) - 1) + ["#e2e8f0"],
                       ["#f8fafc"] * (len(df) - 1) + ["#e2e8f0"],
                       [df["Couleur"]]],
            align="left",
            font=dict(color="black", size=11)
        )
    )])
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=35 * (len(df) + 1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Graphique de répartition des mots
    st.subheader("Répartition des mots par section")
    
    # Exclure la ligne de total
    df_without_total = df.iloc[:-1]
    
    fig = px.pie(
        df_without_total,
        values="Mots",
        names="Section",
        color="Section",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Graphique de densité qualitative
    st.subheader("Densité qualitative par section")
    
    fig = px.bar(
        df_without_total,
        x="Section",
        y="Densité",
        color="Catégorie",
        color_discrete_map={
            "Très haute": "#28a745",
            "Haute": "#5cb85c",
            "Moyenne": "#ffc107",
            "Faible": "#fd7e14",
            "Très faible": "#dc3545"
        },
        text_auto=".1f"
    )
    
    fig.update_layout(
        xaxis_title="Section",
        yaxis_title="Score de densité (0-100)",
        yaxis_range=[0, 100],
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    return df

def render_visualization_sidebar():
    """
    Affiche une barre latérale pour la visualisation.
    """
    with st.sidebar:
        st.header("Options de visualisation")
        
        st.subheader("Affichage")
        show_content = st.checkbox("Afficher le contenu", value=True)
        show_stats = st.checkbox("Afficher les statistiques", value=True)
        show_density = st.checkbox("Afficher l'analyse de densité", value=True)
        
        st.subheader("Navigation")
        if st.button("Retour au projet"):
            st.session_state.page = "project_overview"
            st.rerun()
        
        if st.button("Aller au storyboard"):
            st.session_state.page = "storyboard"
            st.rerun()
        
        if st.button("Aller à la rédaction"):
            st.session_state.page = "redaction"
            st.rerun()
        
        if st.button("Aller à la révision"):
            st.session_state.page = "revision"
            st.rerun()
        
        if st.button("Aller à la finalisation"):
            st.session_state.page = "finalisation"
            st.rerun()
    
    return show_content, show_stats, show_density

def get_project_versions(project_id, history_manager):
    """
    Récupère les versions d'un projet.
    
    Args:
        project_id: ID du projet
        history_manager: Instance de HistoryManager
    
    Returns:
        DataFrame: DataFrame contenant les versions du projet
    """
    # Récupération de l'historique
    history = history_manager.get_project_history(project_id)
    
    # Filtrage des versions
    versions = [entry for entry in history if entry.get("type") == "version"]
    
    # Création du DataFrame
    data = []
    
    for version in versions:
        timestamp = datetime.fromisoformat(version.get("timestamp", ""))
        
        data.append({
            "id": version.get("id", ""),
            "timestamp": timestamp,
            "date": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "description": version.get("description", ""),
            "project_data": version.get("project_data", {})
        })
    
    # Tri par date (du plus récent au plus ancien)
    data.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return data
