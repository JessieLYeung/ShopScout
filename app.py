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
    if location:
        coordinates = get_coordinates(location)
        # code to find nearby stores here
    return jsonify(
        # nearby stores and products
    )

if __name__ == "__main__":
    app.run(debug=True)