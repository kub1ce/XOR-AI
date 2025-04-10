from aiogram import Router, filters, types
from aiogram.types import Message

greetingRouter = Router(name="Start")

@greetingRouter.message(filters.CommandStart())
async def greeting(msg: Message):
        await msg.answer("Crocodillo Bombordiro")

