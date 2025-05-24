"""
Module de gestion de la sédimentation contextuelle.
Permet de suivre l'évolution des projets à travers les différentes étapes.
"""

import streamlit as st
from datetime import datetime
import json
from auth_manager import get_credentials
from drive_manager import DriveManager

class SedimentationManager:
    """Gestionnaire de sédimentation pour le suivi de l'évolution des projets."""
    
    def __init__(self):
        """Initialise le gestionnaire de sédimentation."""
        self.credentials = get_credentials()
        if self.credentials:
            self.drive_manager = DriveManager(self.credentials)
        else:
            self.drive_manager = None
    
    def save_project_state(self, project_id, project_name, data, stage):
        """Sauvegarde l'état actuel d'un projet à une étape spécifique."""
        if not self.drive_manager:
            st.error("Vous devez être connecté pour sauvegarder l'état du projet.")
            return False
        
        # Ajout des métadonnées de sédimentation
        timestamp = datetime.now().isoformat()
        sedimentation_data = {
            "project_data": data,
            "metadata": {
                "stage": stage,
                "timestamp": timestamp,
                "version": data.get("version", 1) + 1
            }
        }
        
        # Sauvegarde de l'état actuel
        self.drive_manager.save_project_data(project_id, project_name, sedimentation_data)
        
        # Sauvegarde d'une version spécifique pour cette étape
        version_name = f"{stage}_{timestamp.replace(':', '-')}"
        self.drive_manager.save_version(project_id, project_name, sedimentation_data, version_name)
        
        return True
    
    def load_latest_project_state(self, project_id, project_name):
        """Charge l'état le plus récent d'un projet."""
        if not self.drive_manager:
            st.error("Vous devez être connecté pour charger l'état du projet.")
            return None
        
        data = self.drive_manager.load_project_data(project_id, project_name)
        return data.get("project_data") if data else None
    
    def get_project_history(self, project_id, project_name):
        """Récupère l'historique complet d'un projet."""
        if not self.drive_manager:
            st.error("Vous devez être connecté pour accéder à l'historique du projet.")
            return []
        
        versions = self.drive_manager.list_project_versions(project_id, project_name)
        
        history = []
        for version in versions:
            version_data = self.drive_manager.load_project_data(
                project_id, 
                project_name, 
                f"version_{version['name']}.json"
            )
            if version_data:
                history.append({
                    "version_name": version['name'],
                    "metadata": version_data.get("metadata", {}),
                    "data": version_data.get("project_data", {})
                })
        
        return history
    
    def visualize_sedimentation(self, project_id, project_name):
        """Génère une visualisation de la sédimentation du projet."""
        history = self.get_project_history(project_id, project_name)
        
        if not history:
            st.info("Aucun historique disponible pour ce projet.")
            return
        
        # Affichage de la timeline de sédimentation
        st.subheader("Timeline de sédimentation du projet")
        
        for i, version in enumerate(history):
            metadata = version.get("metadata", {})
            stage = metadata.get("stage", "inconnu")
            timestamp = metadata.get("timestamp", "")
            
            if timestamp:
                try:
                    date_obj = datetime.fromisoformat(timestamp)
                    formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
                except:
                    formatted_date = timestamp
            else:
                formatted_date = "Date inconnue"
            
            with st.expander(f"{i+1}. {stage} - {formatted_date}"):
                st.json(version.get("data", {}))
                
                if i < len(history) - 1:
                    if st.button(f"Restaurer cette version", key=f"restore_{i}"):
                        self.restore_version(project_id, project_name, version)
                        st.success("Version restaurée avec succès!")
                        st.experimental_rerun()
    
    def restore_version(self, project_id, project_name, version):
        """Restaure une version spécifique d'un projet."""
        if not self.drive_manager:
            st.error("Vous devez être connecté pour restaurer une version.")
            return False
        
        # Sauvegarde de la version actuelle avant restauration
        current_data = self.load_latest_project_state(project_id, project_name)
        if current_data:
            self.save_project_state(
                project_id,
                project_name,
                current_data,
                "pre_restore_backup"
            )
        
        # Restauration de la version sélectionnée
        project_data = version.get("data", {})
        if project_data:
            self.save_project_state(
                project_id,
                project_name,
                project_data,
                f"restored_from_{version.get('version_name', 'unknown')}"
            )
            return True
        
        return False
