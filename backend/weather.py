"""Historical climate context plus optional, genuine short-range live weather.

Weather is never silently merged into 12-month crop price predictions.
"""

from __future__ import annotations

from functools import lru_cache

import httpx
import pandas as pd

from backend.forecasting import ROOT


COORDS = {
    "Bengaluru": (12.9716, 77.5946),
    "Mysuru": (12.2958, 76.6394),
    "Hubballi": (15.3647, 75.1240),
    "Belagavi": (15.8497, 74.4977),
    "Kalaburagi": (17.3297, 76.8343),
    "Shivamogga": (13.9299, 75.5681),
    "Davanagere": (14.4644, 75.9218),
    "Tumakuru": (13.3392, 77.1006),
}

# AGMARKNET can use a different transliteration for the same city.
DISTRICT_TO_WEATHER_CITY = {**{city: city for city in COORDS}, "Davangere": "Davanagere"}


@lru_cache(maxsize=1)
def historical_weather() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data/karnataka_weather_8_cities_2021_2026.csv")


def climate_context(district: str, month: int) -> dict:
    city = DISTRICT_TO_WEATHER_CITY.get(district)
    if not city:
        return {
            "available": False,
            "note": "No validated city-level weather match for this district. Weather was not added to the price model.",
        }
    df = historical_weather()
    subset = df[(df["city"] == city) & (df["date"].str.slice(5, 7).astype(int) == month)]
    if subset.empty:
        return {"available": False, "note": "No historical weather observations for this month."}
    return {
        "available": True, "city_proxy": city,
        "years_observed": int(len(subset)),
        "historical_mean_temperature_c": round(float(subset["mean_temperature_c"].mean()), 1),
        "historical_mean_monthly_rainfall_mm": round(float(subset["rainfall_mm"].mean()), 1),
        "note": "Historical reanalysis at a city coordinate. Not a future weather forecast or a price-model input.",
    }


async def live_weather(district: str) -> dict:
    city = DISTRICT_TO_WEATHER_CITY.get(district)
    if not city:
        return {"available": False, "note": "Live weather is available only for supported city coordinates."}
    lat, lon = COORDS[city]
    params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,precipitation",
        "daily": "precipitation_sum",
        "forecast_days": 3, "timezone": "Asia/Kolkata",
    }
    try:
        async with httpx.AsyncClient(timeout=7) as client:
            response = await client.get("https://api.open-meteo.com/v1/forecast", params=params)
            response.raise_for_status()
            payload = response.json()
        return {
            "available": True, "city_proxy": city,
            "updated_at": payload["current"]["time"],
            "temperature_c": payload["current"]["temperature_2m"],
            "precipitation_mm": payload["current"]["precipitation"],
            "next_3_days_rainfall_mm": round(sum(v or 0 for v in payload["daily"]["precipitation_sum"]), 1),
            "source": "Open-Meteo short-range forecast API",
            "note": "Current and next-three-day weather only. Not used as a 12-month price forecast input.",
        }
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        return {"available": False, "note": "Live weather could not be loaded. Historical prices and prediction remain available."}
