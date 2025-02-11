import asyncio
import logging
import subprocess
from database import initialize_database, save_product_details, fetch_previous_details
from notifications import send_heartbeat, should_send, send_to_telegram_with_image
from product_urls import product_urls
from gamestop_urls import gamestop_urls
from gamestop import get_gamestop_product_data, start_selenium
from amazon import get_amazon_product_details

# Constants
CHECK_INTERVAL = 60  # Time in seconds before checking for new updates
BATCH_SIZE = 5       # Number of URLs processed in each batch
HEARTBEAT_INTERVAL = 21600  # Send heartbeat every 6 hours
GAMESTOP_UPDATE_INTERVAL = 3600  # Run GameStop scraping once per hour

async def run_am():
    """Run Amazon scraper (AM.py) asynchronously."""
    logging.info("[INFO] Running AM.py asynchronously...")
    process = await asyncio.create_subprocess_exec("python", "AM.py")
    await process.communicate()

async def run_gs():
    """Run GameStop scraper (GS.py) asynchronously once per hour."""
    while True:
        logging.info("[INFO] Running GS.py asynchronously...")
        process = await asyncio.create_subprocess_exec("python", "GS.py")
        await process.communicate()
        await asyncio.sleep(GAMESTOP_UPDATE_INTERVAL)  # Runs every hour

async def process_gamestop():
    """Processes GameStop URLs once per hour to avoid redundant scraping."""
    while True:
        logging.info("[INFO] Running GameStop scraper...")

        driver = start_selenium()
        seen_urls = set()

        try:
            results = []
            for url in gamestop_urls:
                if url not in seen_urls:
                    seen_urls.add(url)
                    product_data = await get_gamestop_product_data(driver, url)
                    if product_data:
                        results.append(product_data)

            # Print only unique extracted product data
            for product in results:
                print(product)

        finally:
            driver.quit()

        logging.info("[INFO] GameStop scraping complete. Sleeping for 1 hour.")
        await asyncio.sleep(GAMESTOP_UPDATE_INTERVAL)

async def track_products():
    """Main tracking function that processes Amazon and GameStop URLs."""
    last_heartbeat = asyncio.get_running_loop().time()

    while True:
        start_time = asyncio.get_running_loop().time()
        logging.debug("Fetching valid URLs...")

        all_urls = gamestop_urls + product_urls
        logging.debug(f"Total URLs to check: {len(all_urls)}")

        try:
            for batch_start in range(0, len(all_urls), BATCH_SIZE):
                batch = all_urls[batch_start:batch_start + BATCH_SIZE]
                logging.info(f"Processing batch {batch_start // BATCH_SIZE + 1}/{(len(all_urls) + BATCH_SIZE - 1) // BATCH_SIZE}")

                # Process all URLs (Amazon and GameStop)
                for url in batch:
                    try:
                        # Detect source and call appropriate scraper
                        if "gamestop.it" in url:
                            driver = start_selenium()
                            product_data = await get_gamestop_product_data(driver, url)
                            driver.quit()
                        else:
                            product_data = await get_amazon_product_details(url)

                        if product_data:
                            # Save the data in the database
                            save_product_details(url, product_data['title'], product_data['price'],
                                                product_data['availability'], product_data['image_url'])

                            # Retrieve the previous details
                            previous_details = fetch_previous_details(url)

                            # Verify saved data
                            print(f"[DEBUG] Saved product_data: {product_data}")
                            retrieved_data = fetch_previous_details(url)
                            print(f"[DEBUG] Retrieved data from database: {retrieved_data}")

                            # Evaluate whether to send a notification
                            should_notify, reason = should_send(product_data, previous_details)
                            if should_notify:
                                # Determine the source
                                source = "GameStop" if "gamestop.it" in url else "Amazon"

                                # Send notification
                                await send_to_telegram_with_image(product_data['title'], product_data['image_url'],
                                                                product_data['price'], url, source)
                    except Exception as e:
                        print(f"[ERROR] Error processing URL {url}: {e}")

            elapsed = asyncio.get_running_loop().time() - start_time
            logging.debug(f"Sleeping for {max(0, CHECK_INTERVAL - elapsed)} seconds before next check...")
            await asyncio.sleep(max(0, CHECK_INTERVAL - elapsed))

            # Send heartbeat if needed
            if asyncio.get_running_loop().time() - last_heartbeat >= HEARTBEAT_INTERVAL:
                send_heartbeat()
                last_heartbeat = asyncio.get_running_loop().time()

        except asyncio.CancelledError:
            logging.info("Shutting down gracefully...")
            break

async def main():
    """Initialize database, start tracking products, and run periodic scripts."""
    logging.debug("Initializing database...")
    initialize_database()

    try:
        await asyncio.gather(track_products(), run_am(), run_gs(), process_gamestop())
    except asyncio.CancelledError:
        logging.info("Main process interrupted. Cleaning up...")
    finally:
        logging.info("Shutdown complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Process terminated by user.")