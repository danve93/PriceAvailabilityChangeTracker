import requests
from bs4 import BeautifulSoup
import random
import sys
import os
import time
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import clean_amazon_url
from product_urls import product_urls
from dotenv import load_dotenv
load_dotenv()

USER_AGENTS = os.getenv("USER_AGENTS")

def fetch(url, retries=5):
    """Fetch page content with retries and delay to avoid CAPTCHAs."""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "it-IT,it;q=0.9"
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Check for CAPTCHA or empty response
            if "captcha" in response.text.lower() or "Type the characters you see below" in response.text:
                print(f"[🚨] CAPTCHA detected. Retrying {attempt+1}/{retries}...")
                time.sleep(random.uniform(5, 10))  # Longer delay
                continue

            if response.text.strip() == "":
                print(f"[🚨] Empty response for {url}. Retrying {attempt+1}/{retries}...")
                time.sleep(random.uniform(5, 10))  # Increase delay
                continue

            return response.text

        except requests.RequestException as e:
            print(f"[🚨] Request failed for {url}: {e}")
            time.sleep(random.uniform(3, 7))  # Delay before retry

    print(f"[ERROR] Failed to fetch {url} after {retries} retries.")
    return None

async def get_amazon_product_details(url):
    """Extract Amazon product details if fulfilled & shipped by Amazon."""
    await asyncio.sleep(random.uniform(2, 6))  # Random delay to avoid detection

    clean_url = clean_amazon_url(url)
    print(f"[DEBUG] Fetching details for URL: {clean_url}")
    html = fetch(clean_url)
    if not html:
        print(f"[WARNING] Skipping {clean_url} due to missing page content.")
        return None

    soup = BeautifulSoup(html, "html.parser")

    # Extract merchant and fulfillment info
    merchant_element = soup.select_one('[offer-display-feature-name="desktop-merchant-info"] .offer-display-feature-text-message')
    fulfillment_element = soup.select_one('[offer-display-feature-name="desktop-fulfiller-info"] .offer-display-feature-text-message')

    # Alternative selectors
    if not merchant_element:
        merchant_element = soup.select_one("#merchant-info")
    if not fulfillment_element:
        fulfillment_element = soup.select_one("#shipsFromSoldBy_feature_div")

    merchant_text = merchant_element.get_text(strip=True) if merchant_element else "Unknown Merchant"
    fulfillment_text = fulfillment_element.get_text(strip=True) if fulfillment_element else "Unknown Fulfillment"

    print(f"[DEBUG] Merchant: '{merchant_text}', Fulfillment: '{fulfillment_text}'")

    is_fulfilled_by_amazon = "amazon" in merchant_text.lower() and "amazon" in fulfillment_text.lower()

    if not is_fulfilled_by_amazon:
        print(f"[INFO] Skipping {clean_url} (Not fulfilled & shipped by Amazon)")
        return None

    # Extract product details
    title_element = soup.select_one("#productTitle")
    title_text = title_element.get_text(strip=True) if title_element else "Titolo non trovato"

    price_element = soup.select_one(".a-price .a-offscreen")
    image_element = soup.select_one("#landingImage")

    product_data = {
        "title": title_text,
        "price": price_element.get_text(strip=True) if price_element else "Prezzo non disponibile",
        "availability": True,
        "image_url": image_element["src"] if image_element else "Immagine non trovata"
    }

    print(f"[SUCCESS] Scraped: {product_data['title']}")

    # Free memory
    del soup
    return product_data