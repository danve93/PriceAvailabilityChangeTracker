from amazon import get_amazon_product_details
from gamestop import get_gamestop_product_data


SCRAPER_MAP = {
    "amazon.it": get_amazon_product_details,
    "gamestop.it": get_gamestop_product_data,
}

async def get_product_details(url):
    """Determine which scraper to use based on the URL."""
    for domain, scraper in SCRAPER_MAP.items():
        if domain in url:
            return await scraper(url)
    
    return None  # If no scraper is found for the domain
