import geolocation


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


def test_get_coordinates_returns_first_geocoding_result(monkeypatch):
    request = {}
    calls = []

    def fake_get(url, params, timeout):
        calls.append(params["text"])
        request.update(params)
        request["timeout"] = timeout
        return FakeResponse({
            "features": [
                {"properties": {"lat": 28.54, "lon": -81.38}},
            ],
        })

    monkeypatch.setattr(geolocation.requests, "get", fake_get)

    assert geolocation.get_coordinates("cache-test-32801") == {
        "lat": 28.54,
        "lon": -81.38,
    }
    assert geolocation.get_coordinates("CACHE-TEST-32801") == {
        "lat": 28.54,
        "lon": -81.38,
    }
    assert request["text"] == "cache-test-32801"
    assert request["timeout"] == 10
    assert calls == ["cache-test-32801"]


def test_get_coordinates_returns_none_for_no_results(monkeypatch):
    monkeypatch.setattr(
        geolocation.requests,
        "get",
        lambda *args, **kwargs: FakeResponse({"features": []}),
    )

    assert geolocation.get_coordinates("no such place") is None
