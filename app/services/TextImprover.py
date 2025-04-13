import requests
from app.settings import secrets
import aiohttp

from app.utils.errorHandler import api_error_handler
from app.utils.APIValidators import validateResponse

class TextImprover:
    def __init__(self):
        self.api_key = secrets.gptKey
        self.url = "https://api.intelligence.io.solutions/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.model = "deepseek-ai/DeepSeek-R1"
        self.defaultSystemPrompt = "Исправь орфографию и пунктуацию, сохраняя оригинальный смысл. В качесве ответета верни ТОЛЬКО исправленный текст. Запрещаются ЛЮБЫЕ комментарии. Исправление стиля и вписывание своих слов запрещено. Запрещено изменеие слов синонимами".upper()
        self.temperature = 0.1

    @api_error_handler(logger_name= "improveText")
    async def improveText(self, text: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url, 
                json=self._build_payload(text),
                headers=self.headers
            ) as response:
                response_data = await response.json()
                validated = validateResponse(response_data)
                return validated.split("</think>")[-1].strip() or "&"
    
    def _build_payload(self, text: str) -> dict:
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.defaultSystemPrompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": self.temperature
        }

textImprover = TextImprover()
