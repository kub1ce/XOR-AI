import requests, base64
from app.settings import secrets

class QwenOCR:
    def __init__(self):
        self.api_key = secrets.gptKey
    
    def process_image(self, file_bytes: bytes):

        url = "https://api.intelligence.io.solutions/api/v1/chat/completions"

        file_bytes = base64.b64encode(file_bytes.getvalue()).decode("utf-8")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", 
            "messages": [
                {"role": "system", "content": ""},
                {"role": "user", "content": [
                    {"type": "text", "text": "image to text. Could be on different languages. Give the answer on the same language"},
                    {"type": "image", "image": file_bytes}
                ]}
            ]}
        
        response = requests.post(url, json=data, headers=headers)

        return response.json()

qwenOCR = QwenOCR()
