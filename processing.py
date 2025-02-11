import asyncio
import logging
import random
import re
from database import save_product_details, fetch_previous_details, mark_url_as_invalid
from notifications import send_to_telegram_with_image, should_send, send_error_alert
from scraper_manager import get_product_details
from utils import clean_price
from gamestop import start_selenium, get_gamestop_product_data
from requests.exceptions import ConnectionError

PRICE_CHANGE_THRESHOLD = 0.05  
MAX_RETRIES = 3  

def convert_price_to_float(price):
    """Converts a price string to a float after cleaning it."""
    if isinstance(price, (int, float)):  # Already a number
        return float(price)
    
    if isinstance(price, str):
        # Remove non-numeric characters (like currency symbols)
        cleaned_price = re.sub(r"[^\d,.]", "", price).replace(",", ".")
        try:
            return float(cleaned_price)
        except ValueError:
            logging.warning(f"⚠️ Failed to convert price: {price}")
            return None  # Return None if conversion fails
    return None

async def process_url(url):
    """Process a product URL asynchronously, updating the database and sending notifications if necessary."""
    retry_delay = 5

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.debug(f"Processing URL: {url}")

            # ✅ Detect source (GameStop vs. Amazon)
            if "gamestop.it" in url:
                logging.debug("[INFO] Detected GameStop URL, using Selenium scraper...")
                driver = start_selenium()
                details = await get_gamestop_product_data(driver, url)
                driver.quit()
                await asyncio.sleep(random.uniform(15, 30))
            else:
                details = await get_product_details(url)

            if not details:
                logging.warning(f"❌ No details returned for URL: {url}")
                mark_url_as_invalid(url)
                return

            # ✅ Convert and compare prices
            details["price"] = convert_price_to_float(details["price"])
            previous_details = fetch_previous_details(url)

            # ✅ Check if product is NEW
            if not previous_details:
                print(f"[INFO] 🆕 New product found: {details['title']}")
                save_product_details(url, details["title"], details["price"], details["availability"], details.get("image_url"))

                try:
                    await send_to_telegram_with_image(
                        details["title"], details.get("image_url"), details["price"], url, 
                        "GameStop" if "gamestop.it" in url else "Amazon"
                    )
                    logging.info(f"✅ Notification sent for new product: {details['title']}")
                except Exception as e:
                    logging.error(f"❌ Failed to send notification for new product {details['title']}: {e}")
                return  # Exit after saving

            # ✅ Check if price/availability changed
            prev_price = convert_price_to_float(previous_details["price"])
            price_changed = abs(prev_price - details["price"]) / prev_price >= PRICE_CHANGE_THRESHOLD if prev_price else False
            availability_changed = previous_details["availability"] != details["availability"]

            if price_changed or availability_changed:
                print(f"[INFO] 🔄 Updating product: {details['title']}")
                save_product_details(url, details["title"], details["price"], details["availability"], details.get("image_url"))

                try:
                    await send_to_telegram_with_image(
                        details["title"], details.get("image_url"), details["price"], url, 
                        "GameStop" if "gamestop.it" in url else "Amazon"
                    )
                    logging.info(f"✅ Notification sent for {details['title']}")
                except Exception as e:
                    logging.error(f"❌ Failed to send notification for {details['title']}: {e}")
            else:
                print(f"[DEBUG] No changes detected for {details['title']}")

        except Exception as e:
            logging.error(f"❌ Failed to process URL {url}: {e}")
            mark_url_as_invalid(url)
            send_error_alert(e)
            return
