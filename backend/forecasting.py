"""Leakage-aware, origin-based monthly price forecasting helpers.

An origin is the *last observed price month*. Every input feature is evaluated
at or before that origin. Forecast targets are up to 14 months afterwards.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from statistics import median, pstdev

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


ROOT = Path(__file__).resolve().parents[1]
PRICE_FILE = ROOT / "data/karnataka_prices.csv"
CAT_FEATURES = ["crop", "district"]
NUM_FEATURES = [
    "horizon", "origin_year", "origin_month_sin", "origin_month_cos",
    "target_month_sin", "target_month_cos", "origin_price", "lag_1_price",
    "lag_2_price", "lag_3_price", "lag_12_price", "lag_12_missing",
    "recent_mean_3", "recent_std_3", "last_change_pct",
    "seasonal_reference_price", "seasonal_reference_missing",
    "seasonal_past_month_median", "seasonal_past_month_missing",
]
FEATURES = CAT_FEATURES + NUM_FEATURES
TRAIN_CUTOFF = date(2024, 7, 1)
TEST_CUTOFF = date(2025, 7, 1)
MAX_HORIZON = 14
MIN_TRAIN_HISTORY_MONTHS = 18


def shift_month(d: date, offset: int) -> date:
    """Offset calendar month, preserving monthly-period-start convention."""
    index = d.year * 12 + d.month - 1 + offset
    return date(index // 12, index % 12 + 1, 1)


class PriceHistory:
    def __init__(self, csv_path: Path = PRICE_FILE):
        self.rows = []
        self.lookup = {}
        self.series = defaultdict(list)
        df = pd.read_csv(csv_path)
        required = {"date", "crop", "district", "wholesale_price_rs_per_quintal"}
        if not required.issubset(df.columns):
            raise ValueError("Price data columns are missing")
        for r in df.itertuples(index=False):
            d = date.fromisoformat(r.date)
            price = float(r.wholesale_price_rs_per_quintal)
            key = (str(r.crop), str(r.district), d)
            if key in self.lookup or d.day != 1 or not math.isfinite(price) or price <= 0:
                raise ValueError(f"Invalid or duplicate price record: {key}")
            self.lookup[key] = price
            item = (d, price)
            self.series[(key[0], key[1])].append(item)
            self.rows.append((key[0], key[1], d, price))
        for values in self.series.values():
            values.sort()
        self.latest_global_date = max(r[2] for r in self.rows)

    def eligible_series(self, cutoff: date = TRAIN_CUTOFF) -> set[tuple[str, str]]:
        return {
            pair for pair, series in self.series.items()
            if sum(d <= cutoff for d, _ in series) >= MIN_TRAIN_HISTORY_MONTHS
        }

    def value(self, crop: str, district: str, when: date) -> float | None:
        return self.lookup.get((crop, district, when))

    def features(self, crop: str, district: str, origin: date, horizon: int) -> dict | None:
        if not 1 <= horizon <= MAX_HORIZON:
            return None
        pair = (crop, district)
        if pair not in self.series:
            return None
        look = {i: self.value(crop, district, shift_month(origin, -i)) for i in (0, 1, 2, 3, 12)}
        if any(look[i] is None for i in (0, 1, 2)):
            return None
        target = shift_month(origin, horizon)
        # Never use a value later than the forecast origin (prevents leakage at h > 12).
        seasonal_date = shift_month(target, -12)
        year_ago = self.value(crop, district, seasonal_date) if seasonal_date <= origin else None
        past_same_month = [v for d, v in self.series[pair] if d <= origin and d.month == target.month]
        recent = [look[0], look[1], look[2]]
        def cyc(month: int):
            angle = 2 * math.pi * (month - 1) / 12
            return math.sin(angle), math.cos(angle)
        osin, ocos = cyc(origin.month)
        tsin, tcos = cyc(target.month)
        return {
            "crop": crop, "district": district,
            "horizon": horizon, "origin_year": origin.year,
            "origin_month_sin": osin, "origin_month_cos": ocos,
            "target_month_sin": tsin, "target_month_cos": tcos,
            "origin_price": look[0], "lag_1_price": look[1], "lag_2_price": look[2],
            "lag_3_price": np.nan if look[3] is None else look[3],
            "lag_12_price": np.nan if look[12] is None else look[12],
            "lag_12_missing": int(look[12] is None),
            "recent_mean_3": sum(recent) / 3,
            "recent_std_3": pstdev(recent),
            "last_change_pct": 100 * (look[0] - look[1]) / look[1],
            "seasonal_reference_price": np.nan if year_ago is None else year_ago,
            "seasonal_reference_missing": int(year_ago is None),
            "seasonal_past_month_median": np.nan if not past_same_month else median(past_same_month),
            "seasonal_past_month_missing": int(not past_same_month),
        }

    def supervised_samples(self, cutoff: date, pairs: set[tuple[str, str]]) -> pd.DataFrame:
        examples = []
        for crop, district in sorted(pairs):
            for origin, _ in self.series.get((crop, district), []):
                if origin > cutoff:
                    break
                for h in range(1, MAX_HORIZON + 1):
                    target = shift_month(origin, h)
                    if target > cutoff:
                        break
                    actual = self.value(crop, district, target)
                    if actual is None:
                        continue
                    f = self.features(crop, district, origin, h)
                    if f is not None:
                        f.update({"origin_date": origin.isoformat(), "target_date": target.isoformat(), "target": actual})
                        examples.append(f)
        return pd.DataFrame(examples)

    def forecast_origin(self, origin: date, pairs: set[tuple[str, str]]) -> pd.DataFrame:
        examples = []
        for crop, district in sorted(pairs):
            for h in range(1, MAX_HORIZON + 1):
                f = self.features(crop, district, origin, h)
                if f is None:
                    continue
                target = shift_month(origin, h)
                actual = self.value(crop, district, target)
                if actual is not None:
                    f.update({"origin_date": origin.isoformat(), "target_date": target.isoformat(), "target": actual})
                    examples.append(f)
        return pd.DataFrame(examples)

    def historical_series(self, crop: str, district: str, limit: int = 36) -> list[dict]:
        return [{"date": d.isoformat(), "price": p} for d, p in self.series.get((crop, district), [])[-limit:]]


def make_model() -> Pipeline:
    transformer = ColumnTransformer([
        ("crop_and_district", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT_FEATURES),
        ("numeric", "passthrough", NUM_FEATURES),
    ], sparse_threshold=0)
    model = HistGradientBoostingRegressor(
        max_iter=180, max_leaf_nodes=27, min_samples_leaf=40,
        learning_rate=0.065, l2_regularization=10,
        random_state=42,
    )
    return Pipeline([("features", transformer), ("model", model)])


def predictions_for(model: Pipeline, samples: pd.DataFrame) -> dict[str, np.ndarray]:
    ml = np.maximum(0, model.predict(samples[FEATURES]))
    seasonal = samples["seasonal_reference_price"].fillna(samples["origin_price"]).to_numpy()
    return {
        "hgb": ml,
        "seasonal_naive": seasonal,
        "last_price": samples["origin_price"].to_numpy(),
    }


def score(y: np.ndarray, pred: np.ndarray) -> dict:
    y = np.asarray(y, dtype=float)
    pred = np.asarray(pred, dtype=float)
    errors = np.abs(pred - y)
    return {
        "samples": int(len(y)),
        "mae_rs_per_quintal": round(float(errors.mean()), 2),
        "wape_pct": round(float(100 * errors.sum() / y.sum()), 2),
    }


def evaluate_by_horizon(samples: pd.DataFrame, predictions: dict[str, np.ndarray]) -> dict:
    result = {}
    for h in range(1, MAX_HORIZON + 1):
        mask = samples["horizon"].to_numpy() == h
        if not mask.any():
            continue
        result[str(h)] = {
            name: score(samples.loc[mask, "target"].to_numpy(), vals[mask])
            for name, vals in predictions.items()
        }
    return result


def chosen_methods(validation_scores: dict) -> dict[str, str]:
    return {
        horizon: min(results, key=lambda method: results[method]["mae_rs_per_quintal"])
        for horizon, results in validation_scores.items()
    }


def indicative_errors(samples: pd.DataFrame, preds: dict[str, np.ndarray], selected: dict) -> dict:
    out = {}
    for h, method in selected.items():
        mask = samples["horizon"].to_numpy() == int(h)
        y = samples.loc[mask, "target"].to_numpy()
        p = preds[method][mask]
        # A historical descriptive percentile, NOT a 80% calibrated interval.
        absolute_pct_errors = np.abs((p - y) / y)
        out[h] = round(float(np.quantile(absolute_pct_errors, 0.8)), 4)
    return out
