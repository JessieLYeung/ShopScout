import requests
import os
import math
from dotenv import load_dotenv
from cache import TTLCache

load_dotenv()

GEOAPIFY_KEY = os.getenv("GEOAPIFY_KEY")
url = "https://api.geoapify.com/v2/places"
_nearby_stores_cache = TTLCache()
_NEARBY_STORES_CACHE_TTL = 6 * 60 * 60


def find_nearby_stores(coordinates, radius_meters=5000):
    if coordinates is None:
        return None
    if coordinates.get("lat") is None or coordinates.get("lon") is None:
        return None
    latitude = coordinates["lat"]
    longitude = coordinates["lon"]
    cache_key = (
        round(latitude, 5),
        round(longitude, 5),
        radius_meters,
    )
    cached_stores = _nearby_stores_cache.get(cache_key)
    if cached_stores is not None:
        return cached_stores

    search_filter = f"circle:{longitude},{latitude},{radius_meters}"

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

    _nearby_stores_cache.set(
        cache_key,
        nearby_store,
        _NEARBY_STORES_CACHE_TTL,
    )
    return nearby_store


def add_store_distances(stores, coordinates):
    latitude = math.radians(coordinates["lat"])
    longitude = math.radians(coordinates["lon"])

    for store in stores:
        store_latitude = math.radians(store["latitude"])
        store_longitude = math.radians(store["longitude"])
        latitude_delta = store_latitude - latitude
        longitude_delta = store_longitude - longitude
        haversine = (
            math.sin(latitude_delta / 2) ** 2
            + math.cos(latitude)
            * math.cos(store_latitude)
            * math.sin(longitude_delta / 2) ** 2
        )
        store["distance_km"] = round(
            6371 * 2 * math.atan2(
                math.sqrt(haversine),
                math.sqrt(1 - haversine),
            ),
            1,
        )

    return sorted(stores, key=lambda store: store["distance_km"])