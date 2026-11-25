"""Short, evidence-scoped farmer explanations. Never assert unobserved causes."""

from __future__ import annotations

from datetime import date
from statistics import median

from backend.forecasting import PriceHistory


# Approximate recurring calendar periods only. Exact festival dates move by year.
FESTIVAL_WINDOWS = {
    1: ("Makara Sankranti",),
    3: ("Ugadi (date varies)",),
    4: ("Ugadi (date varies)",),
    9: ("Dasara (date varies)",),
    10: ("Dasara / Deepavali (dates vary)",),
    11: ("Deepavali (date varies)",),
}


def explain_forecast(
    history: PriceHistory, crop: str, district: str, origin: date,
    target: date, price: float, last_price: float,
) -> dict:
    change_pct = 100 * (price - last_price) / last_price
    if change_pct > 5:
        direction = "rise"
        headline = "The forecast is above the last observed price."
    elif change_pct < -5:
        direction = "fall"
        headline = "The forecast is below the last observed price."
    else:
        direction = "stable"
        headline = "The forecast is close to the last observed price."

    reasons = [{
        "type": "model",
        "title": "Historical price patterns",
        "message": "This estimate reflects earlier district wholesale prices and annual seasonality. It cannot establish an exact cause.",
        "evidence": "forecast model and historical observations",
    }]
    pairs = history.series.get((crop, district), [])
    available = [v for d, v in pairs if d <= origin]
    same_month = [v for d, v in pairs if d <= origin and d.month == target.month]
    if len(same_month) >= 2 and available:
        typical = median(same_month)
        overall = median(available)
        gap = 100 * (typical - overall) / overall
        if gap > 10:
            message = f"In {len(same_month)} observed past seasons, prices for this calendar month were typically higher than the district's overall historical median."
        elif gap < -10:
            message = f"In {len(same_month)} observed past seasons, prices for this calendar month were typically lower than the district's overall historical median."
        else:
            message = "Historical prices in this calendar month were broadly similar to the district's overall median."
        reasons.append({"type": "season", "title": "Seasonal pattern", "message": message,
                        "evidence": f"{len(same_month)} historical observations available at forecast origin"})

    if target.month in FESTIVAL_WINDOWS:
        names = ", ".join(FESTIVAL_WINDOWS[target.month])
        reasons.append({
            "type": "festival", "title": "Festival calendar context",
            "message": f"Festival periods such as {names} may fall around this time. Their effects on this crop's demand or price have not been verified.",
            "evidence": "approximate seasonal calendar; exact year-specific date must be checked",
        })
    return {
        "direction": direction,
        "change_pct_vs_last_observed": round(change_pct, 1),
        "headline": headline,
        "reasons": reasons,
        "transport_note": "No verified transport disruptions or costs were used. We cannot attribute this price to transportation.",
        "weather_note": "Historical city weather is contextual only and is not a proven cause or a 12-month weather forecast.",
    }
