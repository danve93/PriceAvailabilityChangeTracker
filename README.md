# 📊 Price & Availability Change Tracker

A fully automated **price tracker and notification system** for **Amazon** and **GameStop**. It scrapes product pages, detects **new products** and **price changes**, and sends real-time **Telegram alerts**.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green) ![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 🚀 Features
✔ **Tracks Amazon & GameStop products** automatically  
✔ **Sends Telegram notifications** for new products & price drops  
✔ **Supports affiliate links** for Amazon monetization  
✔ **Handles Amazon CAPTCHA detection & retries**  
✔ **Filters products using custom keywords**  
✔ **Uses Selenium for JavaScript-based scraping** (GameStop)  

---

## 📂 Project Structure
```
📦 price-tracker
 ┓ 🐝 main.py               # Main script that manages product tracking
 ┓ 🐝 scraper_manager.py     # Automatically selects the correct scraper
 ┓ 🐝 AM.py                  # Amazon URL scraper
 ┓ 🐝 amazon.py              # Amazon product details scraper
 ┓ 🐝 GS.py                  # GameStop URL scraper
 ┓ 🐝 gamestop.py            # GameStop product details scraper
 ┓ 🐝 database.py            # SQLite database management
 ┓ 🐝 notifications.py       # Sends Telegram & email notifications
 ┓ 🐝 processing.py          # Handles product updates & comparisons
 ┓ 🐝 utils.py               # Helper functions (user-agents, URL cleaning)
 ┓ 🐝 requirements.txt       # Python dependencies
 ┓ 🐝 README.md              # This documentation
```

---

## 📌 How It Works
1️⃣ **Collects product URLs**  
   - `AM.py` scrapes **Amazon product links**  
   - `GS.py` scrapes **GameStop pre-order links**  

2️⃣ **Scrapes product details**  
   - `amazon.py` extracts **title, price, availability, image**  
   - `gamestop.py` extracts **product data using Selenium**  

3️⃣ **Compares with previous data**  
   - If a **new product is found** or **price changes**, it's stored in SQLite  

4️⃣ **Sends a Telegram alert**  
   - 🚀 Users get notified instantly  

---

## 📄 Installation

### 🔹 **1. Clone the repository**
```bash
git clone https://github.com/yourusername/price-tracker.git
cd price-tracker
```

### 🔹 **2. Install dependencies**
```bash
pip install -r requirements.txt
```

### 🔹 **3. Set up the database**
```bash
python -c "from database import initialize_database; initialize_database()"
```

### 🔹 **4. Add your Telegram bot token & settings in `.env`**
```ini
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHANNEL_ID=@yourchannelid
REFERRAL_TAG=pokemonofferte-21
AMAZON_CATEGORY_URL="https://www.amazon.it/s?k=pokemon"
GAMESTOP_PREORDER_URL="https://www.gamestop.it/preorder"
```

### 🔹 **5. Run the tracker**
```bash
python main.py
```

---

## 📢 Telegram Notifications
When a **new product is added** or **a price changes**, a Telegram message is sent with **inline buttons**:

📅 **Example Message:**
```
Pokémon Booster Box 🎉
👉🏼 29.99€ da Amazon
```

💼 **Buttons:**
```
🎈 Open Site       ☕ Buy Me a Coffee  
🛆 Prova Prime     📤 Share  
```

---

## 📊 How Data Is Processed

### 🛒 **Amazon Scraping**
- `AM.py` collects product links & filters **relevant products**
- `amazon.py` scrapes **title, price, availability, image**
- If **price changes by more than 5%**, an alert is triggered

### 🎮 **GameStop Scraping**
- `GS.py` scrapes **pre-order product links**
- `gamestop.py` extracts **product data using Selenium**
- If the product **is no longer available**, it’s flagged in the database

---

## 🛠️ Configuration
### 🔹 **Modify tracked products**
Edit the **keywords** in `utils.py`:
```python
KEYWORDS = ["pokemon", "booster", "elite trainer box"]
EXCLUDED_KEYWORDS = ["random", "assortita", "Heartforcards"]
```

### 🔹 **Change price change threshold**
Modify the percentage in `processing.py`:
```python
PRICE_CHANGE_THRESHOLD = 0.05  # 5% price change required for notification
```

### 🔹 **Enable/Disable sites**
If you want to **disable GameStop tracking**, remove `run_gs()` from `main.py`:
```python
await asyncio.gather(track_products(), run_am())
```

---

## 🚀 Future Improvements
- [ ] **Support for more e-commerce sites (BestBuy, Walmart, etc.)**  
- [ ] **Web dashboard to visualize tracked products**  
- [ ] **Price history tracking for trends**  

---

## 👉 License
This project is licensed under the **MIT License**.

---

🚀 **Start tracking product deals today!** 🎯

