from aiogram import Router, F, enums
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.exceptions import TelegramAPIError

from app.settings import bot
from app.services.GoogleDriveService import googleDriveService
from app.services.QwenOCR import qwenOCR
from app.services.TextImprover import textImprover
from app.utils.document_utils import convert_and_send_text
from app.settings_manager import settings_manager
import logging

ERROR_MESSAGE = \
    "❌ Не удалось распознать текст\n\n" \
    "Советы для лучшего распознавания:\n" \
    "• Снимайте фото при хорошем освещении, без наклона.\n" \
    "• Большие документы отправляйте файлом.\n" \
    "• Если текст распознался плохо, попробуйте переснять или выбрать доп. обработку."


REACTIONS = {
    "processing": "👀",
    "improving": "💅"
}

user_data = {} # Временное хранилище данных

imageRouter = Router(name="Images")

def get_improve_buttons() -> InlineKeyboardMarkup:
    """Создает клавиатуру кнопками доп. обработки и сохранения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "доп. обработка", callback_data="improve_text")],
        [InlineKeyboardButton(text = "перевести", callback_data="translate_text")],
        [InlineKeyboardButton(text = "пересказать", callback_data="summarize_text")],
        [InlineKeyboardButton(text = "сохранить", callback_data="save")],
    ])

def is_valid_text(text: str) -> bool:
    """Проверяет, является ли текст валидным для отправки в Telegram"""
    return isinstance(text, str) and len(text.strip()) > 1

async def send_error_message(message: Message) -> None:
    """Отправляет сообщение об ошибке с кнопкой повтора"""
    try:
        await message.reply(
            ERROR_MESSAGE
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

def get_text_from_message(message: Message) -> str:
    """Извлекает текст из сообщения"""
    return message.html_text.split('<pre><code class="language-XOR-AI">')[1].split('</code></pre>')[0]

@imageRouter.message(F.photo)
async def handle_photo(msg: Message) -> None:
    """Обработчик входящих фотографий"""
    try: # TODO: Добавить обработку ошибок
        # Получаем фотографию из сообщения
        photo = msg.photo[-1]
        file = await bot.download(photo)
        photo_bytes = file.read()

        user_data[msg.from_user.id] = {
            "photo_bytes": photo_bytes,
            "chat_id": msg.chat.id,
            "msg": msg
        }
    except Exception as e:
        logging.error(f"Ошибка при обработке фото: {e}")
        await send_error_message(msg)
        return

    await set_reaction(msg, REACTIONS["processing"])

    # 1. Распознаем текст через Google OCR
    try:
        text = await googleDriveService.imageToTextExtractor(photo_bytes)
        if not is_valid_text(text):
            raise ValueError("Не удалось распознать текст")
        
    except Exception as e:
        logging.error(f"Ошибка при распознавании текста: {e}")
        await send_error_message(msg)
        return

    # 2. Отправляем текст в Telegram
    if not is_valid_text(text):
        await send_error_message(msg)
    else:
        await msg.reply(
            text = "🔍 Первый вариант распознавания:\n" \
                   f"```XOR-AI\n{text}```",
            reply_markup = get_improve_buttons(),
            parse_mode = enums.ParseMode.MARKDOWN
        )
        

@imageRouter.callback_query(F.data == "improve_text")
async def improve_text(callback: CallbackQuery) -> None:
    """Обработчик улучшения текста"""

    user_id = callback.from_user.id
    data = user_data.get(user_id)
    ai_model = settings_manager.get_user_settings(user_id)["ai_model"]
    improve_level = settings_manager.get_user_settings(user_id)["improve_level"]

    if improve_level == 0: 
        improve_level = 1
    
    if not data:
        await callback.answer("Извините, время обработки истекло. Отправьте фото ещё раз.")
        return
    
    await callback.message.edit_reply_markup()
    await bot.send_message(
        chat_id = user_id,
        text = f"Улучшаю текст с текущими настройками " \
               f"({ai_model}, " \
               f"{improve_level} подход{'' if improve_level == 1 else 'а'})...",
        parse_mode = enums.ParseMode.MARKDOWN
    )
    await set_reaction(callback.message, REACTIONS["improving"])

    try:
        text = callback.message.text
        if not is_valid_text(text):
            raise ValueError("Не удалось получить текст")

        for _ in range(improve_level):
            if ai_model == "qwen":
                text = await qwenOCR.process_image(data["photo_bytes"], text)
            else:
                text = await textImprover.improve_text(text)

        if not is_valid_text(text):
            raise ValueError("Не удалось улучшить текст")

        await data["msg"].reply(
            text = f"🔍 Результат обработки:\n" \
                   f"```XOR-AI\n{text}```\n" \
                   f"Используйте /settings для изменения параметров обработки",
            reply_markup=get_improve_buttons(),
            parse_mode=enums.ParseMode.MARKDOWN
        )
    except Exception as e:
        logging.error(f"Ошибка при улучшении текста: {e}")
        await send_error_message(callback.message)

@imageRouter.callback_query(F.data == "save")
async def save_text(callback: CallbackQuery) -> None:
    """Обработчик сохранения текста"""
    
    user_id = callback.from_user.id
    format_type = settings_manager.get_user_settings(user_id)["output_type"]
    
    text = get_text_from_message(callback.message)
    
    try:
        success = await convert_and_send_text(bot, user_id, text, format_type)
        if success:
            await callback.answer("Файл успешно сохранен и отправлен!")
        else:
            raise Exception("Failed to convert and send text")
            
    except Exception as e:
        logging.error(f"Error saving document: {e}")
        await callback.message.reply(
            "❌ Произошла ошибка при сохранении документа. Попробуйте еще раз."
        )

@imageRouter.callback_query(F.data == "summarize_text")
async def summarize_text(callback: CallbackQuery) -> None:
    """Обработчик краткого пересказа текста"""
    
    text = get_text_from_message(callback.message)

    text = await textImprover.summarize_text(text)

    await callback.message.reply(
        text = f"🔍 Результат краткого пересказа:\n" \
               f"```XOR-AI\n{text}```",
        parse_mode = enums.ParseMode.MARKDOWN,
        reply_markup = get_improve_buttons()
    )

@imageRouter.callback_query(F.data == "translate_text")
async def translate_text(callback: CallbackQuery) -> None:
    """Обработчик перевода текста"""
    text = get_text_from_message(callback.message)
    translate_language = settings_manager.get_user_settings(callback.from_user.id)["translate_language"]

    translated_text = await textImprover.translate_text(text, translate_language)

    await callback.message.reply(
        text = f"🔍 Результат перевода:\n" \
               f"```XOR-AI\n{translated_text}```",
        parse_mode = enums.ParseMode.MARKDOWN,
        reply_markup = get_improve_buttons()
    )
