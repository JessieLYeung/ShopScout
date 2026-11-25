import pytest

import database
import stores
from stores import add_store_distances
from stores_database import get_all_stores, save_nearby_stores, save_store


@pytest.fixture
def temporary_database(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "shopscout.db")
    database.create_tables()


def test_store_records_are_persisted(temporary_database):
    first_id = save_store("Publix", "123 Main St", 28.54, -81.38)
    duplicate_id = save_store("Publix", "123 Main St", 28.54, -81.38)
    store_ids = save_nearby_stores([
        {
            "name": "ALDI",
            "address": "456 Main St",
            "latitude": 28.55,
            "longitude": -81.37,
        }
    ])

    assert first_id == duplicate_id
    assert len(store_ids) == 1
    assert len(get_all_stores()) == 2


def test_nearby_stores_include_distance_and_are_sorted():
    coordinates = {"lat": 28.54, "lon": -81.38}
    stores = [
        {
            "name": "Far",
            "address": "Far away",
            "latitude": 29.0,
            "longitude": -81.38,
        },
        {
            "name": "Close",
            "address": "Nearby",
            "latitude": 28.541,
            "longitude": -81.38,
        },
    ]

    sorted_stores = add_store_distances(stores, coordinates)

    assert [store["name"] for store in sorted_stores] == ["Close", "Far"]
    assert sorted_stores[0]["distance_km"] == 0.1
    assert sorted_stores[1]["distance_km"] > 50


def test_store_search_uses_requested_radius(monkeypatch):
    request_params = {}
    calls = []

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"features": []}

    def fake_get(url, params, timeout):
        calls.append(params)
        request_params.update(params)
        return FakeResponse()

    monkeypatch.setattr(stores.requests, "get", fake_get)

    result = stores.find_nearby_stores(
        {"lat": 28.54, "lon": -81.38},
        radius_meters=10000,
    )
    cached_result = stores.find_nearby_stores(
        {"lat": 28.54, "lon": -81.38},
        radius_meters=10000,
    )

    assert result == []
    assert cached_result == []
    assert len(calls) == 1
    assert request_params["filter"].endswith(",10000")
