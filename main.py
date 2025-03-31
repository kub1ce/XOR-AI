import asyncio

from aiogram import Dispatcher
from aiogram.methods import DeleteWebhook

from app.settings import bot
from app.handlers import event_handler


async def start():  
    dp = Dispatcher()

    dp.message.register(event_handler.message)


    try:  
        await bot(DeleteWebhook(drop_pending_updates=True))  
        await dp.start_polling(bot)  
    finally:  
        await bot.session.close()  


if __name__ == "__main__":  
    print(">>> Bot started")
    asyncio.run(start())