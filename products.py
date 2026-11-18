from apify_client import ApifyClient
import os
from dotenv import load_dotenv

load_dotenv()

def find_products(product_name, postal_code, nearby_stores):
    supported_retailers = {
        "publix": "Publix",
        "aldi": "Aldi",
        "sprouts farmers market": "Sprouts"
    }

    if not nearby_stores:
        print("No nearby stores found.")
        return []

    retailers = []

    for store in nearby_stores:
        name = store["name"].lower()
        retailer = supported_retailers.get(name)

        if retailer is not None and retailer not in retailers:
            retailers.append(retailer)

    if not retailers:
        print("No supported retailers found.")
        return []

    apify_token = os.getenv("APIFY_TOKEN")
    if not apify_token:
        return None

    apify_client = ApifyClient(apify_token)
    actor_client = apify_client.actor('abotapi/instacart-grocery-price-scraper')

    run_input = {
        "mode": "search",
        "queries": [product_name],
        "retailers": retailers,
        "postalCode": str(postal_code),
        "maxItems": 20
    }
    call_result = actor_client.call(run_input=run_input)

    if call_result is None:
        print('Actor run failed.')
        return []

    dataset_client = apify_client.dataset(call_result.default_dataset_id)
    list_items_result = dataset_client.list_items()

    return list_items_result.items