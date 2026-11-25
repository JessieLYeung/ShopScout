from apify_client import ApifyClient
import os
import re
from dotenv import load_dotenv
from database import get_db_connection
from stores_database import save_store
from cache import TTLCache

load_dotenv()

_product_search_cache = TTLCache()
_PRODUCT_SEARCH_CACHE_TTL = 5 * 60


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

    cache_key = (
        product_name.strip().casefold(),
        str(postal_code).strip(),
        tuple(sorted(
            (
                str(store.get("name") or "").casefold(),
                str(store.get("address") or "").casefold(),
                store.get("latitude"),
                store.get("longitude"),
            )
            for store in nearby_stores
        )),
    )
    cached_products = _product_search_cache.get(cache_key)
    if cached_products is not None:
        return cached_products

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
    matched_products = []

    for product in scraped_products:
        retailer_name = product.get("retailerName")
        matching_store = _match_nearby_store(
            retailer_name,
            product.get("storeAddress"),
            nearby_stores,
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

        available = product.get("available")
        availability = (
            "unknown" if available is None
            else "available" if available
            else "out_of_stock"
        )

        last_updated = add_store_listing(
            product_id=product_id,
            store_id=store_id,
            price=product.get("price"),
            availability=availability,
            product_url=product.get("productUrl")
        )

        matched_products.append({
            **product,
            "store_name": matching_store["name"],
            "store_address": matching_store["address"],
            "store_distance_km": matching_store.get("distance_km"),
            "last_updated": last_updated,
        })

    _product_search_cache.set(
        cache_key,
        matched_products,
        _PRODUCT_SEARCH_CACHE_TTL,
    )
    return matched_products


def _retailer_key(name):
    if not name:
        return None

    normalized_name = str(name).casefold()
    for retailer in ("publix", "aldi", "sprouts"):
        if retailer in normalized_name:
            return retailer
    return None


def _address_key(address):
    return re.sub(r"[^a-z0-9]", "", str(address or "").casefold())


def _match_nearby_store(retailer_name, product_address, nearby_stores):
    product_retailer = _retailer_key(retailer_name)
    if not product_retailer:
        return None

    candidates = [
        store for store in nearby_stores
        if _retailer_key(store.get("name")) == product_retailer
    ]
    if not candidates:
        return None

    product_address_key = _address_key(product_address)
    if len(product_address_key) < 10:
        return candidates[0] if len(candidates) == 1 else None

    address_matches = [
        store for store in candidates
        if (
            _address_key(store.get("address")) == product_address_key
            or (
                len(product_address_key) >= 10
                and (
                    product_address_key in _address_key(store.get("address"))
                    or _address_key(store.get("address")) in product_address_key
                )
            )
        )
    ]
    if len(address_matches) == 1:
        return address_matches[0]
    return None

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
    cursor.execute("""
        SELECT last_updated
        FROM StoreListings
        WHERE product_id = ? AND store_id = ?
    """, (product_id, store_id))
    last_updated = cursor.fetchone()["last_updated"]
    connection.close()
    return last_updated

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
