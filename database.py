import sqlite3
from pathlib import Path

# Keep the database file in the project directory
DATABASE_PATH = Path(__file__).resolve().parent / "shopscout.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT,
            category TEXT,
            package_size TEXT
        );

        CREATE TABLE IF NOT EXISTS Stores (
            store_id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_name TEXT NOT NULL,
            address TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS StoreListings (
            listing_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            store_id INTEGER NOT NULL,
            price REAL CHECK (price IS NULL OR price >= 0),
            availability TEXT NOT NULL DEFAULT 'unknown'
                CHECK (availability IN (
                    'available',
                    'out_of_stock',
                    'unknown'
                )),
            product_url TEXT,
            last_updated TEXT,

            FOREIGN KEY (product_id)
                REFERENCES Products(product_id),

            FOREIGN KEY (store_id)
                REFERENCES Stores(store_id),

            UNIQUE (product_id, store_id)
        );

        CREATE INDEX IF NOT EXISTS idx_products_name
            ON Products(name);
        CREATE INDEX IF NOT EXISTS idx_store_listings_product
            ON StoreListings(product_id);
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")
