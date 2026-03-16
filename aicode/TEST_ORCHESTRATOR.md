# How to test the orchestrator endpoints

Parties (Payer, Payee, Banks) report status **RECEIVED / APPLIED / TESTED / READY** after receiving our manifest. This guide shows how to test that the API works.

---

## How change ID, bank/agent, and status are stored

- **In memory:** `ORCHESTRATOR_STATE` is a dict: **key = change ID**, **value = dict of agent → status**.
- **On disk:** Same structure is written to **`artifacts/orchestrator_state.json`** after every update (so it survives server restart).

**Shape:**

```text
ORCHESTRATOR_STATE = {
  "CHG-624": {
    "Payer":   "RECEIVED",
    "Payee":   "APPLIED",
    "Bank_A":  "TESTED",
    "Bank_B":  "READY"
  },
  "CHG-331": {
    "Payer": "RECEIVED",
    "Bank_X": "APPLIED"
  }
}
```

- **Change ID** = top-level key (e.g. `"CHG-624"`).
- **Bank / agent** = key inside that change (e.g. `"Payer"`, `"Payee"`, `"Bank_A"`). Any string the party sends as `agent` is stored.
- **Status** = value for that agent: one of `RECEIVED`, `APPLIED`, `TESTED`, `READY`.

**File location:** `artifacts/orchestrator_state.json` (same JSON structure). Loaded on startup, saved after each **POST /orchestrator/a2a/status**.

## 1. Start the backend

From the project root (e.g. `aicode`):

```bash
python -m uvicorn main:app --reload --port 8000
```

## 2. Report status (party updates us)

**POST /orchestrator/a2a/status** – body must have `changeId`, `agent`, and `status` (one of: RECEIVED, APPLIED, TESTED, READY).

### PowerShell

```powershell
# Payer reports RECEIVED
Invoke-RestMethod -Uri "http://localhost:8000/orchestrator/a2a/status" -Method POST -ContentType "application/json" -Body '{"changeId":"CHG-624","agent":"Payer","status":"RECEIVED"}'

# Payee reports APPLIED
Invoke-RestMethod -Uri "http://localhost:8000/orchestrator/a2a/status" -Method POST -ContentType "application/json" -Body '{"changeId":"CHG-624","agent":"Payee","status":"APPLIED"}'

# Bank_A reports TESTED
Invoke-RestMethod -Uri "http://localhost:8000/orchestrator/a2a/status" -Method POST -ContentType "application/json" -Body '{"changeId":"CHG-624","agent":"Bank_A","status":"TESTED"}'

# Bank_B reports READY
Invoke-RestMethod -Uri "http://localhost:8000/orchestrator/a2a/status" -Method POST -ContentType "application/json" -Body '{"changeId":"CHG-624","agent":"Bank_B","status":"READY"}'
```

Expected response each time: `{"ack":"RECEIVED"}`

### curl (if installed)

```bash
curl -X POST http://localhost:8000/orchestrator/a2a/status \
  -H "Content-Type: application/json" \
  -d "{\"changeId\":\"CHG-624\",\"agent\":\"Payer\",\"status\":\"RECEIVED\"}"
```

## 3. View orchestration status for a change

**GET /orchestrator/change/{change_id}** – returns which agents have reported and their status.

### PowerShell

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/orchestrator/change/CHG-624" -Method GET
```

Expected (after the calls above):

```json
{
  "changeId": "CHG-624",
  "agents": {
    "Payer": "RECEIVED",
    "Payee": "APPLIED",
    "Bank_A": "TESTED",
    "Bank_B": "READY"
  }
}
```

### curl

```bash
curl http://localhost:8000/orchestrator/change/CHG-624
```

## 4. Validation: invalid status returns 422

Send a status that is not allowed (e.g. `ADOPTED`):

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/orchestrator/a2a/status" -Method POST -ContentType "application/json" -Body '{"changeId":"CHG-624","agent":"Payer","status":"ADOPTED"}'
```

Expected: error (422) with message that only RECEIVED, APPLIED, TESTED, READY are allowed.

## 5. Persistence

State is stored in `artifacts/orchestrator_state.json`. After restarting the backend, run GET again for the same change_id – you should still see the same agents and statuses.

## 6. OpenAPI (Swagger) UI

In the browser open: **http://localhost:8000/docs**

- Find **POST /orchestrator/a2a/status** – try it with body `{"changeId":"CHG-624","agent":"Payer","status":"RECEIVED"}`.
- Find **GET /orchestrator/change/{change_id}** – try it with `change_id` = `CHG-624`.
