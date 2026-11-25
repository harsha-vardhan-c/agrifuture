import math
import unittest
from datetime import date

from backend.forecasting import PriceHistory, shift_month
from backend.weather import climate_context


class ForecastingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history = PriceHistory()

    def test_features_do_not_depend_on_future_prices(self):
        h = self.history
        origin = date(2025, 9, 1)
        pair = ("Beans", "Bengaluru")
        before = h.features(*pair, origin, 6)
        self.assertIsNotNone(before)
        # Prove we can change future values without changing any input feature.
        relevant_future_keys = [key for key in h.lookup if key[0:2] == pair and key[2] > origin]
        original = {key: h.lookup[key] for key in relevant_future_keys}
        try:
            for key in relevant_future_keys:
                h.lookup[key] = 999999.99
            after = h.features(*pair, origin, 6)
        finally:
            h.lookup.update(original)
        for field, value in before.items():
            if isinstance(value, float) and math.isnan(value):
                self.assertTrue(math.isnan(after[field]), field)
            else:
                self.assertEqual(value, after[field], field)

    def test_horizon_not_above_twelve(self):
        h = self.history
        self.assertIsNone(h.features("Beans", "Bengaluru", date(2025, 9, 1), 0))
        self.assertIsNone(h.features("Beans", "Bengaluru", date(2025, 9, 1), 13))
        self.assertEqual(shift_month(date(2026, 9, 1), 12), date(2027, 9, 1))

    def test_city_weather_is_only_contextual(self):
        weather = climate_context("Bengaluru", 9)
        self.assertTrue(weather["available"])
        self.assertIn("Not a future weather forecast", weather["note"])
        self.assertFalse(climate_context("Not a District", 9)["available"])


if __name__ == "__main__":
    unittest.main()
