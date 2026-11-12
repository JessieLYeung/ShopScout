import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_coordinates(location):
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

    return {
        "lat": data["features"][0]["properties"]["lat"],
        "lon": data["features"][0]["properties"]["lon"]
    }
