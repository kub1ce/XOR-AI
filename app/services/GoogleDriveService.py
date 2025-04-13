from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload

import io
from datetime import datetime

from app.settings import secrets


class GoogleDriveService:
    """Google Drive service"""

    def __init__(self):
        self.SERVICE_ACCOUNT_FILE = f'{secrets.jsonId}.json'
        self.credentials = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
    
    def uploadFile(self, file_bytes: bytes, extre:bool = False) -> str:
        """Uploads file to google drive and returns file id"""

        file_metadata = {
            'name': f'OCR_TEMP_FILE_{int(datetime.now().timestamp())}.jpg',
            'parents': [secrets.folderId]
        }

        if extre: file_metadata['mimeType'] =  'application/vnd.google-apps.document'

        media = MediaIoBaseUpload(
            io.BytesIO(file_bytes),
            mimetype='image/jpeg',
            resumable=True
        )
        file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        fileID = file.get('id')

        self.drive_service.permissions().create(
            fileId=fileID,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()

        return fileID
    
    def deleteFile(self, file_id: str) -> None:
        """Deletes file from google drive"""
        self.drive_service.files().delete(fileId=file_id).execute()

    async def imageToTextExtractor(self, file_bytes: bytes) -> str:
        """Extracts text from image"""
        
        doc_id = self.uploadFile(file_bytes, extre=True)

        result = self.drive_service.files().export(
            fileId=doc_id,
            mimeType='text/plain'
        ).execute()
        
        self.deleteFile(doc_id)
        
        return result.decode('utf-8')

googleDriveService = GoogleDriveService()