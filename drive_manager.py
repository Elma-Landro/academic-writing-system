
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import mimetypes

class GoogleDriveManager:
    """Gestionnaire Google Drive complet pour l'intégration avec le système d'écriture."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.service = None
        
    def _get_service(self):
        """Initialise le service Google Drive avec gestion d'erreurs."""
        try:
            from auth_manager import auth_manager
            
            credentials = auth_manager.get_credentials()
            if not credentials:
                raise ValueError("Aucun credentials Google Drive disponible")
            
            self.service = build('drive', 'v3', credentials=credentials)
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur initialisation service Drive: {e}")
            st.error(f"Impossible de se connecter à Google Drive: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Teste la connexion à Google Drive."""
        try:
            if not self._get_service():
                return False
            
            # Test simple: récupérer les informations du compte
            about = self.service.about().get(fields="user").execute()
            user = about.get('user', {})
            
            self.logger.info(f"Connexion Drive réussie pour {user.get('emailAddress', 'utilisateur inconnu')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Test connexion Drive échoué: {e}")
            return False
    
    def list_files(self, folder_id: str = None, mime_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Liste les fichiers dans Google Drive avec filtres optionnels."""
        try:
            if not self._get_service():
                return []
            
            # Construction de la requête
            query_parts = []
            
            if folder_id:
                query_parts.append(f"'{folder_id}' in parents")
            
            if mime_type:
                query_parts.append(f"mimeType='{mime_type}'")
            
            # Exclure les fichiers supprimés
            query_parts.append("trashed=false")
            
            query = " and ".join(query_parts) if query_parts else "trashed=false"
            
            # Exécution de la requête
            results = self.service.files().list(
                q=query,
                pageSize=limit,
                fields="files(id,name,mimeType,modifiedTime,size,parents,webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            
            # Formatage des résultats
            formatted_files = []
            for file in files:
                formatted_files.append({
                    'id': file.get('id'),
                    'name': file.get('name'),
                    'mime_type': file.get('mimeType'),
                    'modified_time': file.get('modifiedTime'),
                    'size': file.get('size'),
                    'parents': file.get('parents', []),
                    'web_view_link': file.get('webViewLink')
                })
            
            return formatted_files
            
        except HttpError as e:
            self.logger.error(f"Erreur HTTP Drive: {e}")
            st.error(f"Erreur lors de la récupération des fichiers: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Erreur listage fichiers Drive: {e}")
            st.error(f"Erreur inattendue: {e}")
            return []
    
    def download_file(self, file_id: str) -> Optional[str]:
        """Télécharge un fichier depuis Google Drive."""
        try:
            if not self._get_service():
                return None
            
            # Récupération des métadonnées du fichier
            file_metadata = self.service.files().get(fileId=file_id).execute()
            mime_type = file_metadata.get('mimeType')
            
            # Gestion des documents Google (conversion nécessaire)
            if mime_type == 'application/vnd.google-apps.document':
                # Export en format texte
                request = self.service.files().export_media(
                    fileId=file_id,
                    mimeType='text/plain'
                )
            elif mime_type == 'application/vnd.google-apps.spreadsheet':
                # Export en CSV
                request = self.service.files().export_media(
                    fileId=file_id,
                    mimeType='text/csv'
                )
            else:
                # Téléchargement direct pour les autres types
                request = self.service.files().get_media(fileId=file_id)
            
            # Téléchargement du contenu
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            # Conversion en texte
            content = file_io.getvalue().decode('utf-8', errors='ignore')
            
            self.logger.info(f"Fichier téléchargé avec succès: {file_metadata.get('name')}")
            return content
            
        except HttpError as e:
            self.logger.error(f"Erreur HTTP téléchargement: {e}")
            st.error(f"Erreur lors du téléchargement: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erreur téléchargement fichier: {e}")
            st.error(f"Erreur inattendue lors du téléchargement: {e}")
            return None
    
    def upload_file(self, file_name: str, content: str, folder_id: str = None, mime_type: str = 'text/plain') -> Optional[str]:
        """Upload un fichier vers Google Drive."""
        try:
            if not self._get_service():
                return None
            
            # Préparation des métadonnées
            file_metadata = {
                'name': file_name
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Préparation du contenu
            media = MediaIoBaseUpload(
                io.BytesIO(content.encode('utf-8')),
                mimetype=mime_type
            )
            
            # Upload du fichier
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            
            file_id = file.get('id')
            self.logger.info(f"Fichier uploadé avec succès: {file_name} (ID: {file_id})")
            
            return file_id
            
        except HttpError as e:
            self.logger.error(f"Erreur HTTP upload: {e}")
            st.error(f"Erreur lors de l'upload: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erreur upload fichier: {e}")
            st.error(f"Erreur inattendue lors de l'upload: {e}")
            return None
    
    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> Optional[str]:
        """Crée un dossier dans Google Drive."""
        try:
            if not self._get_service():
                return None
            
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id,name'
            ).execute()
            
            folder_id = folder.get('id')
            self.logger.info(f"Dossier créé avec succès: {folder_name} (ID: {folder_id})")
            
            return folder_id
            
        except HttpError as e:
            self.logger.error(f"Erreur HTTP création dossier: {e}")
            st.error(f"Erreur lors de la création du dossier: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erreur création dossier: {e}")
            st.error(f"Erreur inattendue lors de la création du dossier: {e}")
            return None
    
    def search_files(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Recherche des fichiers dans Google Drive."""
        try:
            if not self._get_service():
                return []
            
            # Construction de la requête de recherche
            search_query = f"name contains '{query}' and trashed=false"
            
            results = self.service.files().list(
                q=search_query,
                pageSize=limit,
                fields="files(id,name,mimeType,modifiedTime,webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            
            # Formatage des résultats
            formatted_files = []
            for file in files:
                formatted_files.append({
                    'id': file.get('id'),
                    'name': file.get('name'),
                    'mime_type': file.get('mimeType'),
                    'modified_time': file.get('modifiedTime'),
                    'web_view_link': file.get('webViewLink')
                })
            
            return formatted_files
            
        except HttpError as e:
            self.logger.error(f"Erreur HTTP recherche: {e}")
            st.error(f"Erreur lors de la recherche: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Erreur recherche fichiers: {e}")
            st.error(f"Erreur inattendue lors de la recherche: {e}")
            return []
    
    def update_file_content(self, file_id: str, content: str) -> bool:
        """Met à jour le contenu d'un fichier existant."""
        try:
            if not self._get_service():
                return False
            
            # Préparation du nouveau contenu
            media = MediaIoBaseUpload(
                io.BytesIO(content.encode('utf-8')),
                mimetype='text/plain'
            )
            
            # Mise à jour du fichier
            self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            
            self.logger.info(f"Contenu du fichier mis à jour avec succès: {file_id}")
            return True
            
        except HttpError as e:
            self.logger.error(f"Erreur HTTP mise à jour: {e}")
            st.error(f"Erreur lors de la mise à jour: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erreur mise à jour fichier: {e}")
            st.error(f"Erreur inattendue lors de la mise à jour: {e}")
            return False
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les métadonnées d'un fichier."""
        try:
            if not self._get_service():
                return None
            
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields="id,name,mimeType,size,modifiedTime,createdTime,webViewLink,parents"
            ).execute()
            
            return {
                'id': file_metadata.get('id'),
                'name': file_metadata.get('name'),
                'mime_type': file_metadata.get('mimeType'),
                'size': file_metadata.get('size'),
                'modified_time': file_metadata.get('modifiedTime'),
                'created_time': file_metadata.get('createdTime'),
                'web_view_link': file_metadata.get('webViewLink'),
                'parents': file_metadata.get('parents', [])
            }
            
        except HttpError as e:
            self.logger.error(f"Erreur HTTP métadonnées: {e}")
            st.error(f"Erreur lors de la récupération des métadonnées: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erreur récupération métadonnées: {e}")
            st.error(f"Erreur inattendue lors de la récupération des métadonnées: {e}")
            return None

# Instance globale
drive_manager = GoogleDriveManager()

# Fonctions d'interface pour compatibilité
def test_drive_connection() -> bool:
    return drive_manager.test_connection()

def list_drive_files(folder_id: str = None, mime_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    return drive_manager.list_files(folder_id, mime_type, limit)

def download_drive_file(file_id: str) -> Optional[str]:
    return drive_manager.download_file(file_id)

def upload_to_drive(file_name: str, content: str, folder_id: str = None) -> Optional[str]:
    return drive_manager.upload_file(file_name, content, folder_id)

def search_drive_files(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    return drive_manager.search_files(query, limit)
