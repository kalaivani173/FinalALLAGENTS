# Run PayerPSP, PayeePSP, RemitterBank, BeneficiaryBank (Agents + Frontends)

Each service has a **Python backend** (FastAPI) and a **React frontend** (Vite). Run the backend first, then the frontend (or use the scripts below).

**Ports:**

| Service          | Backend port | Frontend port |
|------------------|-------------:|---------------|
| PayerPSP         | 9001         | 5173          |
| BeneficiaryBank  | 9002         | 5174          |
| RemitterBank     | 9003         | 5175          |
| PayeePSP         | 9004         | 5176          |

---

## 1. PayerPSP (Payer-agent)

**Backend** (from repo root):

```powershell
cd d:\UPI-Hackathon-2\Allagents\Payer-agent
python -m uvicorn app:app --reload --host 127.0.0.1 --port 9001
```

**Frontend** (new terminal):

```powershell
cd d:\UPI-Hackathon-2\Allagents\Payer-agent\frontend
npm install
npm run dev
```

- Backend: http://localhost:9001  
- Frontend: http://localhost:5173  

---

## 2. BeneficiaryBank (Beneficiary-agent)

**Backend:**

```powershell
cd d:\UPI-Hackathon-2\Allagents\Beneficiary-agent
python -m uvicorn app:app --reload --host 127.0.0.1 --port 9002
```

**Frontend** (new terminal):

```powershell
cd d:\UPI-Hackathon-2\Allagents\Beneficiary-agent\frontend
npm install
npm run dev
```

- Backend: http://localhost:9002  
- Frontend: http://localhost:5174  

---

## 3. RemitterBank (Remitter-agent)

**Backend:**

```powershell
cd d:\UPI-Hackathon-2\Allagents\Remitter-agent
python -m uvicorn app:app --reload --host 127.0.0.1 --port 9003
```

**Frontend** (new terminal):

```powershell
cd d:\UPI-Hackathon-2\Allagents\Remitter-agent\frontend
npm install
npm run dev
```

- Backend: http://localhost:9003  
- Frontend: http://localhost:5175  

---

## 4. PayeePSP (Payee-agent)

**Backend:**

```powershell
cd d:\UPI-Hackathon-2\Allagents\Payee-agent
python -m uvicorn app:app --reload --host 127.0.0.1 --port 9004
```

**Frontend** (new terminal):

```powershell
cd d:\UPI-Hackathon-2\Allagents\Payee-agent\frontend
npm install
npm run dev
```

- Backend: http://localhost:9004  
- Frontend: http://localhost:5176  

---

## Quick start (PowerShell scripts)

From repo root `d:\UPI-Hackathon-2\Allagents`:

- **Start all 4 backends** (run in one terminal; each runs in background):
  ```powershell
  .\scripts\start-agent-backends.ps1
  ```

- **Start all 4 frontends** (run in one terminal):
  ```powershell
  .\scripts\start-agent-frontends.ps1
  ```

See `scripts/README.md` for details.

---

## Prerequisites

- **Python**: venv and `pip install -r requirements.txt` in each agent folder (Payer-agent, Payee-agent, Remitter-agent, Beneficiary-agent) if they have one, or use a shared env with FastAPI, uvicorn, etc.
- **Node**: `npm install` once in each agent’s `frontend` folder.
- **Optional**: Set `OPENAI_API_KEY` in env or `.env` in each agent root for manifest processing.
