import asyncio
import random
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
load_dotenv()

USER_AGENTS = os.getenv("USER_AGENTS")

def start_selenium():
    """Initialize and return a headless Selenium WebDriver."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

    driver = webdriver.Chrome(service=Service(), options=options)
    return driver

async def extract_price(driver):
    """Extract price from the product page."""
    try:
        price_span = driver.find_element(By.XPATH, '//span[contains(@class, "prodPriceCont")]')
        raw_price = price_span.text.strip()
        price = re.sub(r"[^\d,]", "", raw_price).replace(",", ".")  # Convert "18,98€" -> "18.98"
        print(f"[DEBUG] Extracted price: {price}")
        return price
    except Exception as e:
        print(f"[DEBUG] Price extraction failed: {e}")
        return "Price not found"

async def extract_availability(driver):
    """Determines whether the product is available or not."""
    try:
        availability_section = driver.find_element(By.CLASS_NAME, "productAvailability")

        def check_availability(alt_text):
            try:
                img = availability_section.find_element(By.XPATH, f'.//img[@alt="{alt_text}"]')
                return "deliveryAvailable.png" in img.get_attribute("src")
            except:
                return False

        home_delivery = check_availability("Is Delivery Available")
        store_pickup = check_availability("Is Collect Available")
        reservation = check_availability("Is Reservation Available")

        if home_delivery or store_pickup:
            print("[DEBUG] Product is Available")
            return "Available"
        elif reservation:
            print("[DEBUG] Product is a Preorder")
            return "Preorder"
        else:
            print("[DEBUG] Product is Not Available")
            return "Not Available"
    except Exception as e:
        print(f"[DEBUG] Availability check failed: {e}")
        return "Not Available"

async def extract_image(driver):
    """Extracts the highest resolution image available."""
    try:
        image_element = driver.find_element(By.CSS_SELECTOR, 'a.prodImg.max')
        image_url = image_element.get_attribute("href")
        print(f"[DEBUG] Extracted high-res image: {image_url}")
        return image_url
    except:
        print("[DEBUG] High-res image not found, falling back to low-res image.")
        try:
            image_element = driver.find_element(By.CSS_SELECTOR, 'img#packshotImage')
            return image_element.get_attribute("src")
        except:
            return "Image not found"

async def get_gamestop_product_data(driver, url):
    """Extract product details from GameStop with retry logic."""
    print(f"\nOpening URL: {url}")

    for attempt in range(3):  # Retry up to 3 times
        try:
            driver.get(url)
            await asyncio.sleep(random.uniform(3, 6))  # Wait for JavaScript to load

            title = driver.find_element(By.CSS_SELECTOR, 'meta[property="og:title"]').get_attribute("content")
            price = await extract_price(driver)  # ✅ Await the coroutine
            image_url = await extract_image(driver)  # ✅ Await the coroutine
            availability = await extract_availability(driver)  # ✅ Await the coroutine

            product_data = {
                "title": title,
                "price": price,
                "image_url": image_url,
                "availability": availability,
            }
            print(f"\nExtracted Product Data: {product_data}")
            return product_data

        except Exception as e:
            print(f"[ERROR] Failed to fetch {url}, attempt {attempt + 1}/3: {e}")
            await asyncio.sleep(attempt * 5)  # Exponential backoff
            
    return None

if __name__ == "__main__":
    from gamestop_urls import gamestop_urls  # Import URLs from external file

    driver = start_selenium()
    seen_urls = set()  # ✅ Avoid duplicate processing

    try:
        for url in gamestop_urls:
            if url not in seen_urls:
                seen_urls.add(url)  # ✅ Track seen URLs
                asyncio.run(get_gamestop_product_data(driver, url))
    finally:
        driver.quit()
