"""
Module d'initialisation NLTK pour l'analyse de densité qualitative.

Ce script télécharge automatiquement les ressources NLTK nécessaires
pour l'analyse de densité qualitative lors du premier démarrage de l'application.
"""

import streamlit as st
import nltk
import os

def download_nltk_resources():
    """
    Télécharge les ressources NLTK nécessaires pour l'analyse de densité qualitative.
    Cette fonction est appelée au démarrage de l'application.
    """
    # Liste des ressources NLTK nécessaires
    resources = [
        'punkt',           # Pour la tokenization des phrases et des mots
        'stopwords',       # Pour la liste des mots vides
        'averaged_perceptron_tagger',  # Pour l'étiquetage grammatical
        'wordnet'          # Pour l'analyse sémantique
    ]
    
    # Vérification du dossier NLTK_DATA
    nltk_data_dir = os.path.expanduser('~/nltk_data')
    os.makedirs(nltk_data_dir, exist_ok=True)
    
    # Téléchargement des ressources
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
            st.write(f"✅ Ressource NLTK '{resource}' déjà installée.")
        except LookupError:
            st.write(f"⏳ Téléchargement de la ressource NLTK '{resource}'...")
            nltk.download(resource, quiet=True)
            st.write(f"✅ Ressource NLTK '{resource}' installée avec succès.")

# Fonction à appeler au démarrage de l'application
def initialize_nltk():
    """
    Initialise NLTK en téléchargeant les ressources nécessaires.
    Cette fonction doit être appelée au démarrage de l'application.
    """
    # Vérification si les ressources NLTK sont déjà téléchargées
    try:
        # Tentative d'accès à une ressource NLTK
        nltk.data.find('tokenizers/punkt')
        # Si aucune erreur n'est levée, les ressources sont déjà téléchargées
        return
    except LookupError:
        # Si une erreur est levée, les ressources doivent être téléchargées
        with st.spinner("Initialisation des ressources linguistiques pour l'analyse de densité..."):
            download_nltk_resources()
        st.success("Initialisation terminée ! L'analyse de densité qualitative est maintenant disponible.")

if __name__ == "__main__":
    # Test de la fonction d'initialisation
    initialize_nltk()
