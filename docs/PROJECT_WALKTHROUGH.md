# AgriForecast — simple complete project explanation

Read this before explaining the project to a recruiter or changing the code.

## 1. What is the problem?

Imagine a farmer in Mysuru growing tomatoes. They can see today's prices at a nearby market, but they may want an **early rough idea** about wholesale tomato prices several months later. Future prices are uncertain and change with growing conditions, market arrivals and demand. Our project makes **dated, district-level price estimates from past genuine wholesale reports**, and clearly labels them as estimates.

The project is called **AgriForecast Karnataka**. It focuses on one state first so crop/district definitions and source coverage remain manageable.

## 2. Exactly what does a visitor do?

1. Open the welcome page, read a simple explanation and click **Explore price outlooks**.
2. Pick a **vegetable**, for example Tomato.
3. Pick a **district**, for example Mysuru. Only district/crop combinations with enough usable source data can be picked.
4. Pick an available **future month**, for example January 2027.
5. Click **View price outlook**.
6. See an **estimated monthly district wholesale price**, an easy ₹/kg conversion, a historical/forecast chart, an indicative range, short seasonality and festival *context* when relevant, a historical backtest error and weather *context* if the location can be mapped.
7. Return to the selection form and try a different crop/month.

**Very important:** A farmer is not seeing the exact price a trader will pay on that day. The data is **district-month wholesale** history measured in **₹ per 100 kg**. The `/kg` value is simply the `/quintal` number divided by 100 and does not mean retail-store prices.

## 3. What are the data rows?

Each row in the main CSV contains:

`date = 2026-09-01`, `crop = Beans`, `district = Bengaluru`, `wholesale_price_rs_per_quintal = [recorded value]`.

Think of one row as: **“For this vegetable, in this district, during this month, the reported district wholesale rate was X rupees per quintal.”**

The captured official reports were cleaned and assembled into 13,552 distinct observations for October 2021–September 2026. They represent 20 vegetables with at least some observations and hundreds of district–vegetable histories. Missing observations remain missing. We did not manufacture prices for Pumpkin, Spinach or recent Okra months.

## 4. What is an ML model doing here?

The model looks for relationships between past prices, seasonality, vegetable identity, district and how far into the future we want to estimate. This is **supervised regression**:

**Input:** `{crop: Tomato, district: Mysuru, last known month: September 2026, horizon: 4 months, recent prices, historical seasonal reference, ...}`

**Predicted output:** a single estimated ₹/quintal value for **January 2027**.

This is **not classification** (a yes/no prediction), recommendation, image analysis, or a chatbot. It is *time-series forecasting represented as tabular regression*.

## 5. Why is “12 months” a hard limit?

The model was trained and checked at 1, 2, ..., **12 months ahead**. It is **not** trained for month 13 or infinity. Its forecasts all originate at the **last actual observed price month**, September 2026, so the maximum target is September 2027. As of 24 November 2026, October and November are past calendar months, not selectable future targets; the app offers December 2026–September 2027. This window shrinks unless new official data is collected and the model retrained.

The model does **not** fake the October/November observations just to keep the forecasts looking live.

## 6. Why compare several methods?

A machine-learning model should beat a reasonable simple rule before we trust that it adds value. We tried:

- **Gradient boosting (ML):** learns patterns across crops, districts, seasonal months, recent price changes and price lags.
- **Last-price rule:** future price equals the most recently known actual monthly price.
- **Previous-year-month rule:** future price equals the actual price reported in the same calendar month one year earlier, when available.

We trained a model on past periods, tested the three methods on a **validation forecast from September 2024**, chose the lowest-MAE method for each horizon, and then evaluated those fixed choices on an unseen **forecast from September 2025**. We finally refit ML with everything known through September 2026 for the deployed forecasts.

**Why do simpler methods sometimes win?** Vegetables have noisy prices, missing district reports and relatively short history. Bigger models can overfit. A baseline is sometimes the less-wrong choice, and saying so in an interview is a strength.

## 7. Explain leakage in easy words

Suppose you are standing in **September 2025** trying to predict February 2026. You cannot use actual November or December 2025 prices in your input, because those prices **have not happened yet**. That would be cheating or *data leakage*.

Our input features are deliberately calculated using prices dated **September 2025 or before**. And the training process for that backtest uses labels dated no later than September 2025. The actual February 2026 price is used only afterwards to check the prediction error.

The 12-month path uses one fixed origin, instead of pretending intermediate predicted months became real observations.

## 8. What is the real error?

The final method-mix had **26.19% weighted absolute percentage error (WAPE)** across 1,808 held-out forecast comparisons from a September 2025 origin. For 12-month-ahead predictions specifically, gradient boosting was the validation-selected method: **22.67% WAPE on 151 test comparisons**, but **33.72% WAPE in the earlier validation snapshot**. That difference matters — the real future might be different again.

You **cannot** correctly say “the model has 85% accuracy” on this evidence. You also cannot claim the model gets “22.67% error” for every crop or district — there is variation. For exact model numbers read `docs/MODEL_CARD.md`.

## 9. What do the explanatory notes mean?

We wanted farmer-friendly messages, but truthful ones:

- **Direction:** The predicted price is above, below or close to the **last actual observed district price**. It doesn't say the market will certainly go up or down next week.
- **Seasonality:** We compare historical prices for the forecast calendar month with the overall median, using **only observed past seasons**. The note explains a pattern, not a proven causal relationship.
- **Festivals:** If a festival period is approximately nearby, the app names it as **calendar context**. Ugadi, Deepavali and Dasara dates vary year-to-year, and the app **does not claim they caused a price rise**.
- **Transportation:** No real transport/road disruption data was collected. The app explicitly refuses to invent a “transport costs caused this spike” reason.

Better explanations would require integrating observed arrivals, weather forecasts, festival-date calendars, and local supply-chain signals — **with independent backtests proving their value**.

## 10. How does weather work?

**Historical:** A separate file of 480 climate-reanalysis city-month rows covers eight city coordinates and five years. When the chosen district matches a supported city, the result displays its average historical monthly temperature and rainfall. This is *context*, not a forecast for January 2027.

**Live:** The backend can contact Open-Meteo to show **current temperature and total forecast rain for the next three days** for those city coordinates. If the internet is down or the district cannot be mapped, the site says that weather isn't available; the crop-price prediction still works.

**Honesty:** No weather values are currently inputs to the 12-month price regression. Historical weather cannot be substituted for a genuine 12-month weather prediction. We intentionally avoided inventing distant-month forecasts.

## 11. How all the code connects

| File | Role |
|---|---|
| `data/karnataka_prices.csv` | Source-derived official monthly prices |
| `data/raw/…json.gz` | Original captured report archive for audit |
| `backend/forecasting.py` | Feature engineering, ML model and error calculations |
| `backend/train.py` | Time-safe validation/test and final model training |
| `models/forecast_bundle.joblib` | The saved trained model and chosen baselines |
| `backend/app.py` | Accepts user choices, calculates prices, exposes HTTP endpoints |
| `backend/explanations.py` | Careful seasonal/context messages |
| `backend/weather.py` | Historical and optional short-term weather context |
| `frontend/src/App.jsx` | Homepage, selection form, results and chart |
| `frontend/src/styles.css` | Mobile-friendly design |
| `frontend/dist/` | Ready-to-use compiled website (no Node needed to run) |
| `reports/backtest.json` | Full validation/held-out test numbers |
| `tests/` | Repeatable correctness checks |

## 12. What can I say in a resume?

**Honest suggested bullet:**

> Built an end-to-end Karnataka vegetable wholesale-price forecasting application with React and FastAPI, using 13,552 source-derived district-month observations; evaluated gradient boosting against temporal baselines through leakage-aware 12-month holdouts (26.19% pooled held-out WAPE across 1,808 comparisons) and delivered data-backed trend explanations.

Do **not** write: “85% accuracy, real-time 12-month weather forecasts, AI-driven festival and logistics predictions, prices guaranteed for farmers.” None of those are supported by the current implementation.

## 13. Questions a recruiter might ask

**Q: Why a state-level pilot?** Consistent crop/district cleaning, auditable scope and simpler local context, before scaling to multiple states with different data quality.

**Q: What does `quintal` mean?** A weight unit equal to 100 kilograms. Government wholesale price quotes are commonly per quintal.

**Q: Is it live?** The **website responds instantly** to a request, and short-range weather can update live. The **price dataset is a historical snapshot**; that is different from live market ingestion. We are transparent about the last observed month.

**Q: Why not LSTM/deep learning?** With only about five years of monthly histories, uneven crop coverage and one-state data, a simpler gradient-boosted model with strong naive baselines is easier to audit. More model complexity does not guarantee less forecasting error.

**Q: Which feature matters most?** We have engineered several informative lag and seasonality features, but have **not run a validated feature-attribution study**. Claiming a precise feature-importance ranking would be unsupported.

**Q: Why one model across districts and crops?** It shares statistical patterns between shorter series while encoding crop/district identity. That comes with a tradeoff: common patterns may not capture district-specific shocks.

**Q: What next?** Ingest new AGMARKNET months on a schedule; version source snapshots; add rolling-origin backtests across more historical windows; test market-arrival volume and explicitly historical weather as predictors with an ablation study; calibrate uncertainty intervals; provide a farmer-facing Kannada language option and per-mandi actual quotes when legally and technically available.
