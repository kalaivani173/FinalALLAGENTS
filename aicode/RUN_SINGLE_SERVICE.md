# Run everything on one service (port 8000)

You can run the **frontend and backend from a single process** so you only open **http://localhost:8000** (no separate Vite on 3000).

## Steps

1. **Build the frontend for same-origin API** (so the app uses relative URLs when served from the backend):

   ```bash
   cd frontend
   npm run build:single
   ```

   Or manually with empty API base:

   ```bash
   cd frontend
   set VITE_API_BASE_URL=
   npm run build
   ```

2. **Start the backend** (from the project root, e.g. `aicode`):

   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Open **http://localhost:8000** in the browser. The app and all APIs (including XSD and manifest download) are on the same origin.

## Development (two processes)

- **Frontend:** `cd frontend && npm run dev` → http://localhost:3000 (Vite proxies `/agent`, `/npciswitch`, `/health` to 8000).
- **Backend:** `python -m uvicorn main:app --reload --port 8000`.

You only need to open **http://localhost:3000**; the proxy forwards API calls to the backend.
