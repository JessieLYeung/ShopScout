from flask import Flask, jsonify, request
from geolocation import get_coordinates

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
            {"error": "Location and product are required"},
            400
        )
    coordinates = get_coordinates(location)
    # write code to find nearby stores here
    return jsonify({
        "location": location,
        "product": product,
        "coordinates": coordinates
    }
    )

if __name__ == "__main__":
    app.run(debug=True)