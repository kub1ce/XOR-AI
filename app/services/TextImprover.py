import logging
from typing import Dict, Any, Optional

import aiohttp
from app.settings import secrets
from app.utils.errorHandler import api_error_handler
from app.utils.APIValidators import validateResponse

class TextImprover:
    def __init__(self):
        self.api_key = secrets.ioKey
        self.url = "https://api.intelligence.io.solutions/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.model = "deepseek-ai/DeepSeek-R1"
        self.temperature = 0.1
        self._prompts = self._load_system_prompts()

    def _load_system_prompts(self) -> Dict[str, str]:
        """Load system prompts from the prompts file."""
        try:
            with open("app/prompts/text_improver_prompts.txt", "r", encoding="utf-8") as f:
                content = f.read()
                prompts = {}
                current_section = None
                current_content = []
                
                for line in content.split('\n'):
                    if line.startswith('[') and line.endswith(']'):
                        if current_section:
                            prompts[current_section] = '\n'.join(current_content).strip()
                        current_section = line[1:-1]
                        current_content = []
                    elif line.strip() and current_section:
                        current_content.append(line)
                
                if current_section:
                    prompts[current_section] = '\n'.join(current_content).strip()
                
                return prompts
        except FileNotFoundError:
            logging.error("Text improver prompts file not found")
            return {}

    @api_error_handler(logger_name="improveText")
    async def improve_text(self, text: str) -> str:
        """
        Improve text by fixing spelling and punctuation while preserving the original meaning.
        
        Args:
            text: The text to improve
            
        Returns:
            str: The improved text
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url, 
                json=self._build_payload(text, "IMPROVE_TEXT"),
                headers=self.headers
            ) as response:
                response_data = await response.json()
                validated = validateResponse(response_data)
                return validated.split("</think>")[-1].strip() or "&"

    @api_error_handler(logger_name="summarizeText")
    async def summarize_text(self, text: str) -> str:
        """
        Create a brief summary of the text while preserving main ideas and key points.
        
        Args:
            text: The text to summarize
            
        Returns:
            str: The summarized text
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url, 
                json=self._build_payload(text, "SUMMARIZE_TEXT"),
                headers=self.headers
            ) as response:
                response_data = await response.json()
                validated = validateResponse(response_data)
                return validated.split("</think>")[-1].strip() or "&"

    def _build_payload(self, text: str, prompt_type: str) -> Dict[str, Any]:
        """
        Build the API request payload.
        
        Args:
            text: The text to process
            prompt_type: Type of prompt to use (IMPROVE_TEXT or SUMMARIZE_TEXT)
            
        Returns:
            Dict containing the API request payload
        """
        system_prompt = self._prompts.get(prompt_type, "")
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": self.temperature
        }

textImprover = TextImprover()
