from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from urllib.parse import urlparse, quote
import asyncio
from datetime import datetime
from PIL import Image, ImageOps
import requests
from io import BytesIO
from dotenv import load_dotenv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import traceback
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

def is_valid_url(url):
    """Check if the URL is valid and properly formatted."""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme) and bool(parsed.netloc)
    except Exception as e:
        print(f"[DEBUG] Invalid URL: {url}, Error: {e}")
        return False

def clean_url(url):
    """Clean and encode the URL for safe use."""
    try:
        return quote(url, safe=":/?&=")
    except Exception as e:
        print(f"[ERROR] Failed to clean URL: {e}")
        return url

def should_send(current_details, previous_details, price_change_threshold=0.05):
    """Determine whether a notification should be sent based on price or availability changes."""
    print(f"[DEBUG] should_send called with:\n - current_details: {current_details}\n - previous_details: {previous_details}")

    if not previous_details:
        print("[DEBUG] No previous details found. This is a new product.")
        return True, "New product detected."

    print("[DEBUG] No notification triggered. Check logic for issues.")
    return False, "No significant changes detected."

def process_image(image_url):
    """Download and process the image to fit within a square."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))

        # Create a white square background
        size = max(image.size)
        background = Image.new('RGB', (size, size), (255, 255, 255))

        # Center the image on the background
        offset = ((size - image.size) // 2, (size - image.size) // 2)
        background.paste(image, offset)

        # Save the processed image to a BytesIO object
        output = BytesIO()
        background.save(output, format='JPEG')
        output.seek(0)

        return output

    except Exception as e:
        print(f"[ERROR] Failed to process image: {e}")
        return None

async def send_to_telegram_with_image(title, image_url, price, url, site):
    print(f"[DEBUG] Entering send_to_telegram_with_image with title: {title}, image_url: {image_url}, price: {price}, url: {url}, site: {site}")
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    # Validate and clean the main product URL
    url = clean_url(url)
    if not is_valid_url(url):
        print(f"[ERROR] Invalid product URL: {url}. Skipping notification.")
        return

    # Construct the message text
    message = f"<b>{title}</b>\n\n👉🏼 {price}€ da <b>{site}</b>\n\n"

    # Create buttons
    buttons = [[InlineKeyboardButton("🛒 Apri Amazon 🛒", url=url)]]

    # Validate and clean the share URL
    share_url = clean_url(f"https://t.me/share/url?url={url}&text={title}")
    if is_valid_url(share_url):
        buttons.append([InlineKeyboardButton("📤 Condividi 📤", url=share_url)])
    else:
        print(f"[ERROR] Invalid share URL skipped: {share_url}")

    reply_markup = InlineKeyboardMarkup(buttons)

    try:
        if image_url and is_valid_url(image_url):
            print(f"[DEBUG] Attempting to send image message to {TELEGRAM_CHANNEL_ID}")
            processed_image = process_image(image_url)
            if processed_image:
                print(f"[DEBUG] Processed image successfully")
                response = await bot.send_photo(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    photo=processed_image,
                    caption=message,
                    parse_mode="HTML",
                    reply_markup=reply_markup,
                )
                print(f"[DEBUG] Sent: {title}")
            else:
                print(f"[DEBUG] Failed to process image")
                response = await bot.send_message(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    text=message,
                    parse_mode="HTML",
                    reply_markup=reply_markup,
                )
                print(f"[DEBUG] Sent: {title}")
        else:
            print(f"[DEBUG] No image URL provided or invalid image URL")
            response = await bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=message,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
            print(f"[DEBUG] Sent: {title}")

    except TelegramError as e:
        print(f"[ERROR] Telegram API Error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error while sending Telegram message: {e}")

def send_email(subject, body):
    """Sends an email notification."""
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USERNAME
        msg["To"] = TO_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, TO_EMAIL, msg.as_string())
        server.quit()

        print(f"[INFO] Email sent: {subject}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

def send_heartbeat():
    """Sends a periodic heartbeat email to confirm the script is running."""
    subject = "✅ Price Tracker Status: Running"
    body = "The price tracking script is running normally."
    send_email(subject, body)

def send_error_alert(error):
    """Sends an error alert email when an exception occurs."""
    subject = "❌ Price Tracker Alert: Error Detected"
    body = f"An error occurred in the script:\n\n{traceback.format_exc()}"
    send_email(subject, body)