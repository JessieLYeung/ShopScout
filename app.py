import os

from flask import Flask, jsonify, request
from geolocation import get_coordinates
from stores import find_nearby_stores
from products import find_products
from comparison import filter_products, compare_products, group_products_by_type
from stores_database import save_nearby_stores

app = Flask(__name__)

@app.route("/")
def home():
    return "ShopScout"


@app.route("/search")
def search():
    zip_code = request.args.get('zip')
    product_name = request.args.get('product')

    if not zip_code or not product_name:
        return jsonify(
            {"error": "ZIP code and product are required"}
        ), 400

    if not os.getenv("GEOAPIFY_KEY"):
        return jsonify(
            {"error": "Search is not configured. Set GEOAPIFY_KEY in your .env file."}
        ), 503

    coordinates = get_coordinates(zip_code)
    if coordinates is None:
        return jsonify(
            {"error": "Unable to find the specified location"}
        ), 400

    nearby_stores = find_nearby_stores(coordinates)
    if nearby_stores is None:
        return jsonify(
            {"error": "Unable to retrieve nearby stores"}
        ), 502

    # Save nearby stores to the database
    store_ids = save_nearby_stores(nearby_stores)

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

        products = find_products(product_name, zip_code, nearby_stores)

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
        "coordinates": coordinates,
        "nearby_stores": nearby_stores,
        "products": grouped_products
    }

    if not any(grouped_products.values()):
        response["message"] = "No matching products found"

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)