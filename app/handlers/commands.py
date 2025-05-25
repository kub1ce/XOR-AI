from aiogram import Router, filters, enums, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from app.settings_manager import settings_manager

commandsRouter = Router(name="Commands")

def get_menu_buttons() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками навигации в меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "выбор нейросети", callback_data="ai")],
        [InlineKeyboardButton(text = "выбор формата", callback_data="type")],
        [InlineKeyboardButton(text = "доп. обработка", callback_data="improve")],
        [InlineKeyboardButton(text = "язык перевода", callback_data="translate")],
        # [InlineKeyboardButton(text = "LaTex", callback_data="latex")],
    ])

def get_ai_buttons() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками навигации в меню, выбор нейросети"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "Qwen (по умолчанию)", callback_data="ai_qwen")],
        [InlineKeyboardButton(text = "DeepSeek", callback_data="ai_deepseek")],
    ])

def get_type_buttons() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками навигации в меню, выбор формата"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "pdf (по умолчанию)", callback_data="tp_pdf")],
        [InlineKeyboardButton(text = "txt", callback_data="tp_txt")],
        [InlineKeyboardButton(text = "docx", callback_data="tp_docx")],
    ])

def get_improve_buttons() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками навигации в меню, доп. обработка"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "1 (по умолчанию)", callback_data="im_1")],
        [InlineKeyboardButton(text = "2", callback_data="im_2")],
    ])

def get_latex_buttons() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками навигации в меню, LaTex"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "выключить (по умолчанию)", callback_data="lt_no")],
        [InlineKeyboardButton(text = "включить", callback_data="lt_yes")],
    ])

def get_translate_buttons() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками навигации в меню, язык перевода"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "русский (по умолчанию)", callback_data="tr_ru")],
        [InlineKeyboardButton(text = "english", callback_data="tr_en")],
    ])

@commandsRouter.message(filters.CommandStart())
async def greeting(msg: Message):
    await msg.answer(
        text = "👋 XOR AI - отправьте фото/файл, и я преобразую его в текст!\n" \
                "🔍 Для лучшего результата присылайте чёткие фото или файлы.\n" \
                "🚀 Команды:\n" \
                " • /help - если нужны подсказки\n" \
                " • /settings - выбор формата и нейросети",
        parse_mode = enums.ParseMode.MARKDOWN
    )

@commandsRouter.message(filters.Command("help"))
async def help(msg: Message):
    await msg.answer(
        text = "Отправьте фото/файл → получите текст.\n\n" \
               "Советы для лучшего результата:  \n" \
               " • Снимайте фото при хорошем освещении, без наклона.\n" \
               " • Большие документы отправляйте файлом.\n" \
               " • Если текст распознался плохо, попробуйте переснять или выбрать доп. обработку.\n\n" \
               "⚙️ Команды бота:\n" \
               "/start - возобновление бота.\n" \
               "/settings - выбор нейросети, формата ответа и др.\n\n" \
               "Проблемы? Пишите @kubice",
        parse_mode = enums.ParseMode.MARKDOWN
    )

@commandsRouter.message(filters.Command("settings"))
async def settings(msg: Message):
    await msg.answer(
        text = "⚙️ Настройки XOR AI\n" \
               "Здесь вы можете настроить, как бот будет обрабатывать ваши файлы",
        reply_markup = get_menu_buttons()
    )


# ========== Settings callbacks ==========

@commandsRouter.callback_query(F.data == "ai")
async def switch_ai(callvack: CallbackQuery):
    """Изменение нейросети"""
    await callvack.message.edit_text(
        text = "Выберите нейросеть для доп. обработки:",
        reply_markup = get_ai_buttons()
    )

@commandsRouter.callback_query(F.data == "type")
async def switch_type(callvack: CallbackQuery):
    """Изменение формата"""
    await callvack.message.edit_text(
        text = "Выберите формат для сохранения обработанного текста:",
        reply_markup = get_type_buttons()
    )

@commandsRouter.callback_query(F.data == "improve")
async def switch_improve(callvack: CallbackQuery):
    """Изменение доп. обработки"""
    await callvack.message.edit_text(
        text = "Выберите количество повторов доп. обработки:\n\n" \
               "Текст после экстракции будет передан в LLM-модель для структурирования, исправления опечаток и правильного расположения слов",
        reply_markup = get_improve_buttons()
    )

@commandsRouter.callback_query(F.data == "latex")
async def switch_latex(callvack: CallbackQuery):
    """Изменение LaTex"""
    await callvack.answer(
        "Недоступно в вашем регионе",
        show_alert = True
    )

    # await callvack.message.edit_text(
    #     text = "Включите обработку LaTex, если требуется (обработка формул):",
    #     reply_markup = get_latex_buttons()
    # )


@commandsRouter.callback_query(F.data == "translate")
async def switch_translate(callvack: CallbackQuery):
    """Изменение языка перевода"""
    await callvack.message.edit_text(
        text = "Выберите язык для перевода:",
        reply_markup = get_translate_buttons()
    )

@commandsRouter.callback_query(F.data.startswith("ai_"))
@commandsRouter.callback_query(F.data.startswith("tp_"))
@commandsRouter.callback_query(F.data.startswith("im_"))
@commandsRouter.callback_query(F.data.startswith("lt_"))
@commandsRouter.callback_query(F.data.startswith("tr_"))
async def switch_settings(callvack: CallbackQuery):
    # Сохраняем настройки пользователя
    _type = callvack.data.split("_")[0]
    _value = callvack.data.split("_")[1]

    # Update settings
    success = settings_manager.update_user_settings(callvack.from_user.id, _type, _value)
    
    if not success:
        await callvack.answer(
            "Произошла ошибка при сохранении настроек",
            show_alert = True
        )
        return
    
    # Ответ
    """Изменение настроек"""
    await callvack.answer(
        "Настройки успешно изменены!",
        # show_alert = True
    )
    await callvack.message.edit_text(
        text = "Вы успешно изменили настройки!\n\n" \
               "Хотите ещё что-то изменить?",
        reply_markup = get_menu_buttons()
    )