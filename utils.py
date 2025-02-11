from urllib.parse import urlparse, parse_qs, urlencode
from dotenv import load_dotenv
load_dotenv()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/113.0.1774.57",
]

def clean_amazon_url(url):
    """Keep only the Amazon product page and the affiliate tag while removing unnecessary parameters."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Preserve only the affiliate tag
    filtered_params = {k: v for k, v in query_params.items() if k == "tag"}
    clean_query = urlencode(filtered_params, doseq=True)

    # Reconstruct the cleaned URL
    clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    if clean_query:
        clean_url += f"?{clean_query}"

    return clean_url

KEYWORDS = ["pokemon", "Evoluzioni Prismatiche", "scarlatto", "prismatiche", "Pok%C3%A9mon","Avventure Insieme",
            "Battle Partners","Team Rocket","Heat Wave Arena", "Rivali"]
EXCLUDED_KEYWORDS = ["random","assortita", "assortite","Heartforcards","Pokemon-Company-International","Commercio", 
                     "Sammelkartenspiel",  "Glurak"]
EXCLUDED_URLS = ["https://www.amazon.it/gp/gc"]

def clean_price(price):
    """ Convert price from string to float, handling different formats. """
    try:
        if not price or price.strip() == "":
            print(f"[DEBUG] Price is empty or unavailable: '{price}'")
            return None

        # Remove euro symbol, convert comma to dot
        price = price.replace('€', '').replace(',', '.').strip()

        # Convert to float
        return float(price)
    except ValueError as e:
        print(f"[DEBUG] Price cleaning failed for '{price}'. Error: {e}")
        return None