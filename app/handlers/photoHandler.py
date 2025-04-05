from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from app.settings import bot
from app.services.GoogleOCR import drive_ocr
from app.services.QwenOCR import qwenOCR

import logging


# Временное хранилище данных пользователя
user_data = {}

imageRouter = Router(name="Images")

def get_check_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, проверить ещё раз", callback_data="confirm_check"),
            InlineKeyboardButton(text="❌ Нет, этого достаточно", callback_data="deny_check")
        ]
    ])

@imageRouter.message(F.photo)
async def message(msg: Message):

    photo = msg.photo[-1]
    file = await bot.download(photo)
    photo_bytes = file.read()

    user_data[msg.from_user.id] = {
        "photo_bytes": photo_bytes,
        "chat_id": msg.chat.id,
        "msg": msg
    }

    await msg.reply(
        "Нужна ли дополнительная проверка текста?\n" \
        "Она может занять больше времени. Также возможна небольшая корректировка текста (исправление опечаток, орфографии и т.п.)",
        reply_markup=get_check_buttons()
    )


@imageRouter.callback_query(F.data.endswith("_check"))
async def process_confirm_check(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = user_data.get(user_id)
    
    if not data:
        await callback.answer("Извините, время обработки истекло. Отправьте фото ещё раз.")
        return
    
    await callback.message.edit_reply_markup()
    
    try:
        await bot.set_message_reaction(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reaction=[{"type": "emoji", "emoji": "👀"}]
        )
    except Exception as e:
        logging.error()

    text=""
    
    try:
        text = await drive_ocr.process_image(data["photo_bytes"])
    except Exception as e:
        logging.error(e)

    if callback.data == "confirm_check":
        try:
            await bot.set_message_reaction(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reaction=[{"type": "emoji", "emoji": "💅"}]
            )
        except Exception as e:
            logging.error(e)
        text = qwenOCR.process_image(data["photo_bytes"], text)
    
    await data["msg"].reply(text)
    await callback.message.delete()
