import os
from time import perf_counter

from flask import Flask, g, jsonify, request
from geolocation import get_coordinates
from stores import find_nearby_stores, add_store_distances
from products import find_products
from comparison import filter_products, compare_products, group_products_by_type
from stores_database import save_nearby_stores
from database import create_tables

app = Flask(__name__)
create_tables()


def _timed_search_stage(stage, operation, *args, **kwargs):
    started_at = perf_counter()
    try:
        return operation(*args, **kwargs)
    finally:
        app.logger.info(
            "search_stage=%s duration_ms=%.1f",
            stage,
            (perf_counter() - started_at) * 1000,
        )


@app.before_request
def start_search_timer():
    if request.endpoint == "search":
        g.search_started_at = perf_counter()


@app.after_request
def log_search_duration(response):
    started_at = getattr(g, "search_started_at", None)
    if started_at is not None:
        app.logger.info(
            "search_total status=%s duration_ms=%.1f",
            response.status_code,
            (perf_counter() - started_at) * 1000,
        )
    return response


@app.route("/")
def home():
    return "ShopScout"


@app.route("/search")
def search():
    zip_code = request.args.get('zip')
    product_name = request.args.get('product')
    try:
        radius_km = int(request.args.get("radius_km", "5"))
    except ValueError:
        return jsonify({"error": "Radius must be 5, 10, or 25 km"}), 400

    if not zip_code or not product_name:
        return jsonify(
            {"error": "ZIP code and product are required"}
        ), 400

    if radius_km not in (5, 10, 25):
        return jsonify({"error": "Radius must be 5, 10, or 25 km"}), 400

    if not os.getenv("GEOAPIFY_KEY"):
        return jsonify(
            {"error": "Search is not configured. Set GEOAPIFY_KEY in your .env file."}
        ), 503

    coordinates = _timed_search_stage(
        "geocoding",
        get_coordinates,
        zip_code,
    )
    if coordinates is None:
        return jsonify(
            {"error": "Unable to find the specified location"}
        ), 400

    nearby_stores = _timed_search_stage(
        "nearby_stores",
        find_nearby_stores,
        coordinates,
        radius_km * 1000,
    )
    if nearby_stores is None:
        return jsonify(
            {"error": "Unable to retrieve nearby stores"}
        ), 502

    nearby_stores = add_store_distances(nearby_stores, coordinates)
    save_nearby_stores(nearby_stores)

    # Initialize empty product groups
    grouped_products = {
        "volume": [],
        "weight": [],
        "count": []
    }

    # Only search for products if nearby stores exist
    if nearby_stores:
        if not os.getenv("APIFY_TOKEN"):
            return jsonify(
                {"error": "Product search is not configured. Set APIFY_TOKEN in your .env file."}
            ), 503

        products = _timed_search_stage(
            "product_search",
            find_products,
            product_name,
            zip_code,
            nearby_stores,
        )

        if products is None:
            return jsonify(
                {"error": "Unable to retrieve products"}
            ), 502

        filtered_products = filter_products(products, product_name)
        compared_products = compare_products(filtered_products)
        grouped_products = group_products_by_type(compared_products)

    response = {
        "location": zip_code,
        "product_name": product_name,
        "radius_km": radius_km,
        "coordinates": coordinates,
        "nearby_stores": nearby_stores,
        "products": grouped_products
    }

    if not any(grouped_products.values()):
        response["message"] = "No matching products found"

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)