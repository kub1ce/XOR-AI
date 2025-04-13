from pydantic import BaseModel, ValidationError
import logging

class QwenResponse(BaseModel):
    content: str
    status: int = 200

def validateResponse(response_data: dict) -> str:
    try:
        if "choices" not in response_data:
            raise ValidationError("Invalid API response structure")
        
        message = response_data["choices"][0]["message"]
        return QwenResponse(**message).content
    except (KeyError, IndexError, ValidationError) as e:
        logging.error(e)
        return "&"