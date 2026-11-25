# Frontend

This is the full React 19 + Vite 6 + Tailwind CSS 4 source. The `dist/` folder is already built so Windows users can simply run the Python backend. Source entry point: `src/App.jsx`; styling: `src/styles.css`.

When editing the UI:

```bash
npm ci
npm run dev
```

Start the FastAPI backend on port 8000 separately, because the development proxy passes `/api` there. Visit http://localhost:5173 for a hot-reloading preview.

For production:

```bash
npm run build
```

FastAPI automatically hosts the rebuilt files in `dist/` at port 8000. A static-only host cannot run the Python prediction service.
