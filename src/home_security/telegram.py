from typing import List
from telegram import Bot, InputMediaPhoto
from typing import List
from home_security.settings import settings
from PIL import Image
from io import BytesIO


async def send_photo(images: List[Image.Image], image_caption: str, recipients: List):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    for recipient in recipients:
        img_bytes = []
        for img in images:
            bio = BytesIO()
            img.save(bio, format="JPEG")
            bio.seek(0)
            img_bytes.append(InputMediaPhoto(media=bio))

        await bot.send_media_group(
            chat_id=recipient, media=img_bytes, caption=image_caption
        )
    return True
