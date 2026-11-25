import cache
from cache import TTLCache


def test_ttl_cache_expires_values_and_returns_independent_copies(monkeypatch):
    now = [100.0]
    monkeypatch.setattr(cache, "monotonic", lambda: now[0])
    ttl_cache = TTLCache()

    ttl_cache.set("key", {"items": ["milk"]}, ttl_seconds=10)
    cached_value = ttl_cache.get("key")
    cached_value["items"].append("bread")

    assert ttl_cache.get("key") == {"items": ["milk"]}

    now[0] = 110.0
    assert ttl_cache.get("key") is None


def test_ttl_cache_evicts_oldest_entry_when_full():
    ttl_cache = TTLCache(max_entries=2)
    ttl_cache.set("first", 1, ttl_seconds=60)
    ttl_cache.set("second", 2, ttl_seconds=60)
    ttl_cache.set("third", 3, ttl_seconds=60)

    assert ttl_cache.get("first") is None
    assert ttl_cache.get("second") == 2
    assert ttl_cache.get("third") == 3
