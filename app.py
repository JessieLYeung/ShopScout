import json
import math
import os
import sqlite3
import urllib.parse
import urllib.request
from pathlib import Path

from flask import Flask, jsonify, request


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "shopping.db"

KNOWN_LOCATIONS = {
    "orlando, fl": (28.5383, -81.3792),
    "miami, fl": (25.7617, -80.1918),
    "tampa, fl": (27.9506, -82.4572),
}


def create_app():
    app = Flask(__name__)
    app.config["DATABASE"] = str(DB_PATH)
    init_db(app.config["DATABASE"])

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/search")
    def search():
        payload = request.get_json(silent=True) or {}
        location = (payload.get("location") or "").strip()
        item = (payload.get("item") or "").strip()

        if not location or not item:
            return jsonify({"error": "location and item are required"}), 400

        try:
            latitude, longitude = geocode_location(location)
        except ValueError:
            return jsonify({"error": "location could not be geocoded"}), 404

        results = search_item_prices(
            app.config["DATABASE"], latitude, longitude, item=item
        )
        return jsonify(
            {
                "location": location,
                "coordinates": {"latitude": latitude, "longitude": longitude},
                "item": item,
                "results": results,
            }
        )

    return app


def geocode_location(location):
    normalized = location.lower()
    if normalized in KNOWN_LOCATIONS:
        return KNOWN_LOCATIONS[normalized]

    api_key = os.getenv("GEOAPIFY_API_KEY")
    if not api_key:
        raise ValueError("location could not be geocoded")

    query = urllib.parse.urlencode({"text": location, "apiKey": api_key, "limit": 1})
    url = f"https://api.geoapify.com/v1/geocode/search?{query}"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            body = response.read()
        payload = json.loads(body.decode("utf-8"))
        feature = (payload.get("features") or [None])[0]
        if not feature:
            raise ValueError("location could not be geocoded")
        coordinates = feature.get("geometry", {}).get("coordinates", [])
        if len(coordinates) != 2:
            raise ValueError("location could not be geocoded")
        longitude, latitude = coordinates
        return float(latitude), float(longitude)
    except Exception as exc:  # pragma: no cover
        raise ValueError("location could not be geocoded") from exc


def distance_km(latitude_1, longitude_1, latitude_2, longitude_2):
    radius_km = 6371.0
    lat1 = math.radians(latitude_1)
    lon1 = math.radians(longitude_1)
    lat2 = math.radians(latitude_2)
    lon2 = math.radians(longitude_2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_km * c


def search_item_prices(database_path, latitude, longitude, item):
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT
                s.name AS store_name,
                s.address AS store_address,
                s.latitude AS store_latitude,
                s.longitude AS store_longitude,
                p.item_name AS item_name,
                p.price AS price,
                p.discount_percent AS discount_percent
            FROM item_prices p
            JOIN stores s ON s.id = p.store_id
            WHERE lower(p.item_name) LIKE '%' || lower(?) || '%'
            """,
            (item,),
        ).fetchall()

    output = []
    for row in rows:
        store_distance_km = distance_km(
            latitude,
            longitude,
            row["store_latitude"],
            row["store_longitude"],
        )
        if store_distance_km > 75:
            continue
        final_price = round(row["price"] * (1 - (row["discount_percent"] / 100.0)), 2)
        output.append(
            {
                "store": row["store_name"],
                "address": row["store_address"],
                "distance_km": round(store_distance_km, 2),
                "item": row["item_name"],
                "price": round(row["price"], 2),
                "discount_percent": row["discount_percent"],
                "final_price": final_price,
            }
        )
    return sorted(output, key=lambda result: (result["final_price"], result["distance_km"]))


def init_db(database_path):
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS stores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS item_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                price REAL NOT NULL,
                discount_percent REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
            """
        )
        store_count = connection.execute("SELECT COUNT(*) FROM stores").fetchone()[0]
        if store_count == 0:
            connection.executemany(
                """
                INSERT INTO stores (name, address, latitude, longitude)
                VALUES (?, ?, ?, ?)
                """,
                [
                    ("Fresh Market", "123 Orange Ave, Orlando, FL", 28.5412, -81.3787),
                    ("Value Foods", "450 Pine St, Orlando, FL", 28.5470, -81.3902),
                    ("Budget Grocer", "789 Lake Rd, Orlando, FL", 28.5215, -81.3659),
                ],
            )
            connection.executemany(
                """
                INSERT INTO item_prices (store_id, item_name, price, discount_percent)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (1, "coca cola", 2.99, 10),
                    (2, "coca cola", 2.79, 5),
                    (3, "coca cola", 3.09, 15),
                    (1, "bread", 3.49, 0),
                    (2, "bread", 3.19, 5),
                    (3, "bread", 3.29, 0),
                ],
            )
        connection.commit()


app = create_app()


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(debug=debug_mode)
