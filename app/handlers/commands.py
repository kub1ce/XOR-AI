from aiogram import Router, filters, types
from aiogram.types import Message

commandsRouter = Router(name="Commands")

@commandsRouter.message(filters.CommandStart())
async def greeting(msg: Message):
        await msg.answer("Crocodillo Bombordiro")


@commandsRouter.message(filters.Command("help"))
async def help(msg: Message):
    await msg.answer("Тут будет помощь. Пока что нет.")


@commandsRouter.message(filters.Command("settings"))
async def settings(msg: Message):
    await msg.answer("Тут будут настройки. Пока что нет.")





