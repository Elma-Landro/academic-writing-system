"""
Module de gestion des fichiers Google Drive.
Permet la sauvegarde et le chargement des données de projet dans Google Drive.
"""

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
import json
import os
import streamlit as st

class DriveManager:
    """Gestionnaire de fichiers Google Drive pour la persistance des projets."""
    
    def __init__(self, credentials):
        """Initialise le gestionnaire avec les identifiants Google."""
        self.service = build('drive', 'v3', credentials=credentials)
        self.app_folder_id = self._get_or_create_app_folder()
    
    def _get_or_create_app_folder(self):
        """Récupère ou crée le dossier principal de l'application."""
        folder_name = "Academic_Writing_System"
        
        # Recherche du dossier
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(q=query, spaces='drive').execute()
        
        # Si le dossier existe, on retourne son ID
        if results.get('files'):
            return results['files'][0]['id']
        
        # Sinon, on crée le dossier
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self.service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')
    
    def get_or_create_project_folder(self, project_id, project_name):
        """Récupère ou crée un dossier pour un projet spécifique."""
        folder_name = f"{project_id}_{project_name}"
        
        # Recherche du dossier
        query = f"name='{folder_name}' and '{self.app_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(q=query, spaces='drive').execute()
        
        # Si le dossier existe, on retourne son ID
        if results.get('files'):
            return results['files'][0]['id']
        
        # Sinon, on crée le dossier
        folder_metadata = {
            'name': folder_name,
            'parents': [self.app_folder_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self.service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')
    
    def save_project_data(self, project_id, project_name, data, file_name="project_data.json"):
        """Sauvegarde les données d'un projet dans Google Drive."""
        # Récupération ou création du dossier du projet
        folder_id = self.get_or_create_project_folder(project_id, project_name)
        
        # Recherche du fichier s'il existe déjà
        query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
        results = self.service.files().list(q=query, spaces='drive').execute()
        
        # Use BytesIO instead of filesystem
        import tempfile
        import uuid
        
        # Create secure temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            file_path = f.name
        
        media = MediaFileUpload(file_path, mimetype='application/json')
        
        if results.get('files'):
            # Mise à jour du fichier existant
            file_id = results['files'][0]['id']
            self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
        else:
            # Création d'un nouveau fichier
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
        
        # Nettoyage du fichier temporaire
        os.remove(file_path)
    
    def load_project_data(self, project_id, project_name, file_name="project_data.json"):
        """Charge les données d'un projet depuis Google Drive."""
        # Récupération du dossier du projet
        folder_id = self.get_or_create_project_folder(project_id, project_name)
        
        # Recherche du fichier
        query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
        results = self.service.files().list(q=query, spaces='drive').execute()
        
        if not results.get('files'):
            return None
        
        file_id = results['files'][0]['id']
        request = self.service.files().get_media(fileId=file_id)
        
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        done = False
        
        while not done:
            _, done = downloader.next_chunk()
        
        file_content.seek(0)
        return json.loads(file_content.read().decode('utf-8'))
    
    def save_version(self, project_id, project_name, version_data, version_name):
        """Sauvegarde une version spécifique d'un projet."""
        file_name = f"version_{version_name}.json"
        self.save_project_data(project_id, project_name, version_data, file_name)
    
    def list_project_versions(self, project_id, project_name):
        """Liste toutes les versions d'un projet."""
        folder_id = self.get_or_create_project_folder(project_id, project_name)
        
        query = f"'{folder_id}' in parents and name contains 'version_' and trashed=false"
        results = self.service.files().list(q=query, spaces='drive').execute()
        
        versions = []
        for file in results.get('files', []):
            version_name = file['name'].replace('version_', '').replace('.json', '')
            versions.append({
                'name': version_name,
                'file_id': file['id'],
                'modified_time': file.get('modifiedTime')
            })
        
        return sorted(versions, key=lambda x: x.get('modified_time', ''), reverse=True)
