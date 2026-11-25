"""Train and backtest genuine 1–14-month-ahead forecasts.

Run: python -m backend.train

Forecast origins:
* July 2024 -> Aug 2024–Sep 2025 validation (train through Sep 2024)
* July 2025 -> Aug 2025–Sep 2026 held-out test (train through Sep 2025)

Each 14-month path uses one fixed origin. No actual prices after the origin
are used as features or in the model available at that origin.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from backend.forecasting import (
    FEATURES, MAX_HORIZON, ROOT, TEST_CUTOFF, TRAIN_CUTOFF,
    PriceHistory, chosen_methods, evaluate_by_horizon, indicative_errors,
    make_model, predictions_for, score,
)


def run_training() -> dict:
    prices = PriceHistory()
    pairs = prices.eligible_series(TRAIN_CUTOFF)
    if not pairs:
        raise RuntimeError("No eligible price series found")

    train = prices.supervised_samples(TRAIN_CUTOFF, pairs)
    validation = prices.forecast_origin(TRAIN_CUTOFF, pairs)
    if train.empty or validation.empty:
        raise RuntimeError("Insufficient data for origin-based validation")
    model_val = make_model()
    model_val.fit(train[FEATURES], train["target"])
    validation_preds = predictions_for(model_val, validation)
    validation_metrics = evaluate_by_horizon(validation, validation_preds)
    selected = chosen_methods(validation_metrics)
    val_errors = indicative_errors(validation, validation_preds, selected)

    # Chronologically refit with real information available as of Jul 2025.
    train_test = prices.supervised_samples(TEST_CUTOFF, pairs)
    test = prices.forecast_origin(TEST_CUTOFF, pairs)
    model_test = make_model()
    model_test.fit(train_test[FEATURES], train_test["target"])
    test_preds = predictions_for(model_test, test)
    test_metrics = evaluate_by_horizon(test, test_preds)

    # The per-horizon winner was selected ONLY from validation.
    chosen_test_results = {}
    selected_y = []
    selected_predictions = []
    chosen_test_rows = []
    for h, method in selected.items():
        mask = test["horizon"].to_numpy() == int(h)
        if not mask.any():
            continue
        actuals = test.loc[mask, "target"].to_numpy()
        preds = test_preds[method][mask]
        chosen_test_results[h] = {"method": method, **score(actuals, preds)}
        selected_y.extend(actuals)
        selected_predictions.extend(preds)
        test_subset = test.loc[mask, ["crop", "district", "target_date", "horizon", "target"]]
        for r, pred in zip(test_subset.to_dict("records"), preds):
            chosen_test_rows.append({**r, "prediction": float(pred), "method": method})

    overall = score(np.array(selected_y), np.array(selected_predictions))
    per_crop = []
    if chosen_test_rows:
        for crop, group in pd.DataFrame(chosen_test_rows).groupby("crop", sort=True):
            per_crop.append({"crop": crop, **score(group["target"].to_numpy(), group["prediction"].to_numpy())})

    # This final fit includes all known prices, for prospective future forecasts.
    # Backtest metrics above are from independently refitted earlier snapshots.
    final_training = prices.supervised_samples(prices.latest_global_date, pairs)
    model_future = make_model()
    model_future.fit(final_training[FEATURES], final_training["target"])

    model_dir = ROOT / "models"
    report_dir = ROOT / "reports"
    model_dir.mkdir(exist_ok=True)
    report_dir.mkdir(exist_ok=True)
    artifact = {
        "model": model_future,
        "features": FEATURES,
        "selected_methods": selected,
        "val_error_p80_relative": val_errors,
        "trained_through": prices.latest_global_date.isoformat(),
        "eligible_pairs": sorted([list(x) for x in pairs]),
        "message": "Forecasts use 14 lead months to show the next 12 calendar months.",
    }
    joblib.dump(artifact, model_dir / "forecast_bundle.joblib", compress=3)

    report = {
        "data_price_rows": len(prices.rows),
        "observed_months": 60,
        "eligible_crop_district_series": len(pairs),
        "train_supervised_rows": len(train),
        "test_fit_supervised_rows": len(train_test),
        "final_fit_supervised_rows": len(final_training),
        "validation_origin": TRAIN_CUTOFF.isoformat(),
        "test_origin": TEST_CUTOFF.isoformat(),
        "latest_source_month": prices.latest_global_date.isoformat(),
        "selection_rule": "Best validation MAE per horizon (HGB, same-month-previous-year, persistence). Test never selects a method.",
        "selected_per_horizon": selected,
        "validation": validation_metrics,
        "test": test_metrics,
        "test_selected_per_horizon": chosen_test_results,
        "test_selected_overall": overall,
        "val_relative_abs_error_p80": val_errors,
        "limitations": [
            "One validation origin and one test origin: not enough for strong long-range statistical confidence.",
            "An 80th percentile historical relative error is indicative, not an 80% calibrated prediction interval.",
            "Historical monthly district wholesale prices do not predict a daily mandi or retail rate.",
            "Weather and festivals are contextual and have not been validated as price-model inputs.",
            "No 85% accuracy claim; evaluate WAPE/MAE per horizon and crop.",
        ],
    }
    (report_dir / "backtest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(per_crop).to_csv(report_dir / "crop_test_errors.csv", index=False)
    final_training.to_csv(ROOT / "data" / "horizon_training_features.csv", index=False)
    return report


if __name__ == "__main__":
    summary = run_training()
    print("Backtest: chosen method per horizon, held-out test")
    for h, result in summary["test_selected_per_horizon"].items():
        print(f"H{int(h):02d} {result['method']:>15} n={result['samples']:>3} MAE=₹{result['mae_rs_per_quintal']:>8.2f} WAPE={result['wape_pct']:>6.2f}%")
    print("Overall selected test: ", summary["test_selected_overall"])
