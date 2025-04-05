import requests
import logging, io
from random import randint

from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload

from app.settings import secrets

SERVICE_ACCOUNT_FILE = f'{secrets.jsonId}.json'

class QwenOCR:
    def __init__(self):
        self.api_key = secrets.gptKey
        self.url = "https://api.intelligence.io.solutions/api/v1/chat/completions"

        self.credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        self.drive_service = build('drive', 'v3', credentials=self.credentials)

        self.system_prompt = """Вы — профессиональный редактор OCR-текстов с доступом к исходному изображению. Ваша задача — максимально точно восстановить текст с картинки, сохраняя оригинальные особенности.

Инструкции:
1. Тщательно сравнивай присланный текст с визуальным содержанием изображения
2. Сохраняй все орфографические/пунктуационные ошибки, которые присутствуют в оригинале на картинке
3. Точно повторяй структуру оригинала: переносы строк, абзацы, отступы, выравнивание
4. Для формул используй Unicode-символы: ⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉∉∆∃∀∜<>±⇒⇐⇔△Δαεβσⁿ∅∈√∑∛∞∫∬≥≤⊥⋂⋿ и аналогичные
5. Запрещено: 
   - Исправлять намеренные ошибки дизайна
   - Заменять слова синонимами
   - Добавлять пояснения или комментарии
   - Менять порядок элементов без визуального подтверждения
   - Использовать markdown или дополнительное форматирование
6. Уделяй особую точность математическим/физическим формулам (смотри. пункт 4)

Особые случаи:
- Если текст отсутствует/не распознан — анализируй изображение самостоятельно
- Для многоязычных текстов сохраняй оригинальное языковое смешение
- Цифры/даты/коды воспроизводи точно как в оригинале

Формат ответа: 
ТОЛЬКО исправленный текст в чистом виде, без обрамляющих символов или пояснений. Сохраняй все переносы строк и пробелы из оригинала.

Пример корректного ответа:
12.03.2024 №325-ПД
∛x³ + ∑ⁿₖ₌₁ aₖ = ∞ 
Attention: срок действия 
докумнта истекает через 2 дня!"""

    def process_image(self, bytesimage:bytes, text:str="", photoId:str = str(randint(0, 2400))):

        # ? Image to GDrive & get link
        file_metadata = {
            'name': f'photo_{photoId}.jpg',
            'parents': [secrets.folderId]
        }

        media = MediaIoBaseUpload(io.BytesIO(bytesimage), 
                                mimetype='image/jpeg',
                                resumable=True)

        uploaded_file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        file_id = uploaded_file.get('id')

        # Устанавливаем разрешение на доступ для всех
        self.drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()

        file_link = f"https://drive.google.com/uc?export=view&id={file_id}"

        # ? ==========

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "Qwen/Qwen2-VL-7B-Instruct",
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                        {"type": "image_url", "image_url": {"url": file_link}}
                    ]
                },
            ],
            "temperature": 0.2
        }


        response = requests.post(self.url, json=data, headers=headers, timeout=1000)
        self.drive_service.files().delete(fileId=file_id).execute()

        try:
            return response.json()["choices"][0]["message"]['content']
        except Exception as e:
            logging.error(e)
            try:
                logging.warning(response.__dict__)
            except:
                logging.warning("Не привести ответ в формат JSON")

            return "Произошла ошибка"

qwenOCR = QwenOCR()
