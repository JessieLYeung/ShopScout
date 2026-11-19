from unittest.mock import patch
from app import app

client = app.test_client()


def search(path):
    with patch.dict(
        "os.environ",
        {"GEOAPIFY_KEY": "test-key", "APIFY_TOKEN": "test-token"}
    ):
        return client.get(path)


def test_search_endpoint():
    # Successful search
    with patch("app.get_coordinates") as mock_coordinates, \
        patch("app.find_nearby_stores") as mock_stores, \
        patch("app.find_products") as mock_products:

        mock_coordinates.return_value = {
            "lat": 28.54,
            "lon": -81.38
        }

        mock_stores.return_value = [
            {
                "name": "Publix",
                "address": "Example Publix Address",
                "latitude": 28.54,
                "longitude": -81.38
            }
        ]

        mock_products.return_value = [
            {
                "name": "Whole Milk",
                "price": 4.99,
                "size": "1 gal",
                "retailerName": "Publix"
            }
        ]

        response = search("/search?zip=32801&product=milk")

        assert response.status_code == 200
        assert response.json["location"] == "32801"
        assert response.json["product_name"] == "milk"
        assert len(response.json["products"]["volume"]) == 1
        assert response.json["products"]["volume"][0]["retailer"] == "Publix"

    # Invalid location
    with patch("app.get_coordinates") as mock_coordinates:
        mock_coordinates.return_value = None

        response = search("/search?zip=00000&product=milk")

        assert response.status_code == 400
        assert response.json["error"] == "Unable to find the specified location"

    # Store API failure
    with patch("app.get_coordinates") as mock_coordinates, \
        patch("app.find_nearby_stores") as mock_stores:

        mock_coordinates.return_value = {
            "lat": 28.54,
            "lon": -81.38
        }
        mock_stores.return_value = None

        response = search("/search?zip=32801&product=milk")

        assert response.status_code == 502
        assert response.json["error"] == "Unable to retrieve nearby stores"

    # Product API failure
    with patch("app.get_coordinates") as mock_coordinates, \
        patch("app.find_nearby_stores") as mock_stores, \
        patch("app.find_products") as mock_products:

        mock_coordinates.return_value = {
            "lat": 28.54,
            "lon": -81.38
        }

        mock_stores.return_value = [
            {
                "name": "Publix",
                "address": "Example Publix Address",
                "latitude": 28.54,
                "longitude": -81.38
            }
        ]

        mock_products.return_value = None

        response = search("/search?zip=32801&product=milk")

        assert response.status_code == 502
        assert response.json["error"] == "Unable to retrieve products"

    # No nearby stores
    with patch("app.get_coordinates") as mock_coordinates, \
        patch("app.find_nearby_stores") as mock_stores, \
        patch("app.find_products") as mock_products:

        mock_coordinates.return_value = {
            "lat": 28.54,
            "lon": -81.38
        }

        mock_stores.return_value = []

        response = search("/search?zip=32801&product=milk")

        assert response.status_code == 200
        assert response.json["nearby_stores"] == []
        assert response.json["products"] == {
            "volume": [],
            "weight": [],
            "count": []
        }
        assert response.json["location"] == "32801"
        assert response.json["product_name"] == "milk"

        mock_products.assert_not_called()

    # Missing Geoapify API key
    with patch.dict("os.environ", {}, clear=True):
        response = client.get("/search?zip=32801&product=milk")

        assert response.status_code == 503
        assert "GEOAPIFY_KEY" in response.json["error"]

    # Missing Apify API token
    with patch.dict(
        "os.environ",
        {"GEOAPIFY_KEY": "test-key"},
        clear=True
    ), patch("app.get_coordinates") as mock_coordinates, \
       patch("app.find_nearby_stores") as mock_stores:

        mock_coordinates.return_value = {
            "lat": 28.54,
            "lon": -81.38
        }

        mock_stores.return_value = [
            {
                "name": "Publix",
                "address": "Example address"
            }
        ]

        response = client.get("/search?zip=32801&product=milk")

        assert response.status_code == 503
        assert "APIFY_TOKEN" in response.json["error"]
