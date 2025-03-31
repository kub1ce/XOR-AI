from pydantic_settings import BaseSettings
from aiogram import Bot

from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode


class Secrets(BaseSettings):  
    token: str
    jsonId: str
    folderId: str

    class Config:  
        env_file = ".env"  
        env_file_encoding = "utf-8"

secrets = Secrets()

bot = Bot(token=secrets.token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
