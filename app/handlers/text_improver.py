import requests
from app.settings import secrets
import logging

class TextImprover:
    def __init__(self):
        self.api_key = secrets.gptKey

    def improve_text(self, text):
        url = "https://api.intelligence.io.solutions/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        logging.info(text)

        data = {
            "model": "deepseek-ai/DeepSeek-R1",
            "messages": [
                {
                    "role": "system",
                    "content": "Исправь орфографию и пунктуацию, сохраняя оригинальный смысл. В качесве ответета верни ТОЛЬКО исправленный текст. Запрещаются ЛЮБЫЕ комментарии. Исправление стиля и вписывание своих слов запрещено. Запрещено изменеие слов синонимами".upper()
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.1
        }

        response = requests.post(url, json=data, headers=headers)
        print(response.text)

        try:
            return response.json()["choices"][0]["message"]['content'].split("</think>\n\n")[1]
        
        except Exception as e:
            logging.error(e)
            logging.warning(response.json())

            return text

textImprover = TextImprover()
