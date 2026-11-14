from flask import Flask, jsonify, request
from geolocation import get_coordinates
from stores import find_nearby_stores

app = Flask(__name__)

@app.route("/")
def home():
    return "ShopScout"

@app.route("/search")
def search():
    location = request.args.get('q')
    product = request.args.get('p')
    if not location or not product:
        return jsonify(
            {"error": "Location and product are required"}
        ), 400

    coordinates = get_coordinates(location)
    if coordinates is None:
        return jsonify(
            {"error": "Unable to find the specified location"}
        ), 400
    
    nearby_stores = find_nearby_stores(coordinates)
    if nearby_stores is None:
        return jsonify(
            {"error": "Unable to retrieve nearby stores"}
        ), 502
    return jsonify({
        "location": location,
        "product": product,
        "coordinates": coordinates,
        "nearby stores": nearby_stores
    })

if __name__ == "__main__":
    app.run(debug=True)