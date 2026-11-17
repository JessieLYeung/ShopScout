from stores_database import save_store

store_id = save_store(
    "Walmart",
    "Orlando, FL",
    28.5421,
    -81.3790
)

print("Store ID:", store_id)

from stores_database import save_nearby_stores

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

from stores_database import get_all_stores

stores = get_all_stores()

for store in stores:
    print(dict(store))