from apify_client import ApifyClient
import os
from dotenv import load_dotenv
from database import get_db_connection
from stores_database import save_store

load_dotenv()

def find_products(product_name, postal_code, nearby_stores):
    supported_retailers = {
        "publix": "Publix",
        "aldi": "Aldi",
        "sprouts farmers market": "Sprouts"
    }

    if not nearby_stores:
        print("No nearby stores found.")
        return []

    retailers = []

    for store in nearby_stores:
        name = store["name"].lower()

        retailer = next(
            (
                value for key, value in supported_retailers.items()
                if key in name
            ),
            None
        )

        if retailer and retailer not in retailers:
            retailers.append(retailer)

    if not retailers:
        print("No supported retailers found.")
        return []

    apify_token = os.getenv("APIFY_TOKEN")
    if not apify_token:
        return None

    apify_client = ApifyClient(apify_token)
    actor_client = apify_client.actor(
        "abotapi/instacart-grocery-price-scraper"
    )

    run_input = {
        "mode": "search",
        "queries": [product_name],
        "retailers": retailers,
        "postalCode": str(postal_code),
        "maxItems": 20
    }

    call_result = actor_client.call(run_input=run_input)

    if call_result is None:
        print("Actor run failed.")
        return []

    dataset_client = apify_client.dataset(
        call_result.default_dataset_id
    )

    scraped_products = dataset_client.list_items().items

    for product in scraped_products:
        retailer_name = product.get("retailerName")
        store_address = product.get("storeAddress")

        matching_store = next(
            (
                store for store in nearby_stores
                if retailer_name
                and store["name"].lower() in retailer_name.lower()
            ),
            None
        )

        if not matching_store:
            continue

        store_id = save_store(
            matching_store["name"],
            matching_store["address"],
            matching_store["latitude"],
            matching_store["longitude"]
        )

        product_id = add_product(
            name=product.get("name"),
            brand=product.get("brand"),
            package_size=product.get("size")
        )

        availability = (
            "available" if product.get("available")
            else "out_of_stock"
        )

        add_store_listing(
            product_id=product_id,
            store_id=store_id,
            price=product.get("price"),
            availability=availability,
            product_url=product.get("productUrl")
        )

    return scraped_products

def add_product(name, brand=None, category=None, package_size=None):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT product_id
        FROM Products
        WHERE name = ?
          AND brand IS ?
          AND category IS ?
          AND package_size IS ?
    """, (name, brand, category, package_size))

    existing_product = cursor.fetchone()

    if existing_product:
        connection.close()
        return existing_product["product_id"]

    cursor.execute("""
        INSERT INTO Products (name, brand, category, package_size)
        VALUES (?, ?, ?, ?)
    """, (name, brand, category, package_size))

    product_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return product_id


def search_products(search_term):
    connection = get_db_connection()
    cursor = connection.cursor()

    search_pattern = f"%{search_term}%"

    cursor.execute("""
        SELECT *
        FROM Products
        WHERE name LIKE ?
           OR brand LIKE ?
           OR category LIKE ?
        ORDER BY name ASC
    """, (search_pattern, search_pattern, search_pattern))

    products = cursor.fetchall()

    connection.close()

    return products

def add_store_listing(
    product_id,
    store_id,
    price=None,
    availability="unknown",
    product_url=None
):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO StoreListings (
            product_id,
            store_id,
            price,
            availability,
            product_url,
            last_updated
        )
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(product_id, store_id)
        DO UPDATE SET
            price = excluded.price,
            availability = excluded.availability,
            product_url = excluded.product_url,
            last_updated = CURRENT_TIMESTAMP
    """, (
        product_id,
        store_id,
        price,
        availability,
        product_url
    ))

    connection.commit()
    connection.close()

def search_product_listings(search_term):
    connection = get_db_connection()
    cursor = connection.cursor()

    search_pattern = f"%{search_term}%"

    cursor.execute("""
        SELECT
            Products.product_id,
            Products.name,
            Products.brand,
            Products.package_size,
            Stores.store_name,
            Stores.address,
            Stores.latitude,
            Stores.longitude,
            StoreListings.price,
            StoreListings.availability,
            StoreListings.product_url,
            StoreListings.last_updated
        FROM StoreListings
        JOIN Products
            ON StoreListings.product_id = Products.product_id
        JOIN Stores
            ON StoreListings.store_id = Stores.store_id
        WHERE Products.name LIKE ?
           OR Products.brand LIKE ?
           OR Products.category LIKE ?
        ORDER BY
            CASE WHEN StoreListings.price IS NULL THEN 1 ELSE 0 END,
            StoreListings.price ASC
    """, (search_pattern, search_pattern, search_pattern))

    results = cursor.fetchall()
    connection.close()

    return results
