import time
import random
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from utils import USER_AGENTS

load_dotenv()

GAMESTOP_PREORDER_URL = "https://www.gamestop.it/preorder#74bf/fullscreen/f[availability][]=preorder&f[categories][]=cardGames&m=and&q=pok%C3%A9mon"
PRODUCT_URLS_FILE = "gamestop_urls.py"

def start_selenium():
    """Initialize and return a headless Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

    driver = webdriver.Chrome(service=Service(), options=options)
    return driver

def fetch_gamestop_product_links(category_url):
    """Fetch and extract unique product links from a GameStop category page."""
    try:
        driver = start_selenium()
        driver.get(category_url)

        # Wait for the page to load
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.dfd-card-link"))
            )
        except Exception as e:
            print(f"[ERROR] Timeout waiting for elements: {e}")
            driver.quit()
            return []

        time.sleep(5)  # Allow time for lazy-loaded elements

        seen_links = set()
        product_links = []

        links = driver.find_elements(By.CSS_SELECTOR, "a.dfd-card-link")
        if not links:
            print(f"[ERROR] No product links found on {category_url}")
            driver.quit()
            return []

        print(f"[DEBUG] Found {len(links)} links on the page.")

        for link in links:
            url = link.get_attribute("href")
            if url and "/product/" in url:
                if url not in seen_links:
                    seen_links.add(url)
                    product_links.append(url)

        driver.quit()
        print(f"[INFO] Extracted {len(product_links)} unique product links from {category_url}")
        return product_links
    except Exception as e:
        print(f"[ERROR] Error fetching {category_url} using Selenium: {e}")
        return []

def update_urls():
    """Fetch new product links and merge them with existing URLs while ensuring uniqueness."""
    if not os.path.exists(PRODUCT_URLS_FILE):
        existing_urls = []
    else:
        with open(PRODUCT_URLS_FILE, "r", encoding="utf-8") as f:
            try:
                existing_urls = json.load(f)
            except json.JSONDecodeError:
                existing_urls = []

    new_urls = fetch_gamestop_product_links(GAMESTOP_PREORDER_URL)
    urls_to_add = set(new_urls) - set(existing_urls)

    if urls_to_add:
        updated_urls = list(set(existing_urls).union(set(new_urls)))

        with open(PRODUCT_URLS_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_urls, f, indent=4)

        print(f"[INFO] Added {len(urls_to_add)} new URLs. Total URLs: {len(updated_urls)}")
    else:
        print("[INFO] No new GameStop URLs found.")

if __name__ == "__main__":
    print("[INFO] Running GameStop URL scraper...")
    update_urls()
