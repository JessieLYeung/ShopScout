import unittest

from app import create_app


class SearchApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_search_returns_sorted_discounted_prices(self):
        response = self.client.post(
            "/search",
            json={"location": "Orlando, FL", "item": "coca cola"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["location"], "Orlando, FL")
        self.assertEqual(body["item"], "coca cola")
        self.assertGreater(len(body["results"]), 0)

        final_prices = [result["final_price"] for result in body["results"]]
        self.assertEqual(final_prices, sorted(final_prices))
        self.assertAlmostEqual(body["results"][0]["final_price"], 2.63, places=2)

    def test_search_requires_location_and_item(self):
        response = self.client.post("/search", json={"location": "", "item": ""})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
