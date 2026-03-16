# Selenium & E2E Tests

Run Selenium UI tests and API health checks for the orchestrator (aicode) and all four agents (Payer, Beneficiary, Remitter, Payee).

## Prerequisites

- Python 3.10+
- Chrome or Chromium (for Selenium)
- All services running (see below)

## Install test dependencies

From the **project root** (`Allagents`):

```bash
pip install -r tests/requirements.txt
```

## Start the services

Start each app in a separate terminal (from project root):

1. **Orchestrator (aicode)** – port 8000  
   `cd aicode && python -m uvicorn main:app --host 127.0.0.1 --port 8000`

2. **Payer agent** – port 9001  
   `cd Payer-agent && python app.py`

3. **Beneficiary agent** – port 9002  
   `cd Beneficiary-agent && python app.py`

4. **Remitter agent** – port 9003  
   `cd Remitter-agent && python app.py`

5. **Payee agent** – port 9004  
   `cd Payee-agent && python app.py`

Or use your own way to run them (e.g. different ports); then set env vars (see below).

## Run tests

From the **project root**:

```bash
# All tests (Selenium + health APIs)
pytest tests/ -v

# Only Selenium UI tests
pytest tests/test_ui_selenium.py -v

# Only API health tests (no browser)
pytest tests/test_health_apis.py -v

# With visible browser (non-headless)
set E2E_HEADED=1
pytest tests/test_ui_selenium.py -v
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ORCHESTRATOR_E2E_URL` | `http://127.0.0.1:8000` | Orchestrator base URL |
| `PAYER_AGENT_E2E_URL` | `http://127.0.0.1:9001` | Payer agent base URL |
| `BENEFICIARY_AGENT_E2E_URL` | `http://127.0.0.1:9002` | Beneficiary agent base URL |
| `REMITTER_AGENT_E2E_URL` | `http://127.0.0.1:9003` | Remitter agent base URL |
| `PAYEE_AGENT_E2E_URL` | `http://127.0.0.1:9004` | Payee agent base URL |
| `E2E_HEADED` | (unset) | Set to `1` or `true` to run Chrome in headed mode |

## What is tested

- **test_ui_selenium.py**: For each app, open `/`, check page title and presence of main content (`#root` or `.app`); optional console error check.
- **test_health_apis.py**: `GET /health` on each agent (200 + `status: ok`), orchestrator `/` and `/npciswitch/partners` return 200.

If a service is not running, the corresponding tests are **skipped** (no failure). So you can run `pytest tests/` anytime: with no services up you get 21 skipped; with only the orchestrator up you get 6 tests run (3 for orchestrator) and the rest skipped.
