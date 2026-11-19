from unittest.mock import patch
from app import app

client = app.test_client()

def test_search_endpoint():
    response = client.get("/search")

    print("Status code:", response.status_code)
    print("Response:", response.json)

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

        response = client.get("/search?zip=32801&product=milk")

        print("Status code:", response.status_code)
        print("Response:", response.json)

        assert response.status_code == 200
        assert response.json["location"] == "32801"
        assert response.json["product_name"] == "milk"
        assert len(response.json["products"]["volume"]) == 1
        assert response.json["products"]["volume"][0]["retailer"] == "Publix"

        print("All assertions passed!")

    with patch("app.get_coordinates") as mock_coordinates:

        mock_coordinates.return_value = None

        response = client.get("/search?zip=00000&product=milk")

        print("Status code:", response.status_code)
        print("Response:", response.json)

        assert response.status_code == 400
        assert response.json["error"] == "Unable to find the specified location"

        print("Invalid location test passed!")

    with patch("app.get_coordinates") as mock_coordinates, \
        patch("app.find_nearby_stores") as mock_stores:

        mock_coordinates.return_value = {
            "lat": 28.54,
            "lon": -81.38
        }

        mock_stores.return_value = None

        response = client.get("/search?zip=32801&product=milk")

        print("Status code:", response.status_code)
        print("Response:", response.json)

        assert response.status_code == 502
        assert response.json["error"] == "Unable to retrieve nearby stores"

        print("Store API failure test passed!")

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

        response = client.get("/search?zip=32801&product=milk")

        print("Status code:", response.status_code)
        print("Response:", response.json)

        assert response.status_code == 502
        assert response.json["error"] == "Unable to retrieve products"

        print("Product API failure test passed!")

    with patch("app.get_coordinates") as mock_coordinates, \
        patch("app.find_nearby_stores") as mock_stores, \
        patch("app.find_products") as mock_products:

        mock_coordinates.return_value = {
            "lat": 28.54,
            "lon": -81.38
        }

        mock_stores.return_value = []

        response = client.get("/search?zip=32801&product=milk")

        assert response.status_code == 200
        assert response.json["nearby_stores"] == []
        assert response.json["products"] == {
            "volume": [],
            "weight": [],
            "count": []
        }

        mock_products.assert_not_called()

        print("Empty stores test passed!")
