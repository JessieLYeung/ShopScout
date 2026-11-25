import requests
import os
from dotenv import load_dotenv
from cache import TTLCache

load_dotenv()

_coordinates_cache = TTLCache()
_COORDINATES_CACHE_TTL = 24 * 60 * 60


def get_coordinates(location):
    cache_key = str(location).strip().casefold()
    cached_coordinates = _coordinates_cache.get(cache_key)
    if cached_coordinates is not None:
        return cached_coordinates

    GEOAPIFY_KEY = os.getenv("GEOAPIFY_KEY")
    url = "https://api.geoapify.com/v1/geocode/search"
    try:
        response = requests.get(url,
                                params = {"text": location, "apiKey": GEOAPIFY_KEY},
                                timeout = 10
                                )
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.RequestException:
        return None

    if not data["features"]:
        return None

    coordinates = {
        "lat": data["features"][0]["properties"]["lat"],
        "lon": data["features"][0]["properties"]["lon"]
    }
    _coordinates_cache.set(
        cache_key,
        coordinates,
        _COORDINATES_CACHE_TTL,
    )
    return coordinates
