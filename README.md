# AgriForecast Karnataka

**A farmer-friendly, evidence-based outlook for district-level vegetable wholesale prices.**

Select a vegetable, Karnataka district and future month. The application returns an estimated **monthly district wholesale price in ₹ per quintal (100 kg)**, a chart, a historical-error guide, and short explanations that distinguish observed facts from possible influences. It does **not** claim to know the exact price in a specific mandi on a particular day.

![Architecture](docs/architecture.svg)

## What is included?

- Responsive React/Vite landing page, simple forecast form and results dashboard.
- FastAPI service, validated inputs and data-dependent crop/district/month dropdowns.
- Government AGMARKNET-derived, cleaned district-month wholesale price dataset: **13,552 rows**, **October 2021–September 2026**. Original captured reports are preserved as a compressed archive in `data/raw/` for audit.
- **20 crops with at least some price history**; availability varies by crop. Two planned crops (generic Pumpkin and Spinach) had no matching source records. Okra historical data ends early and is currently excluded from predictions.
- A trained scikit-learn HistGradientBoosting model plus **last-price** and **previous-year-same-month** baselines. One winner per 1–12-month horizon is chosen **only from validation data**.
- Fixed-origin holdout reports, training features, model artifact, crop-specific errors and test suite.
- Historical climate reanalysis from eight Karnataka city coordinates, plus optional live 3-day Open-Meteo weather for those city matches. Weather is **contextual only**, **not used** to train the price model.

## Run on Windows (the simplest way)

Requires **Python 3.11 or 3.12**; **3.12 is recommended and is the tested runtime**. Package versions are pinned to the trained artifact's environment for repeatability. You do **not** need Node.js to run the included prebuilt website. In the extracted project folder, open PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000** in Chrome or Edge. Press **Ctrl+C** in PowerShell to stop. The trained model and compiled website are already in this ZIP; the first run does **not** need to train or build them.

**If `py` is not found:** install Python 3.12 from [python.org](https://www.python.org/downloads/), enable the Python launcher and re-open PowerShell. Use `py --version` to verify installation. On some systems the alias is `python` instead of `py`.

Alternative one-command Windows script (from project root):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_windows.ps1
```

**Mac/Linux**:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Then open the same URL. API docs are at **http://127.0.0.1:8000/docs**; readiness endpoint: `/health`.

## How the website flows

1. **Welcome** — a short introduction, real-data commitment, and **Explore price outlooks** button.
2. **Choose** — vegetable → eligible district → valid future month.
3. **Understand** — the monthly wholesale price estimate, ₹/kg conversion for reading convenience, 12-month trend chart, historical-error guide, seasonality evidence, festival-calendar *context*, past/current weather when available, and test error at the selected horizon.
4. **Adjust** — return to the form to change the crop, district or month.

On **24 November 2026**, source prices are available only through **September 2026**. Since forecasts are limited to *12 months after the last observed source month*, the UI correctly offers **December 2026–September 2027** as future months; October/November 2026 predictions may appear in the full-origin chart but are no longer selectable. The site does not pretend those missing months are already observed.

## Retrain or change the code

From the project root (Python dependencies installed):

```powershell
.\.venv\Scripts\python.exe -m backend.train
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

To modify the React UI, install **Node.js 20+** and run:

```powershell
cd frontend
npm ci
npm run dev
```

Keep the FastAPI server running on port 8000; Vite serves a hot-reloading preview on **http://localhost:5173** and proxies `/api` requests to FastAPI. For a single-server deployment, run `npm run build` and use the FastAPI URL; the compiled assets are written to `frontend/dist/`.

## Dataset and provenance

See [data/README.md](data/README.md) for source files, columns, cleaning, limitations and the exact missing crops. The project contains a **snapshot** of collected AGMARKNET reports, not a constantly refreshing source. To extend into 2027 and beyond, collect and verify fresh official records, update `data/karnataka_prices.csv`, rerun training, and re-check forecasts. **Do not generate dummy rows to fill gaps.**

## Honest evaluation

**Test protocol**: train up to September 2024 and forecast October 2024–September 2025 for method selection; then refit using only data available through September 2025 and forecast October 2025–September 2026 as an untouched 12-month test. Test observations never select the winner.

- Held-out selected-method **pooled WAPE: 26.19%** (1,808 crop–district–horizon comparisons), **MAE ₹598.69 per quintal**.
- For **12 months ahead**, model-selected HGB test **WAPE: 22.67%**, **MAE ₹535.07 per quintal**, **151 comparisons**. Its September 2024 validation WAPE was **33.72%**; one test origin is not enough to guarantee the test score will recur.
- Simple baselines beat ML at several horizons. We report this, and deploy the validation-selected method for each horizon rather than falsely promising a sophisticated model always wins.
- **Do not say “85% accuracy.”** For time-series regression, MAE, WAPE, data freshness, and held-out performance are relevant. WAPE is **not** a calibrated forecast confidence or an accuracy guarantee.

Read [docs/PROJECT_WALKTHROUGH.md](docs/PROJECT_WALKTHROUGH.md) for a complete beginner-friendly explanation and interview questions, and [docs/MODEL_CARD.md](docs/MODEL_CARD.md) for horizon-by-horizon results.

For packaging and public-server setup see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). A basic `Dockerfile` is included for a single-server deployment.

## API summary

| Route | Purpose |
|---|---|
| `GET /health` | Server/model readiness and last training month |
| `GET /api/metadata` | Crops, supported districts, future months, price units |
| `POST /api/predict` | Full future price outlook and explanation |
| `GET /api/history/{crop}/{district}` | Last 60 reported district-month prices |
| `GET /api/weather/live?district=Bengaluru` | Optional current + three-day weather, supported city only |
| `GET /docs` | Interactive FastAPI API reference |

Example `POST /api/predict` JSON:

```json
{"crop":"Beans","district":"Bengaluru","month":"2026-12"}
```

## Limitations to be transparent about

- Agriculture market prices depend on supply, demand, interventions, crop quality, localized arrivals and many variables **not captured here**. This isn't trading or farm-income advice.
- Data is district-month aggregated wholesale market history. No per-mandi daily rate, no guaranteed retail price.
- Limited historical window; some crop–district series are sparse or missing recent months; only validated eligible combinations appear in the form.
- Validation and test use **one fixed forecast origin each**. More rolling-origin backtests are required for a high-confidence production evaluation.
- Festival notes identify approximate calendar windows, **not** established price drivers. No transport-disruption signals were collected.
- The 80th-percentile historical relative-error scaling around an estimate is an **illustrative error guide**, *not* a calibrated 80% interval.
- Historical weather covers only eight city coordinates and is spatially approximate; live weather needs internet and reaches just three days. **Neither is a proven input to the 12-month price model**.
- **Deployment:** The ZIP is a complete local application, not an already-hosted website. A backend-capable service that runs Python is needed for public deployment; static-only hosting will not serve the predictions.
- The included data-integrity unit tests pin the supplied **September 2026 snapshot** counts. If you intentionally replace the source dataset with newer records, update those snapshot expectations after auditing the new files.

## Technology

React 19, Vite 6, Tailwind CSS 4 and custom CSS; Python 3, FastAPI, pandas, NumPy, scikit-learn HistGradientBoosting, joblib; AGMARKNET official-data snapshot; Open-Meteo historical weather archive and optional forecast API; `unittest`.

*This is a portfolio/educational forecasting application, not a validated operational government advisory service.*
