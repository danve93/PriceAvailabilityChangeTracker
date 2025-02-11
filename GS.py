import time
import random
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import os
from utils import USER_AGENTS, keywords, excluded_keywords, excluded_urls
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import USER_AGENTS  # ✅ Import USER_AGENTS from utils
load_dotenv()

# Base URLs for scraping
GAMESTOP_PREORDER_URL = os.getenv("GAMESTOP_PREORDER_URL")
PRODUCT_URLS_FILE = "gamestop_urls.py"
USER_AGENTS = os.getenv("USER_AGENTS")

# Future referral system (commented out for now)
# REFERRAL_TAG_GS = os.getenv("REFERRAL_TAG_GS")


def start_selenium():
    """Initialize and return a headless Selenium WebDriver."""
    chromium_service = Service()
    chromium_options = webdriver.ChromeOptions()
    chromium_options.add_argument("--headless")  # Run without a GUI
    chromium_options.add_argument("--log-level=3")  # Suppress unnecessary logs
    chromium_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chromium_options.add_argument("--disable-software-rasterizer")  # Avoid software rendering fallback
    chromium_options.add_argument("--no-sandbox")  # Avoid permission issues
    chromium_options.add_argument("--disable-dev-shm-usage")  # Prevent shared memory issues
    chromium_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    chromium_driver = webdriver.Chrome(service=chromium_service, options=chromium_options)
    return chromium_driver


def clean_gamestop_url(url):
    """Extract and clean the GameStop product URL, keeping only the base /Cards/Games/{ID}/ link."""
    match = re.search(r'(https://www\.gamestop\.it/Cards/Games/\d+)/', url)
    return match.group(1) + "/" if match else None


def fetch_gamestop_product_links(category_url):
    """Fetch and extract unique product links using Selenium from a GameStop category/search page."""
    try:
        driver = start_selenium()
        driver.get(category_url)

        # Ensure elements are loaded by waiting for the targeted links
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.dfd-card-link"))
        )
        
        time.sleep(5)  # Additional wait for lazy-loaded elements
        
        seen_links = set()
        product_links = []

        links = driver.find_elements(By.CSS_SELECTOR, "a.dfd-card-link")
        print(f"[DEBUG] Found {len(links)} links on the page.")

        for link in links:
            url = link.get_attribute("href")
            print(f"[DEBUG] Raw URL found: {url}")
            if url and "/Cards/Games/" in url:
                cleaned_url = clean_gamestop_url(url)
                print(f"[DEBUG] Cleaned URL: {cleaned_url}")
                if cleaned_url and cleaned_url not in seen_links:
                    seen_links.add(cleaned_url)
                    product_links.append(cleaned_url)

        driver.quit()
        print(f"[INFO] Extracted {len(product_links)} unique product links from {category_url}")
        return product_links
    except Exception as e:
        print(f"[ERROR] Error fetching {category_url} using Selenium: {e}")
        return []


def load_existing_urls():
    """Load existing URLs from gamestop_urls.py and ensure it's a list."""
    if not os.path.exists(PRODUCT_URLS_FILE):
        return []
    try:
        with open(PRODUCT_URLS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                content = content.replace("gamestop_urls =", "").strip()
                existing_urls = eval(content)
                return existing_urls if isinstance(existing_urls, list) else []
    except Exception as e:
        print(f"[ERROR] Failed to read existing URLs: {e}")
    return []


def update_urls():
    """Fetch new product links and merge them with existing URLs while ensuring uniqueness."""
    existing_urls = set(load_existing_urls())
    new_urls = set(fetch_gamestop_product_links(GAMESTOP_PREORDER_URL))
    #new_urls.update(fetch_gamestop_product_links(GAMESTOP_GENERAL_URL))

    urls_to_add = new_urls - existing_urls
    updated_urls = list(existing_urls.union(new_urls))

    print(f"[INFO] Adding {len(urls_to_add)} new URLs.")

    with open(PRODUCT_URLS_FILE, "w", encoding="utf-8") as f:
        f.write(f"gamestop_urls = {json.dumps(updated_urls, indent=4)}")

    print(f"[INFO] Updated URL list contains {len(updated_urls)} URLs.")


if __name__ == "__main__":
    print("[INFO] Running GameStop scraper...")
    update_urls()