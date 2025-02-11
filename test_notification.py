import os
import requests
from io import BytesIO
import asyncio
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

# Load environment variables
load_dotenv()

# Telegram bot credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

async def send_to_telegram_with_image(title, image_url, price, url, site):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    message = f"<b>{title}</b>\n\n👉🏼 {price} da <b>{site}</b>\n\n"

    # Buttons
    buttons = [[InlineKeyboardButton("🛒 Apri Gamestop 🛒", url=url)]]
    share_url = f"https://t.me/share/url?url={url}&text={title}"
    buttons.append([InlineKeyboardButton("📤 Condividi 📤", url=share_url)])
    reply_markup = InlineKeyboardMarkup(buttons)

    try:
        # Fetch the image
        response = requests.get(image_url)
        image = BytesIO(response.content)

        # Send message (await required)
        await bot.send_photo(
            chat_id=TELEGRAM_CHANNEL_ID,
            photo=image,
            caption=message,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )
        print(f"[✅ SUCCESS] Message sent: {title}")

    except TelegramError as e:
        print(f"[❌ ERROR] Telegram API Error: {e}")
    except Exception as e:
        print(f"[❌ ERROR] Unexpected error: {e}")

# Run the async function
asyncio.run(send_to_telegram_with_image(
    "Collezione Speciale Charizard-ex",
    "https://static-it.gamestop.it/images/products/325488/3max.jpg",
    "34,99€",
    "https://www.gamestop.it/Cards/Games/147831",
    "Gamestop"
))
