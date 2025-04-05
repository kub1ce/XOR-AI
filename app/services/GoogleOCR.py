import io
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from app.settings import secrets

from random import randint

SERVICE_ACCOUNT_FILE = f'{secrets.jsonId}.json'

class DriveOCR:
    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        self.drive_service = build('drive', 'v3', credentials=self.credentials)

    async def process_image(self, file_bytes: bytes) -> str:
        
        file_metadata = {
            'name': f'OCR_TEMP_FILE_{randint(0, 10000000)}',
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [secrets.folderId]
        }
        media = MediaIoBaseUpload(
            io.BytesIO(file_bytes),
            mimetype='image/jpeg',
        )
        
        file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        doc_id = file.get('id')
        result = self.drive_service.files().export(
            fileId=doc_id,
            mimeType='text/plain'
        ).execute()
        
        self.drive_service.files().delete(fileId=doc_id).execute()
        
        return result.decode('utf-8')

drive_ocr = DriveOCR()