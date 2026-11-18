from flask import Flask, jsonify, request
from geolocation import get_coordinates
from stores import find_nearby_stores
from products import find_products
from comparison import filter_products, compare_products, group_products_by_type

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
    if not nearby_stores:
        return jsonify({
            "location": zip_code,
            "coordinates": coordinates,
            "nearby_stores": [],
            "product_name": product_name,
            "products": {
                "volume": [],
                "weight": [],
                "count": []
        }
        }), 200

    products = find_products(product_name, zip_code, nearby_stores)
    if products is None:
        return jsonify(
            {"error": "Unable to retrieve products"}
        ), 502

    if not products:
        return jsonify(
            {"products": [], "message": "No matching products found"}, 200
        )

    filtered_products = filter_products(products, product_name)
    compared_products = compare_products(filtered_products)
    grouped_products = group_products_by_type(compared_products)

    return jsonify({
        "location": zip_code,
        "product_name": product_name,
        "coordinates": coordinates,
        "nearby_stores": nearby_stores,
        "products": grouped_products
    })

if __name__ == "__main__":
    app.run(debug=True)