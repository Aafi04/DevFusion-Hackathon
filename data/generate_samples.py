"""
Generate small sample SQLite databases (2-3k rows each) for Phase 2 testing.
Runs once to create demo.db, ecommerce.db, and music.db in the data/ directory.
"""
import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

DATA_DIR = Path(__file__).parent
DB_PATH = DATA_DIR / "demo.db"
ECOM_PATH = DATA_DIR / "ecommerce.db"
MUSIC_PATH = DATA_DIR / "music.db"


def create_demo_db():
    """Create minimal demo database (3 tables, ~500 rows)."""
    print(f"Creating demo database at {DB_PATH}...")
    
    if DB_PATH.exists():
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        country TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    users = [(i, f"user_{i}", f"user{i}@example.com", random.choice(["US", "UK", "CA", "AU", "DE"]), 
              datetime.now() - timedelta(days=random.randint(0, 365))) for i in range(1, 251)]
    c.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", users)
    
    # Products table
    c.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT,
        price REAL,
        stock INTEGER
    )
    """)
    
    products = [(i, f"Product_{i}", random.choice(["Electronics", "Books", "Clothing"]), 
                 round(random.uniform(10, 500), 2), random.randint(0, 1000)) for i in range(1, 101)]
    c.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)
    
    # Orders table
    c.execute("""
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        total_amount REAL,
        created_at TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)
    
    orders = [(i, random.randint(1, 250), random.randint(1, 100), random.randint(1, 10),
              round(random.uniform(50, 5000), 2), datetime.now() - timedelta(days=random.randint(0, 365))) 
              for i in range(1, 251)]
    c.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", orders)
    
    conn.commit()
    conn.close()
    print(f"✓ Demo DB created: 3 tables, ~500 rows")


def create_ecommerce_db():
    """Create e-commerce database (5 tables, ~2.5k rows)."""
    print(f"Creating e-commerce database at {ECOM_PATH}...")
    
    if ECOM_PATH.exists():
        os.remove(ECOM_PATH)
    
    conn = sqlite3.connect(ECOM_PATH)
    c = conn.cursor()
    
    # Customers table
    c.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT UNIQUE,
        city TEXT,
        country TEXT
    )
    """)
    
    customers = [(i, f"First_{i}", f"Last_{i}", f"cust{i}@email.com", 
                 random.choice(["São Paulo", "Rio", "New York", "London", "Berlin"]),
                 random.choice(["Brazil", "US", "UK", "Germany", "Canada"])) 
                 for i in range(1, 501)]
    c.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)", customers)
    
    # Categories table
    c.execute("""
    CREATE TABLE categories (
        category_id INTEGER PRIMARY KEY,
        name TEXT UNIQUE
    )
    """)
    
    categories = [(i, name) for i, name in enumerate([
        "Electronics", "Clothing", "Home", "Sports", "Books", "Toys", "Food", "Beauty"
    ], 1)]
    c.executemany("INSERT INTO categories VALUES (?, ?)", categories)
    
    # Products table
    c.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category_id INTEGER,
        price REAL,
        stock INTEGER,
        FOREIGN KEY(category_id) REFERENCES categories(category_id)
    )
    """)
    
    products = [(i, f"Product_{i}", random.randint(1, 8), round(random.uniform(5, 1000), 2), 
                random.randint(0, 500)) for i in range(1, 401)]
    c.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)
    
    # Orders table
    c.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TIMESTAMP,
        total_amount REAL,
        status TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
    )
    """)
    
    orders = [(i, random.randint(1, 500), datetime.now() - timedelta(days=random.randint(0, 365)),
              round(random.uniform(20, 5000), 2), random.choice(["pending", "completed", "shipped", "cancelled"]))
              for i in range(1, 801)]
    c.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)
    
    # Order Items table
    c.execute("""
    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        item_price REAL,
        FOREIGN KEY(order_id) REFERENCES orders(order_id),
        FOREIGN KEY(product_id) REFERENCES products(product_id)
    )
    """)
    
    order_items = [(i, random.randint(1, 800), random.randint(1, 400), random.randint(1, 5),
                   round(random.uniform(10, 1000), 2)) for i in range(1, 1601)]
    c.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", order_items)
    
    conn.commit()
    conn.close()
    print(f"✓ E-commerce DB created: 5 tables, ~2.5k rows")


def create_music_db():
    """Create music store database (4 tables, ~2k rows)."""
    print(f"Creating music database at {MUSIC_PATH}...")
    
    if MUSIC_PATH.exists():
        os.remove(MUSIC_PATH)
    
    conn = sqlite3.connect(MUSIC_PATH)
    c = conn.cursor()
    
    # Artists table
    c.execute("""
    CREATE TABLE artists (
        artist_id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        country TEXT
    )
    """)
    
    artists = [(i, f"Artist_{i}", random.choice(["US", "UK", "Canada", "Brazil", "Japan"]))
              for i in range(1, 151)]
    c.executemany("INSERT INTO artists VALUES (?, ?, ?)", artists)
    
    # Albums table
    c.execute("""
    CREATE TABLE albums (
        album_id INTEGER PRIMARY KEY,
        title TEXT,
        artist_id INTEGER,
        release_year INTEGER,
        genre TEXT,
        FOREIGN KEY(artist_id) REFERENCES artists(artist_id)
    )
    """)
    
    albums = [(i, f"Album_{i}", random.randint(1, 150), random.randint(1995, 2024),
              random.choice(["Rock", "Pop", "Jazz", "Classical", "Hip-Hop", "Country"]))
             for i in range(1, 351)]
    c.executemany("INSERT INTO albums VALUES (?, ?, ?, ?, ?)", albums)
    
    # Tracks table
    c.execute("""
    CREATE TABLE tracks (
        track_id INTEGER PRIMARY KEY,
        album_id INTEGER,
        title TEXT,
        duration_seconds INTEGER,
        FOREIGN KEY(album_id) REFERENCES albums(album_id)
    )
    """)
    
    tracks = [(i, random.randint(1, 350), f"Track_{i}", random.randint(120, 600))
             for i in range(1, 1101)]
    c.executemany("INSERT INTO tracks VALUES (?, ?, ?, ?)", tracks)
    
    # Sales table
    c.execute("""
    CREATE TABLE sales (
        sale_id INTEGER PRIMARY KEY,
        track_id INTEGER,
        sale_date TIMESTAMP,
        price REAL,
        buyer_name TEXT,
        FOREIGN KEY(track_id) REFERENCES tracks(track_id)
    )
    """)
    
    sales = [(i, random.randint(1, 1100), datetime.now() - timedelta(days=random.randint(0, 365)),
             round(random.uniform(0.99, 2.99), 2), f"Buyer_{i}")
            for i in range(1, 601)]
    c.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?)", sales)
    
    conn.commit()
    conn.close()
    print(f"✓ Music DB created: 4 tables, ~2k rows")


if __name__ == "__main__":
    print("Generating small sample databases for Phase 2 testing...\n")
    create_demo_db()
    create_ecommerce_db()
    create_music_db()
    print("\n✓ All databases created successfully!")
    print(f"  - {DB_PATH} (demo)")
    print(f"  - {ECOM_PATH} (e-commerce)")
    print(f"  - {MUSIC_PATH} (music)")
