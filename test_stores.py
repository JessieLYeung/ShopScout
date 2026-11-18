from stores_database import save_store, save_nearby_stores, get_all_stores
from geolocation import get_coordinates
from stores import find_nearby_stores


def test_store_database():
    store_id = save_store(
        "Walmart",
        "Orlando, FL",
        28.5421,
        -81.3790
    )

    print("Store ID:", store_id)

    nearby_stores = [
        {
            "name": "Walmart",
            "address": "123 Main St, Orlando, FL",
            "latitude": 28.54,
            "longitude": -81.37
        },
        {
            "name": "Publix",
            "address": "456 Orange Ave, Orlando, FL",
            "latitude": 28.55,
            "longitude": -81.38
        }
    ]

    store_ids = save_nearby_stores(nearby_stores)
    print("Saved store IDs:", store_ids)

    stores = get_all_stores()

    for store in stores:
        print(dict(store))


def test_nearby_retailers():
    coordinates = get_coordinates("32801")
    nearby_stores = find_nearby_stores(coordinates)

    supported_retailers = {
        "publix": "Publix",
        "aldi": "Aldi",
        "sprouts farmers market": "Sprouts"
    }

    retailers = []

    if nearby_stores:
        for store in nearby_stores:
            name = store["name"].lower()
            retailer = supported_retailers.get(name)

            if retailer is not None and retailer not in retailers:
                retailers.append(retailer)

    print("Supported nearby retailers:", retailers)


if __name__ == "__main__":
    test_store_database()
    test_nearby_retailers()
