from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.exceptions import TelegramAPIError

from app.settings import bot
from app.services.GoogleDriveService import googleDriveService
from app.services.QwenOCR import qwenOCR
from app.services.TextImprover import textImprover

import logging

ERROR_MESSAGES = {
    "processing": (
        "Извините, произошла ошибка при обработке фото. Пожалуйста, убедитесь, что:\n"
        "1. Фото четкое и хорошо освещенное\n"
        "2. Текст на фото читаемый\n"
        "3. Фото не повреждено\n\n"
        "Попробуйте отправить фото еще раз или нажмите кнопку ниже для повторной попытки."
    ),
    "text": "Не удалось распознать текст(("
}

REACTIONS = {
    "processing": "👀",
    "improving": "💅"
}

user_data = {} # Временное хранилище данных

imageRouter = Router(name="Images")

def get_improve_buttons() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками улучшения и повтора"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✨ Улучшить распознавание", callback_data="improve_text"),
            InlineKeyboardButton(text="🔄 Повторить", callback_data="retry_processing")
        ]
    ])

def get_retry_button() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопкой повтора"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Повторить", callback_data="retry_improve")]
    ])

def is_valid_text(text: str) -> bool:
    """Проверяет, является ли текст валидным для отправки в Telegram"""
    return isinstance(text, str) and len(text.strip()) > 1

async def send_error_message(message: Message, error_type: str = "processing") -> None:
    """Отправляет сообщение об ошибке с кнопкой повтора"""
    try:
        await message.reply(
            ERROR_MESSAGES[error_type],
            reply_markup=get_retry_button()
        )
    except TelegramAPIError as e:
        logging.error(f"Ошибка при отправке сообщения об ошибке: {e}")

async def set_reaction(message: Message, emoji: str) -> None:
    """Устанавливает реакцию на сообщение"""
    try:
        await bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[{"type": "emoji", "emoji": emoji}]
        )
    except TelegramAPIError as e:
        logging.error(f"Ошибка при установке реакции: {e}")

@imageRouter.message(F.photo)
async def handle_photo(msg: Message) -> None:
    """Обработчик входящих фотографий"""
    try:
        photo = msg.photo[-1]
        file = await bot.download(photo)
        photo_bytes = file.read()

        user_data[msg.from_user.id] = {
            "photo_bytes": photo_bytes,
            "chat_id": msg.chat.id,
            "msg": msg
        }

        await set_reaction(msg, REACTIONS["processing"])

        try:
            text = await googleDriveService.imageToTextExtractor(photo_bytes)
            if not is_valid_text(text):
                raise ValueError("Не удалось распознать текст")
            
            await msg.reply(text, reply_markup=get_improve_buttons())
        except Exception as e:
            logging.error(f"Ошибка при распознавании текста: {e}")
            await send_error_message(msg)
    except Exception as e:
        logging.error(f"Ошибка при обработке фото: {e}")
        await send_error_message(msg)

@imageRouter.callback_query(F.data == "improve_text")
@imageRouter.callback_query(F.data == "retry_improve")
async def improve_text(callback: CallbackQuery) -> None:
    """Обработчик улучшения текста"""
    user_id = callback.from_user.id
    data = user_data.get(user_id)
    
    if not data:
        await callback.answer("Извините, время обработки истекло. Отправьте фото ещё раз.")
        return
    
    await callback.message.edit_reply_markup()
    await set_reaction(callback.message, REACTIONS["improving"])

    try:
        original_text = callback.message.text
        if not is_valid_text(original_text):
            raise ValueError("Не удалось получить текст")

        improved_text = await qwenOCR.process_image(data["photo_bytes"], original_text)
        if not is_valid_text(improved_text):
            raise ValueError("Не удалось улучшить текст")

        await data["msg"].reply(improved_text, reply_markup=get_retry_button())
    except Exception as e:
        logging.error(f"Ошибка при улучшении текста: {e}")
        await send_error_message(callback.message, "text")
    finally:
        await callback.message.delete()

@imageRouter.callback_query(F.data == "retry_processing")
async def retry_processing(callback: CallbackQuery) -> None:
    """Обработчик повторной обработки фото"""
    user_id = callback.from_user.id
    data = user_data.get(user_id)
    
    if not data:
        await callback.answer("Извините, время обработки истекло. Отправьте фото ещё раз.")
        return
    
    await callback.message.edit_reply_markup()
    await set_reaction(callback.message, REACTIONS["processing"])

    try:
        text = await googleDriveService.imageToTextExtractor(data["photo_bytes"])
        if not is_valid_text(text):
            raise ValueError("Не удалось распознать текст")
        
        await data["msg"].reply(text, reply_markup=get_improve_buttons())
    except Exception as e:
        logging.error(f"Ошибка при повторной обработке: {e}")
        await send_error_message(callback.message)
    finally:
        await callback.message.delete()