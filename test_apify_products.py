from types import SimpleNamespace

import products


def test_find_products_matches_branch_and_drops_ambiguous_prices(monkeypatch):
    scraped_products = [
        {
            "name": "Whole Milk",
            "brand": "Friendly Farms",
            "retailerName": "ALDI",
            "storeAddress": "456 Main St, Orlando, FL",
            "price": 3.25,
            "size": "1 gal",
            "available": True,
            "productUrl": "https://example.com/milk",
        },
        {
            "name": "Another Milk",
            "retailerName": "ALDI",
            "price": 2.00,
            "size": "1 gal",
        },
    ]
    actor_calls = []

    class FakeDataset:
        def list_items(self):
            return SimpleNamespace(items=scraped_products)

    class FakeClient:
        def __init__(self, token):
            self.token = token

        def actor(self, actor_id):
            return self

        def call(self, run_input):
            actor_calls.append(run_input)
            return SimpleNamespace(default_dataset_id="test-dataset")

        def dataset(self, dataset_id):
            return FakeDataset()

    monkeypatch.setenv("APIFY_TOKEN", "test-token")
    monkeypatch.setattr(products, "ApifyClient", FakeClient)
    monkeypatch.setattr(products, "save_store", lambda *args: 7)
    monkeypatch.setattr(products, "add_product", lambda **kwargs: 12)
    monkeypatch.setattr(
        products,
        "add_store_listing",
        lambda **kwargs: "2026-11-25 12:00:00",
    )

    nearby_stores = [
        {
            "name": "ALDI",
            "address": "123 Main St, Orlando, FL",
            "latitude": 28.54,
            "longitude": -81.38,
            "distance_km": 0.5,
        },
        {
            "name": "ALDI",
            "address": "456 Main St, Orlando, FL",
            "latitude": 28.55,
            "longitude": -81.37,
            "distance_km": 1.0,
        },
    ]

    result = products.find_products("milk", "32801", nearby_stores)
    cached_result = products.find_products("milk", "32801", nearby_stores)

    assert len(result) == 1
    assert cached_result == result
    assert len(actor_calls) == 1
    assert result[0]["store_address"] == "456 Main St, Orlando, FL"
    assert result[0]["store_name"] == "ALDI"
    assert result[0]["store_distance_km"] == 1.0
    assert result[0]["last_updated"] == "2026-11-25 12:00:00"
