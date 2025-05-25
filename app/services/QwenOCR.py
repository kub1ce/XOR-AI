import requests
import logging
from typing import Dict, Any, Optional

from app.settings import secrets
from app.services.GoogleDriveService import googleDriveService

from app.utils.errorHandler import api_error_handler
from app.utils.APIValidators import validateResponse

class QwenOCR:
   def __init__(self):
      self.api_key = secrets.ioKey
      self.url = "https://api.intelligence.io.solutions/api/v1/chat/completions"
      self.headers = {
         "Authorization": f"Bearer {self.api_key}",
         "Content-Type": "application/json",
      }
      self.model = "Qwen/Qwen2-VL-7B-Instruct"
      self.temperature = 0.1

   def _load_system_prompt(self) -> str:
         """Load the system prompt from a separate file."""
         try:
            with open("app/prompts/ocr_system_prompt.txt", "r", encoding="utf-8") as f:
               return f.read()
         except FileNotFoundError:
            logging.error("OCR system prompt file not found")
            return ""

   @api_error_handler(logger_name="Qwen-OCR")
   async def process_image(self, bytesimage: bytes, text: str = "") -> str:
         """
         Process an image using the Qwen OCR service.
         
         Args:
               bytesimage: The image bytes to process
               text: Optional text to include with the image
               
         Returns:
               str: The processed text result
         """
         file_id = googleDriveService.uploadFile(bytesimage)
         file_link = f"https://drive.google.com/uc?export=view&id={file_id}"

         try:
            resp = requests.post(
               self.url,
               headers=self.headers,
               json=self._build_payload(text, file_link)
            )

            if resp.status_code != 200:
               logging.error(f"API request failed with status {resp.status_code}")
               return "500"

            return validateResponse(resp.json())
         finally:
            googleDriveService.deleteFile(file_id)

   def _build_payload(self, text: str, file_link: Optional[str] = None) -> Dict[str, Any]:
      """
      Build the API request payload.
       
      Args:
         text: The text to include
         file_link: Optional link to the image file
            
      Returns:
         Dict containing the API request payload
      """
      content = [{"type": "text", "text": text}]
      if file_link:
         content.append({"type": "image_url", "image_url": {"url": file_link}})

      return {
         "model": self.model,
         "messages": [
               {
                  "role": "system",
                  "content": self._load_system_prompt()
               },
               {
                  "role": "user",
                  "content": content
               }
         ],
         "temperature": self.temperature
      }


qwenOCR = QwenOCR()
