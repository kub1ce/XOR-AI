from aiogram.types import Message

from app.settings import bot
from app.handlers.GoogleOCR import drive_ocr
from app.handlers.text_improver import textImprover


async def message(msg: Message):
    if msg.text == "/start":
        await bot.send_message(msg.from_user.id, "Crocodillo Bombordiro")
    elif msg.photo:
        photo = msg.photo[-1]
        file_id = photo.file_id
        file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(file.file_path)

        todel = await msg.reply("Принято в работу!")

        # Конвертация в b64
        # image = Image.open(BytesIO(downloaded_file.getvalue()))
        # buffered = BytesIO()
        # image.save(buffered, format="JPEG")
        # img_str = base64.b64encode(buffered.getvalue()).decode()
        
        text = await drive_ocr.process_image(file_bytes)

        text = textImprover.improve_text(text)
        
        await msg.reply(text)
        await todel.delete()
        
