import unittest
from datetime import date

from fastapi.testclient import TestClient

from backend.app import app, history, future_months, this_calendar_month
from backend.forecasting import MAX_HORIZON, shift_month


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_and_frontend_both_serve(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["model_trained_through"], "2026-09-01")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

    def test_metadata_uses_actual_crop_district_coverage(self):
        response = self.client.get("/api/metadata")
        self.assertEqual(response.status_code, 200)
        meta = response.json()
        self.assertEqual(meta["observed_price_rows"], 13552)
        self.assertEqual(meta["price_unit"], "INR per quintal (100 kg)")
        self.assertTrue(any(c["crop"] == "Beans" and "Bengaluru" in c["districts"] for c in meta["crop_options"]))
        self.assertTrue(any(c["crop"] == "Spinach" and not c["available"] for c in meta["crop_options"]))

    def test_future_months_are_anchored_to_actual_source(self):
        origin = history().latest_global_date
        now = this_calendar_month()
        dates = [date.fromisoformat(x + "-01") for x in future_months()]
        self.assertTrue(all(now < month <= shift_month(origin, MAX_HORIZON) for month in dates))

    def test_prediction_matches_selection_and_has_twelve_horizons(self):
        months = future_months()
        self.assertTrue(months, "Refresh the source snapshot before running this test after September 2027")
        response = self.client.post("/api/predict", json={"crop": "Beans", "district": "Bengaluru", "month": months[0]})
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["selected"]["month"], months[0])
        self.assertEqual(len(result["outlook"]), 12)
        self.assertEqual({p["horizon"] for p in result["outlook"]}, set(range(1, 13)))
        self.assertGreater(result["selected"]["predicted_rs_per_quintal"], 0)
        self.assertEqual(result["origin_month"], "2026-09-01")
        self.assertIn("transport_note", result["explanation"])

    def test_rejects_absent_crop_and_bad_dates(self):
        month = future_months()[0]
        for payload in [
            {"crop": "Spinach", "district": "Bengaluru", "month": month},
            {"crop": "Beans", "district": "Bengaluru", "month": "2049-01"},
            {"crop": "Beans", "district": "Bengaluru", "month": "2026-15"},
        ]:
            with self.subTest(payload=payload):
                response = self.client.post("/api/predict", json=payload)
                self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
