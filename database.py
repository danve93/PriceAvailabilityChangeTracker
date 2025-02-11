import sqlite3

# Initialize database if it does not exist, and add missing columns
def initialize_database():
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()
    
    # Create the table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        title TEXT,
        price REAL,  -- Ensure price is stored as a REAL number
        availability BOOLEAN,
        image_url TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Check if 'is_invalid' column exists
    cursor.execute("PRAGMA table_info(products)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    if "is_invalid" not in existing_columns:
        print("[INFO] Adding missing 'is_invalid' column to the database.")
        cursor.execute("ALTER TABLE products ADD COLUMN is_invalid BOOLEAN DEFAULT 0")
        connection.commit()

    connection.close()

def save_product_details(url, title, price, availability, image_url):
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()

    # Check if product already exists
    cursor.execute("""SELECT title, price, availability FROM products WHERE url = ?""", (url,))
    existing_data = cursor.fetchone()

    if existing_data:
        existing_title, existing_price, existing_availability = existing_data

        # Skip update if nothing has changed
        if (existing_title == title and existing_price == price and existing_availability == availability):
            print(f"[DEBUG] No changes detected for {title}. Skipping update.")
            connection.close()
            return

        print(f"[INFO] 🔄 Updating product: {title}")

    else:
        print(f"[INFO] 🆕 Adding new product: {title}")

    # Insert or update product
    cursor.execute("""
    INSERT INTO products (url, title, price, availability, image_url, last_updated)
    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(url) DO UPDATE SET
        title = excluded.title,
        price = excluded.price,
        availability = excluded.availability,
        image_url = excluded.image_url,
        last_updated = CURRENT_TIMESTAMP,
        is_invalid = 0
    """, (url, title, price, availability, image_url))

    connection.commit()
    connection.close()
    print(f"[INFO] ✅ Saved product: {title} ({url})")

# Fetch previous product details from the database
def fetch_previous_details(url):
    """Retrieve previous details of a product from the database."""
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()
    cursor.execute("SELECT title, price, availability, image_url, last_updated FROM products WHERE url = ?", (url,))
    row = cursor.fetchone()
    connection.close()

    if row:
        try:
            price = float(row[1]) if row[1] is not None else 0.0  # Ensure price is retrieved as a float
        except ValueError:
            price = 0.0

        return {
            "title": row[0],
            "price": price,
            "availability": row[2],
            "image_url": row[3],
            "last_updated": row[4]
        }
    return None  # Return None if no previous data exists

# Check if a URL is already in the database
def is_url_in_database(url):
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT 1 FROM products WHERE url = ?)", (url,))
    exists = cursor.fetchone()[0]
    connection.close()
    return bool(exists)

# Mark a URL as invalid
def mark_url_as_invalid(url):
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE products SET is_invalid = 1 WHERE url = ?", (url,))
    connection.commit()
    connection.close()

# Fetch valid product URLs (excluding invalid ones)
def fetch_valid_urls():
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()
    cursor.execute("SELECT url FROM products WHERE is_invalid = 0")
    urls = [row[0] for row in cursor.fetchall()]
    connection.close()
    return urls

# Fetch invalid URLs that might need rechecking
def fetch_invalid_urls():
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()
    cursor.execute("SELECT url FROM products WHERE is_invalid = 1")
    urls = [row[0] for row in cursor.fetchall()]
    connection.close()
    return urls

# Restore a previously invalid URL if it is now valid again
def restore_valid_url(url):
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE products SET is_invalid = 0 WHERE url = ?", (url,))
    connection.commit()
    connection.close()

# 🔹 (NEW) Delete a product from the database
def delete_product(url):
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM products WHERE url = ?", (url,))
    connection.commit()
    connection.close()
    print(f"[INFO] Deleted product: {url}")

# 🔹 (NEW) Fetch all products (for debugging/exporting)
def fetch_all_products():
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    connection.close()
    return products  # Returns a list of all rows

# 🔹 (NEW) Update product availability
def update_product_availability(url, availability):
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE products SET availability = ?, last_updated = CURRENT_TIMESTAMP WHERE url = ?", (availability, url))
    connection.commit()
    connection.close()
    print(f"[INFO] Updated availability for: {url}")
