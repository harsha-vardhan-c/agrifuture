"""FastAPI service and optional production frontend host for AgriFuture."""

from __future__ import annotations

import csv
from datetime import date
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.explanations import explain_forecast
from backend.forecasting import FEATURES, MAX_HORIZON, ROOT, PriceHistory, shift_month
from backend.weather import climate_context, live_weather


app = FastAPI(title="AgriFuture Karnataka API", version="1.0.0",
              description="Dated Karnataka district wholesale vegetable price outlooks.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type"],
)


class PredictionRequest(BaseModel):
    crop: str = Field(min_length=1, max_length=80)
    district: str = Field(min_length=1, max_length=80)
    month: str = Field(pattern=r"^\d{4}-\d{2}$")


@lru_cache(maxsize=1)
def history() -> PriceHistory:
    return PriceHistory()


@lru_cache(maxsize=1)
def artifact() -> dict:
    path = ROOT / "models/forecast_bundle.joblib"
    if not path.is_file():
        raise RuntimeError("Forecast model not found. Run: python -m backend.train")
    return joblib.load(path)


@lru_cache(maxsize=1)
def crop_coverage() -> list[dict]:
    with (ROOT / "data/crop_coverage.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def this_calendar_month() -> date:
    # Use Asia/Kolkata for user-facing dates.
    from datetime import datetime
    now = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    return now.replace(day=1)


def forecastable_pairs() -> set[tuple[str, str]]:
    h = history()
    eligible = {tuple(p) for p in artifact()["eligible_pairs"]}
    return {
        pair for pair in eligible
        if h.features(*pair, h.latest_global_date, 1) is not None
    }


def future_months() -> list[str]:
    observed_end = history().latest_global_date
    now_month = this_calendar_month()
    # Show only the next 12 complete calendar months, not the first 12 after stale data.
    first_target = shift_month(now_month, 1)
    last_target = shift_month(first_target, 11)
    supported_end = shift_month(observed_end, MAX_HORIZON)
    if last_target > supported_end:
        return []
    return [shift_month(first_target, i).strftime("%Y-%m") for i in range(12)]


@app.get("/health")
def health_check():
    return {"status": "ok", "model_trained_through": artifact()["trained_through"]}


@app.get("/api/metadata")
def metadata():
    h = history()
    available = forecastable_pairs()
    all_crops = sorted({r["crop"] for r in crop_coverage()})
    by_crop = {crop: sorted([district for c, district in available if c == crop]) for crop in all_crops}
    return {
        "app": "AgriFuture Karnataka",
        "observed_price_rows": len(h.rows),
        "latest_price_month": h.latest_global_date.isoformat(),
        "source": "AGMARKNET Government of India — historical district monthly wholesale prices",
        "price_unit": "INR per quintal (100 kg)",
        "target_type": "monthly district-level wholesale price, not daily or mandi-specific rate",
        "available_months": future_months(),
        "crop_options": [
            {"crop": crop, "districts": by_crop[crop], "available": bool(by_crop[crop]),
             "reason": None if by_crop[crop] else "Insufficient recent data or no official observations"}
            for crop in all_crops
        ],
    }


@app.post("/api/predict")
def predict(req: PredictionRequest):
    h = history()
    pair = (req.crop.strip(), req.district.strip())
    if pair not in forecastable_pairs():
        raise HTTPException(422, "This crop/district has insufficient recent verified price history.")
    try:
        chosen = date.fromisoformat(req.month + "-01")
    except ValueError:
        raise HTTPException(422, "Invalid month; expected YYYY-MM")
    allowed = future_months()
    if req.month not in allowed:
        raise HTTPException(422, "Choose a month in the next 12 calendar months. Update the model and market data if the forecast window is unavailable.")

    origin = h.latest_global_date
    features = [h.features(*pair, origin, horizon) for horizon in range(1, MAX_HORIZON + 1)]
    if any(x is None for x in features):
        raise HTTPException(422, "Required consecutive prior months are unavailable.")
    model_bundle = artifact()
    missing_horizons = [str(h) for h in range(1, MAX_HORIZON + 1)
                        if str(h) not in model_bundle["selected_methods"]]
    if missing_horizons:
        raise HTTPException(503, "Forecast model needs retraining. Run: python -m backend.train")
    predicted_ml = np.maximum(0, model_bundle["model"].predict(pd.DataFrame(features)[FEATURES]))
    outlook = []
    for i, feat in enumerate(features):
        h_num = i + 1
        target = shift_month(origin, h_num)
        method = model_bundle["selected_methods"].get(str(h_num), "last_price")
        if method == "hgb":
            predicted_price = float(predicted_ml[i])
        elif method == "seasonal_naive" and not np.isnan(feat["seasonal_reference_price"]):
            predicted_price = float(feat["seasonal_reference_price"])
        else:
            predicted_price = float(feat["origin_price"])
        ratio = model_bundle["val_error_p80_relative"].get(str(h_num), 0.35)
        outlook.append({
            "month": target.strftime("%Y-%m"),
            "horizon": h_num,
            "predicted_rs_per_quintal": round(predicted_price, 2),
            "predicted_rs_per_kg": round(predicted_price / 100, 2),
            "indicative_low_rs_per_quintal": round(max(0, predicted_price * (1 - ratio)), 2),
            "indicative_high_rs_per_quintal": round(predicted_price * (1 + ratio), 2),
            "method": method,
            "illustrative_error_band": True,
        })

    # Return the 12 months users can choose, while retaining the correct origin horizon.
    allowed_set = set(allowed)
    outlook = [row for row in outlook if row["month"] in allowed_set]
    selected = next(x for x in outlook if x["month"] == req.month)
    target_date = date.fromisoformat(req.month + "-01")
    explanation = explain_forecast(h, pair[0], pair[1], origin, target_date,
                                   selected["predicted_rs_per_quintal"],
                                   float(features[0]["origin_price"]))
    import json
    report = json.loads((ROOT / "reports/backtest.json").read_text(encoding="utf-8"))
    h_report = report["test_selected_per_horizon"].get(str(selected["horizon"]), {})
    return {
        "crop": pair[0], "district": pair[1], "selected": selected,
        "origin_month": origin.isoformat(),
        "last_observed_price_rs_per_quintal": float(features[0]["origin_price"]),
        "outlook": outlook,
        "history": h.historical_series(*pair),
        "explanation": explanation,
        "weather": climate_context(pair[1], target_date.month),
        "backtest_for_selected_horizon": h_report,
    }


@app.get("/api/weather/live")
async def weather_live(district: str):
    return await live_weather(district)


@app.get("/api/history/{crop}/{district}")
def crop_history(crop: str, district: str):
    return {"crop": crop, "district": district, "prices": history().historical_series(crop, district, limit=60)}


# React production build: install & build with npm inside frontend; FastAPI will
# then host it at the same origin as its API, avoiding CORS in deployment.
DIST = ROOT / "frontend/dist"


@app.get("/{page:path}", include_in_schema=False)
def frontend_route(page: str):
    if page.startswith("api/") or page == "docs" or page == "openapi.json":
        raise HTTPException(404)
    if DIST.is_dir():
        requested = (DIST / page).resolve()
        if requested.is_file() and requested.is_relative_to(DIST.resolve()):
            return FileResponse(requested)
        return FileResponse(DIST / "index.html")
    return {
        "message": "Backend is running. Start React frontend with: cd frontend; npm install; npm run dev",
        "api_documentation": "/docs",
    }
