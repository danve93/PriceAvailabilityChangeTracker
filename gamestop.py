import asyncio
import json
import os
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from utils import USER_AGENTS

load_dotenv()

PRODUCT_URLS_FILE = "gamestop_urls.py"

def start_selenium():
    """Initialize and return a headless Selenium WebDriver."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--enable-unsafe-swiftshader")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

    driver = webdriver.Chrome(service=Service(), options=options)
    return driver

async def get_gamestop_product_data(driver, url):
    """Extract product details from GameStop."""
    try:
        driver.get(url)
        await asyncio.sleep(random.uniform(3, 6))  # Allow time for JavaScript to load

        title_element = driver.find_element(By.CSS_SELECTOR, 'meta[property="og:title"]')
        title = title_element.get_attribute("content") if title_element else "Unknown Product"

        price_element = driver.find_element(By.CLASS_NAME, "prodPriceCont")
        price = price_element.text.strip() if price_element else "Price not found"

        availability_element = driver.find_element(By.CLASS_NAME, "productAvailability")
        availability = availability_element.text.strip() if availability_element else "Unknown Availability"

        image_element = driver.find_element(By.CSS_SELECTOR, 'img#packshotImage')
        image_url = image_element.get_attribute("src") if image_element else "Image not found"

        product_data = {
            "title": title,
            "price": price,
            "availability": availability,
            "image_url": image_url,
        }

        print(f"[INFO] Scraped product: {title}")
        return product_data
    except Exception as e:
        print(f"[ERROR] Failed to scrape {url}: {e}")
        return None

async def scrape_all_products():
    """Scrape all GameStop products from the stored URLs."""
    if not os.path.exists(PRODUCT_URLS_FILE):
        print(f"[ERROR] {PRODUCT_URLS_FILE} not found!")
        return

    with open(PRODUCT_URLS_FILE, "r", encoding="utf-8") as f:
        urls = json.load(f)

    driver = start_selenium()
    results = []

    for url in urls:
        product_data = await get_gamestop_product_data(driver, url)
        if product_data:
            results.append(product_data)

    driver.quit()
    return results

if __name__ == "__main__":
    asyncio.run(scrape_all_products())
