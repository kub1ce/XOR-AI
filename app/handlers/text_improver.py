import requests
from app.settings import secrets

class TextImprover:
    def __init__(self):
        self.api_key = secrets.gptKey

    def improve_text(self, text):
        url = "https://api.intelligence.io.solutions/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "deepseek-ai/DeepSeek-R1",
            "messages": [
                {
                    "role": "system",
                    "content": "Исправь орфографию и пунктуацию, сохраняя оригинальный смысл. В качесве ответета верни ТОЛЬКО исправленный текст. Запрещаются ЛЮБЫЕ комментарии."
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        }

        response = requests.post(url, json=data, headers=headers)

        return response.json()["choices"][0]["message"]['content'].split("</think>\n\n")[1]

textImprover = TextImprover()
