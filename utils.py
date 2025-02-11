from urllib.parse import urlparse, parse_qs, urlencode
from dotenv import load_dotenv
load_dotenv()

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