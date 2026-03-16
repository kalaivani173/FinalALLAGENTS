# Payer-agent React UI

## Development

1. Start the FastAPI backend on port **9001** (from project root):
   ```bash
   uvicorn app:app --reload --port 9001
   ```

2. Start the React dev server (from this folder):
   ```bash
   npm install
   npm run dev
   ```

3. Open **http://localhost:5173** — Vite proxies `/agent` and `/health` to the backend.

## Production build

From this folder:

```bash
npm install
npm run build
```

Then run FastAPI from the project root on port **9001**:
   ```bash
   uvicorn app:app --port 9001
   ```
   The app will serve the built UI from `frontend/dist` at **http://localhost:9001/** (if `frontend/dist` exists).
