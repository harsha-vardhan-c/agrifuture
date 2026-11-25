# Model card: Karnataka district vegetable price outlooks

## Task definition

Given a **crop, district, known origin month and forecast horizon (1–12 months)**, estimate the **monthly average district wholesale price**, measured in **INR per quintal**. This is a *regression problem*. It is not classification, and the output is not a probability of prices increasing.

## Data and training

- Dataset: `data/karnataka_prices.csv`, **13,552 unique verified-source rows** across **October 2021–September 2026**.
- Predictor columns: crop, district, horizon, origin-year, cyclic origin/target month, current price, earlier price lags, recent mean/volatility/change, lag-12 price, historical same-month price median and previous-year target-month reference. **Missing histories are represented explicitly.** All predictors are taken from the known origin or earlier.
- ML algorithm: scikit-learn `HistGradientBoostingRegressor` with categorical one-hot encodings and non-linear numerical features. This handles non-linear interactions and missing numerical histories.
- Controls: *persistence* (last observed monthly price) and *seasonal naive* (price in the same target calendar month one year earlier, if available; else persistence).
- Strategy: **direct horizon forecasting**, one row per origin/horizon with target in month `origin + horizon`. No recursively substituting invented price observations into later horizons.
- Selection: smallest **validation MAE** for each horizon across ML and both controls; no test-set winner shopping.

## Time-safe validation

| Phase | Prices available to the model | Target months | Role |
|---|---|---|---|
| Validation | Through 2024-09 | 2024-10 to 2025-09 | Select method per horizon |
| Test | Through 2025-09 | 2025-10 to 2026-09 | Held-out honest report |
| Shipped model | Through 2026-09 | 2026-10 to 2027-09 | Prospective experimental outlook |

For each historical origin, the model is **fitted only on labels available at or before that origin**. The origin-based features contain no post-origin actual prices. The final saved model is trained separately on all observed source months after evaluation.

## Held-out results

| Horizon | Validation-selected method | Test comparisons | Test MAE, ₹/quintal | Test WAPE | Validation WAPE |
|---|---|---:|---:|---:|---:|
| 1 | Gradient boosting | 157 | 514.66 | 22.74% | 23.22% |
| 2 | Last observed price | 155 | 635.56 | 25.01% | 24.50% |
| 3 | Last observed price | 139 | 562.10 | 23.01% | 21.80% |
| 4 | Gradient boosting | 150 | 415.50 | 19.63% | 22.92% |
| 5 | Prior-year month | 151 | 576.61 | 28.38% | 29.50% |
| 6 | Prior-year month | 151 | 485.30 | 25.94% | 27.47% |
| 7 | Last observed price | 151 | 577.23 | 27.67% | 37.07% |
| 8 | Last observed price | 151 | 771.51 | 31.96% | 36.25% |
| 9 | Last observed price | 151 | 758.95 | 30.09% | 30.23% |
| 10 | Last observed price | 150 | 666.59 | 27.72% | 31.22% |
| 11 | Prior-year month | 151 | 683.87 | 28.64% | 31.34% |
| 12 | Gradient boosting | 151 | 535.07 | 22.67% | 33.72% |
| **All selected** | **Mix of methods** | **1,808** | **598.69** | **26.19%** | — |

See exact, machine-readable numbers in `reports/backtest.json`. Crop-specific errors: `reports/crop_test_errors.csv`.

### How to read these metrics

- **MAE** = average absolute difference between predicted and actual price, in ₹/quintal. Lower is better.
- **WAPE** = `100 × sum(abs(predicted − actual)) / sum(actual)` on all eligible examples. Lower is better. **Do not call `(100 − WAPE)%` forecast accuracy**; WAPE is sensitive to the mix of crop-price scales and is not a guarantee for an individual district.
- **Illustrative result band** = selected method's 80th percentile absolute *relative* error in the validation snapshot, scaled around the predicted price. It is a historical guide, **not an interval with verified 80% future coverage**.

## Honest limitations

1. Only **one fixed validation origin and one fixed test origin**. More rolling-origin test windows are necessary for reliability, uncertainty calibration and statistical significance.
2. Historical prices cannot account for supply shocks, farmgate vs wholesale margins, government intervention, crop grade, specific mandis or real-time delivery costs.
3. There is no meaningful defensible **85% accuracy claim**, and using deep learning would not magically produce one.
4. Sparse series are filtered. A series eligible for the historical training regime may lack the last three consecutive observed months in September 2026, in which case the API refuses a forecast.
5. Weather and festival information is a **separate descriptive layer**: it is *not* a validated predictor or a proven reason for price movement.
6. No retraining happens automatically when the live calendar advances. Source data must be updated, checked, and the model retrained.

## Appropriate and inappropriate use

**Appropriate:** portfolio demonstration, historical wholesale-price exploration, illustrating uncertainty-aware ML versus baselines, teaching farmers the difference between district wholesale estimates and live mandi prices.

**Inappropriate:** guaranteed farmer revenue planning, promises of festival-price spikes, determining exact future sale/retail rates, using results as formal financial advice, presenting model test errors as field-validated accuracy.

## Reproducibility

Run `python -m backend.train` from the project root. The deterministic scikit-learn model uses random state 42. Training generates all evaluation reports and final artifact. The raw source snapshot is preserved in `data/raw/` and the engineered samples in `data/horizon_training_features.csv`.
