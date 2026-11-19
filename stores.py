import requests
import os
from dotenv import load_dotenv

load_dotenv()

GEOAPIFY_KEY = os.getenv("GEOAPIFY_KEY")
url = "https://api.geoapify.com/v2/places"


def find_nearby_stores(coordinates):
    if coordinates is None:
        return None
    if coordinates.get("lat") is None or coordinates.get("lon") is None:
        return None
    latitude = coordinates["lat"]
    longitude = coordinates["lon"]

    search_filter=f"circle:{longitude},{latitude},5000"

    try:
        response = requests.get(
            url,
            params = {
                "categories": "commercial.supermarket", 
                "filter": search_filter, 
                "apiKey": GEOAPIFY_KEY
                },
            timeout = 10
            )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        return None
    
    stores_list = data.get("features", [])
    nearby_store = []
    
    for store in stores_list:
        properties = store.get("properties", {})
        store_name = properties.get("name")
        store_address = properties.get("formatted")
        
        if store_name and store_address:
            coordinates = store.get("geometry", {}).get("coordinates", [])

            if len(coordinates) >= 2:
                store_info = {
                    "name": store_name,
                    "address": store_address,
                    "longitude": coordinates[0],
                    "latitude": coordinates[1]
                }

                nearby_store.append(store_info)

    return nearby_store