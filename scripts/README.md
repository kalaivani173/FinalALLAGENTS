# Scripts to run agent services

From the **Allagents** repo root (`d:\UPI-Hackathon-2\Allagents`):

## Start all backends (PayerPSP, PayeePSP, RemitterBank, BeneficiaryBank)

```powershell
.\scripts\start-agent-backends.ps1
```

Opens 4 PowerShell windows, one per agent backend:

- PayerPSP (Payer-agent) → http://localhost:9001  
- BeneficiaryBank → http://localhost:9002  
- RemitterBank → http://localhost:9003  
- PayeePSP (Payee-agent) → http://localhost:9004  

## Start all frontends

```powershell
.\scripts\start-agent-frontends.ps1
```

Opens 4 PowerShell windows, one per agent UI:

- PayerPSP → http://localhost:5173  
- BeneficiaryBank → http://localhost:5174  
- RemitterBank → http://localhost:5175  
- PayeePSP → http://localhost:5176  

## Order

1. Run `start-agent-backends.ps1` first (so backends are up before you open UIs).  
2. Run `start-agent-frontends.ps1`.  
3. Close each window to stop that backend or frontend.

## Prerequisites

- Python with dependencies installed for each agent (e.g. `pip install -r requirements.txt` in each agent folder if present).  
- Node/npm: run `npm install` once in each agent’s `frontend` folder before using the frontend script.
