"""  
Основной модуль бота.  

Инициализирует диспетчер и подключает все роутеры из пакета `routers`.  
"""

import asyncio
import logging

from aiogram import Dispatcher, types
from aiogram.methods import DeleteWebhook

from aiogram.filters import Command


from app.settings import bot
from app.handlers import routers


logging.basicConfig(
    level=logging.INFO,
    filename="log.log",
    encoding="utf-8"
)

dp = Dispatcher()

async def start():

    dp.include_routers(*routers)    

    try:  
        await bot(DeleteWebhook(drop_pending_updates=True))  
        await dp.start_polling(bot)  
    finally:  
        await bot.session.close()  

if __name__ == "__main__":  
    print(">>> Bot started")
    
    asyncio.run(start())
