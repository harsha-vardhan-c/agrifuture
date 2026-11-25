# Deployment guide

The ZIP contains an already-built React site and a saved model, so FastAPI can serve both on the **same port**. It must run on a platform capable of executing Python; a static page hosting service alone cannot execute `/api/predict`.

## Option A: Run on your Windows laptop

1. Unzip to a simple path, such as `C:\Users\harsh\Desktop\AgriForecast`.
2. Open PowerShell inside the unzipped project folder (where `requirements.txt` is visible).
3. Run `py -m venv .venv`.
4. Run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.
5. Run `.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000`.
6. Visit **http://127.0.0.1:8000**. Verify the homepage, a prediction and `/health`.

No API token or database account is needed for the included historical-price predictions. Live weather needs outgoing internet access to Open-Meteo; if unavailable, the site handles it as a missing optional feature.

## Option B: Container-based deployment

If you have Docker installed:

```bash
docker build -t agriforecast-karnataka .
docker run --rm -p 8000:8000 agriforecast-karnataka
```

Open **http://localhost:8000**. Choose a hosting provider supporting a container with **at least approximately 1 GB RAM**, map incoming HTTP traffic to port 8000, and ensure the app's model and CSV assets are included. The `Dockerfile` uses the shipped compiled frontend and stored model. Actual cloud-host configuration varies; no public deployment was performed in this deliverable.

## Option C: Edit UI locally

Install Node.js 20+, then use two terminals:

```powershell
# Terminal 1, project root
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

```powershell
# Terminal 2, frontend folder
npm ci
npm run dev
```

Edit `frontend/src/App.jsx` or `frontend/src/styles.css`, then run `npm run build` for the integrated single-server version.

## Before sending the app to farmers

- Update the official data snapshot and retrain. The shipped source ends **September 2026**.
- Expand multi-origin backtesting and measure crop/district fairness. Some holdouts have large errors.
- Add source monitoring, operational logging, rate limiting, error monitoring and language localization.
- Keep the disclaimer that this is an exploratory wholesale monthly projection, not a guaranteed mandi quote.
- Test on actual farmer phones and low-bandwidth connections.
