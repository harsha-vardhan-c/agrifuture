import csv
import json
import math
import unittest
from datetime import date

from backend.forecasting import ROOT, PriceHistory, shift_month
from scripts.audit_source import audit


class DataIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history = PriceHistory()

    def test_dataset_has_original_expected_coverage(self):
        h = self.history
        self.assertEqual(len(h.rows), 13552)
        self.assertEqual(h.latest_global_date, date(2026, 9, 1))
        self.assertEqual(min(r[2] for r in h.rows), date(2021, 10, 1))
        self.assertEqual(len(h.series), 371)
        self.assertEqual(len({r[0] for r in h.rows}), 20)

    def test_cleaned_price_rows_are_positive_unique_months(self):
        h = self.history
        self.assertEqual(len(h.lookup), len(h.rows))
        self.assertTrue(all(d.day == 1 and math.isfinite(p) and p > 0 for _, _, d, p in h.rows))

    def test_reproducible_origin_targets(self):
        for origin in (date(2024, 9, 1), date(2025, 9, 1)):
            for horizon in range(1, 13):
                target = shift_month(origin, horizon)
                self.assertGreater(target, origin)
                self.assertEqual(target.day, 1)

    def test_captured_source_supports_every_cleaned_price(self):
        self.assertEqual(audit(), 13552)

    def test_report_contains_honest_metrics(self):
        report = json.loads((ROOT / "reports/backtest.json").read_text(encoding="utf-8"))
        self.assertEqual(report["test_selected_overall"]["samples"], 1808)
        self.assertEqual(report["latest_source_month"], "2026-09-01")
        self.assertEqual(set(report["test_selected_per_horizon"]), {str(h) for h in range(1, 13)})
        self.assertEqual(report["test_selected_per_horizon"]["12"]["method"], "hgb")


if __name__ == "__main__":
    unittest.main()
