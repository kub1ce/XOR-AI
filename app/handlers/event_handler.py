from aiogram.types import Message
from app.settings import bot

async def message(msg: Message):
    if msg.text == "/start":
        await bot.send_message(msg.from_user.id, "Crocodillo Bombordiro")
    elif msg.photo:
        await bot.send_photo(msg.from_user.id, msg.photo[-1].file_id)