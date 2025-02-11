# Price and Availability Changes Tracker
This project is a price and availability tracker that scrapes product pages from Amazon and GameStop (italy, but really depends on your urls),
detects new products or price changes, and sends notifications via Telegram. The system runs asynchronously.

📂 Project Structure
Here’s a breakdown of all the main components:

1️⃣ main.py – Core Script & Task Manager
This is the main entry point of the project. It:
Loads and processes URLs from product_urls.py (Amazon) and gamestop_urls.py (GameStop).
Fetches product details from the appropriate scraper.
Compares prices and availability against stored data.
Sends notifications if changes are detected.
Runs periodic scraper updates (AM.py and GS.py).
📌 Key functions:
track_products() → Main loop that processes batches of URLs.
run_am() → Runs AM.py to update Amazon URLs.
run_gs() → Runs GS.py to update GameStop URLs.
process_gamestop() → Scrapes GameStop products every hour.

2️⃣ scraper_manager.py – Scraper Dispatcher
Handles dynamic selection of the correct scraper based on the URL.
📌 Key function:
get_product_details(url) → Automatically calls the correct scraper (amazon.py or gamestop.py).

3️⃣ AM.py – Amazon URL Scraper
Fetches Amazon product links from category pages.
Filters URLs based on keywords (e.g., Pokémon-related products).
Saves unique product URLs to product_urls.py.
📌 Key functions:
fetch_amazon_product_links() → Extracts product URLs.
update_urls() → Saves new URLs while keeping existing ones.

4️⃣ amazon.py – Amazon Product Scraper
Extracts title, price, availability, and image from an Amazon product page.
📌 Key functions:
fetch(url) → Handles Amazon requests with CAPTCHA detection & retries.
get_amazon_product_details(url) → Parses product title, price, availability, and image.
✅ Handles:
CAPTCHA detection & retry logic
Filters out non-Amazon-fulfilled products

5️⃣ GS.py – GameStop URL Scraper
Fetches pre-order product links from GameStop.
Saves unique URLs to gamestop_urls.py.
📌 Key functions:
fetch_gamestop_product_links() → Extracts product URLs.
update_urls() → Saves new URLs while keeping existing ones.

6️⃣ gamestop.py – GameStop Product Scraper
Extracts title, price, availability, and image from a GameStop product page.
📌 Key functions:
start_selenium() → Initializes a headless Selenium WebDriver.
get_gamestop_product_data(driver, url) → Extracts product details.
✅ Uses Selenium because GameStop loads data dynamically via JavaScript.

7️⃣ processing.py – Product Processing & Notifications
Handles:
Fetching product details
Comparing them with previous values
Sending notifications for new products or price changes
📌 Key functions:
process_url(url) → Calls scrapers, updates the database, and triggers notifications.
convert_price_to_float(price) → Cleans and converts price values.
✅ Handles:
Price change detection (threshold: 5%).
Automatic retries if scraping fails.
Marking invalid URLs if a product is unavailable.

8️⃣ database.py – SQLite Database
Stores product information and handles updates.
📌 Key functions:
initialize_database() → Sets up the database.
save_product_details(url, title, price, availability, image_url) → Inserts or updates a product.
fetch_previous_details(url) → Retrieves old product details for comparison.
delete_product(url) → Removes a product from the database.
✅ Includes logic for:
Detecting new products
Skipping updates if no changes occur
Marking URLs as invalid if scraping fails

9️⃣ notifications.py – Telegram & Email Alerts
Sends Telegram notifications and emails for errors or heartbeat checks.
📌 Key functions:
send_to_telegram_with_image(title, image_url, price, url, site) → Sends a Telegram notification with buttons.
should_send(current_details, previous_details) → Determines whether a notification should be sent.
send_email(subject, body) → Sends email notifications.
send_heartbeat() → Periodically sends a status email.
✅ Notification buttons:
🛒 Open {site}   ☕ Buy Me a Coffee  
📦 Prova Prime   📤 Share  
Fully automated Telegram alerts for new products & price changes!

🔟 utils.py – Helper Functions
Contains:
User-agent rotation for web requests.
Amazon URL cleaning to remove tracking parameters.
Keyword filtering to exclude unwanted products.
📌 Key functions:
clean_amazon_url(url) → Removes unnecessary Amazon URL parameters.
USER_AGENTS → A list of randomized user agents to prevent blocking.
✅ Prevents scraping issues by rotating user-agents & cleaning URLs.

🚀 How It Works
1️⃣ URL Collection
Amazon & GameStop scrapers (AM.py & GS.py) collect product URLs.
URLs are filtered & stored in product_urls.py and gamestop_urls.py.

2️⃣ Product Scraping
Amazon & GameStop scrapers extract details (amazon.py & gamestop.py).
If the product is new or the price changes, it gets saved to the database.

3️⃣ Notifications
If a product is new or its price changes by more than 5%, Telegram sends an alert.
Buttons allow users to open the site, buy you a coffee, try Amazon Prime, or share the deal.

🛠️ How to Run
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Add your Telegram bot token & settings in .env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHANNEL_ID=@yourchannelid
REFERRAL_TAG=pokemonofferte-21
AMAZON_CATEGORY_URL="https://www.amazon.it/s?k=pokemon"
GAMESTOP_PREORDER_URL="https://www.gamestop.it/preorder"

3️⃣ Run the tracker
python main.py

✅ Key Features
✔ Automated tracking of Amazon & GameStop products.
✔ Real-time notifications via Telegram when prices change.
✔ Selenium support for JavaScript-heavy sites (GameStop).
✔ Amazon CAPTCHA detection & retry logic.
✔ Flexible filtering for tracking specific product categories.
✔ Support for custom affiliate tags to monetize tracked products.

🚀 Future Improvements
 Add more e-commerce sites (Comet, Gamelife, etc.).
 Implement price history tracking for deeper insights.
 Improve scraper efficiency with async requests.
 Create a web dashboard to visualize tracked products.
 
📌 Summary
This project automates product tracking & price alerts from Amazon & GameStop. It scrapes product details, detects price changes, and sends real-time notifications to Telegram.
🔹 Built with Python + SQLite + Selenium + Telegram API
🔹 Designed for price monitoring & deal alerts
🔹 Fully automated & configurable
