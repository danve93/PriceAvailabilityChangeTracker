import time
import random
import requests
import re
import json
import os
import ssl
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Disable SSL warnings (temporary fix)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Force TLS 1.2+ for Amazon SSL issues
session = requests.Session()
adapter = requests.adapters.HTTPAdapter()
context = ssl.create_default_context()
context.set_ciphers('DEFAULT@SECLEVEL=1')  # Adjust security level if needed
context.check_hostname = False  # ✅ Disable check_hostname when verify=False
context.verify_mode = ssl.CERT_NONE  # ✅ Ensure no certificate verification
adapter.init_poolmanager(connections=10, maxsize=10, block=True, ssl_context=context)
session.mount("https://", adapter)

# Referral tag from environment variables
REFERRAL_TAG = os.getenv("REFERRAL_TAG")
if REFERRAL_TAG is None:
    raise ValueError("REFERRAL_TAG environment variable is not set. Please check your .env file.")

AMAZON_CATEGORY_URL = os.getenv("AMAZON_CATEGORY_URL")
AMAZON_NEWEST_URL = os.getenv("AMAZON_NEWEST_URL")
AMAZON_POKEMON_URL = os.getenv("AMAZON_POKEMON_URL")
USER_AGENTS = os.getenv("USER_AGENTS")
keywords =  os.getenv("KEYWORDS")
excluded_keywords =  os.getenv("EXCLUDED_KEYWORDS")
excluded_urls = os.getenv("EXCLUDED_URLS")

# Path to product URLs file
PRODUCT_URLS_FILE = "product_urls.py"

def clean_amazon_url(url):
    """Extract and clean the Amazon product URL, keeping only the base /dp/ link."""
    parsed_url = urlparse(url)
    match = re.search(r'(/dp/[^/?]+)', parsed_url.path)
    if match:
        return f"https://www.amazon.it{match.group(1)}"
    return None  # Return None if the URL is not a valid product page

def add_referral(url):
    """Ensure only the referral tag is appended to a clean Amazon product URL."""
    if url is None:
        return None
    return f"{url}?tag={REFERRAL_TAG.replace('?tag=', '')}"

def fetch_amazon_product_links(category_url, retries=5):
    """Fetch and extract unique product links from an Amazon category page."""
    for attempt in range(retries):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }

            response = session.get(category_url, headers=headers, timeout=15, verify=False)  # ✅ SSL verify disabled
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            seen_links = set()
            product_links = []

            for link in soup.find_all("a", href=True):
                url = link["href"]
                if "/dp/" in url:
                    full_url = urljoin("https://www.amazon.it", url.split("?")[0])  # Remove tracking params
                    cleaned_url = clean_amazon_url(full_url)

                    if cleaned_url and cleaned_url not in seen_links:
                        seen_links.add(cleaned_url)
                        product_links.append(cleaned_url)

            print(f"[DEBUG] Extracted {len(product_links)} unique product links from {category_url}")
            return product_links

        except requests.exceptions.SSLError:
            print(f"[ERROR] SSL Error encountered for {category_url}. Retrying in 5 seconds...")
            time.sleep(5)
            continue  # Retry

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error fetching {category_url}: {e}")
            return []

    return []  # Return empty list if all retries fail

def load_existing_urls():
    """Load existing URLs from product_urls.py and ensure it's a list."""
    if not os.path.exists(PRODUCT_URLS_FILE):
        return []

    try:
        with open(PRODUCT_URLS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                content = content.replace("product_urls =", "").strip()
                existing_urls = eval(content)
                return existing_urls if isinstance(existing_urls, list) else []
    except (SyntaxError, ValueError, Exception) as e:
        print(f"[ERROR] Failed to read existing URLs: {e}")

    return []

def update_urls():
    """Fetch new product links and merge them with existing URLs while ensuring uniqueness."""
    existing_urls = set(load_existing_urls())

    # Fetch links from all sources
    new_urls = set()
    new_urls.update(fetch_amazon_product_links(AMAZON_CATEGORY_URL))
    new_urls.update(fetch_amazon_product_links(AMAZON_NEWEST_URL))
    new_urls.update(fetch_amazon_product_links(AMAZON_POKEMON_URL))

    print(f"[DEBUG] Combined unique new URLs: {len(new_urls)}")

    # Ensure URLs contain at least one keyword and exclude any unwanted ones
    filtered_new_urls = {
        url for url in new_urls
        if any(keyword.lower() in url.lower() for keyword in keywords)
        and not any(excluded_keyword.lower() in url.lower() for excluded_keyword in excluded_keywords)
        and url not in excluded_urls
    }

    print(f"[DEBUG] Filtered URLs after applying keyword and exclusion checks: {len(filtered_new_urls)}")

    # Clean and apply referral tag to URLs
    cleaned_urls = {clean_amazon_url(url) for url in filtered_new_urls}
    cleaned_urls = {url for url in cleaned_urls if url is not None}  # Remove None values
    new_urls_with_referral = {add_referral(url) for url in cleaned_urls}

    # Ensure only truly new URLs are added
    urls_to_add = new_urls_with_referral - existing_urls

    if urls_to_add:
        updated_urls = list(existing_urls.union(urls_to_add))

        # Log the new URLs being added
        print(f"[INFO] New URLs being added: {urls_to_add}")

        with open(PRODUCT_URLS_FILE, "w", encoding="utf-8") as f:
            f.write(f"product_urls = {json.dumps(updated_urls, indent=4)}")
        
        print(f"[INFO] Added {len(urls_to_add)} new URLs. Total URLs: {len(updated_urls)}")
    else:
        print(f"[INFO] No new Amazon URLs found. Keeping existing list.")

if __name__ == "__main__":
    import sys

    if "--once" in sys.argv:
        print("[INFO] Running am.py once for URL updates...")
        update_urls()
    else:
        print("[INFO] Running am.py once for URL updates...")
        update_urls()
