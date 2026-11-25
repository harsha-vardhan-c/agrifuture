"""Verify the cleaned prices against preserved original AGMARKNET responses.

Usage from project root:
    python -m scripts.audit_source

This script reads the original captured JSON reports and the per-row source
dates, then checks that each final price is exactly traceable to the indicated
official district report response. It never changes project data.
"""

from __future__ import annotations

import csv
import gzip
import json
from datetime import date

from backend.forecasting import ROOT


def audit() -> int:
    with gzip.open(ROOT / "data/raw/agmarknet_official_api_reports.json.gz", "rt", encoding="utf-8") as stream:
        capture = json.load(stream)
    by_report = {}
    for r in capture["reports"]:
        date_key = date(int(r["year"]), int(r["month"]), 1)
        for district in r["data"].get("rows", []):
            key = (r["crop"], district["district"], date_key)
            if key in by_report:
                raise ValueError(f"Duplicate source report/district: {key}")
            by_report[key] = district

    with (ROOT / "data/raw/price_source_report_dates.csv").open(newline="", encoding="utf-8") as file:
        origins = {
            (r["crop"], r["district"], r["date"]): date.fromisoformat(r["report_date"])
            for r in csv.DictReader(file)
        }

    checked = 0
    with (ROOT / "data/karnataka_prices.csv").open(newline="", encoding="utf-8") as file:
        for r in csv.DictReader(file):
            key = (r["crop"], r["district"], r["date"])
            if key not in origins:
                raise ValueError(f"Price lacks source-date mapping: {key}")
            report = origins[key]
            source_row = by_report.get((r["crop"], r["district"], report))
            if source_row is None:
                raise ValueError(f"Price lacks original report row: {key}, report={report}")
            period = date.fromisoformat(r["date"])
            field = "prices_" + period.strftime("%B_%Y").lower()
            observed = source_row.get(field)
            if observed is None or abs(float(observed) - float(r["wholesale_price_rs_per_quintal"])) > 0.011:
                raise ValueError(f"Price does not match original report: {key}, value={observed}")
            checked += 1
    if checked != len(origins):
        raise ValueError(f"Count mismatch: {checked} prices, {len(origins)} provenance mappings")
    print(f"PASS: {checked:,} cleaned prices match their original AGMARKNET response and source report date")
    print(f"Captured official monthly reports: {capture['report_count']:,}; capture date: {capture['collected_at']}")
    return checked


if __name__ == "__main__":
    audit()
