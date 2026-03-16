# UPI AI Hackathon – Project Architecture

This document describes the **whole project setup** and high-level architecture for the UPI AI Hackathon demo.

---

## High-Level Architecture Diagram

```mermaid
flowchart TB
    subgraph Central["NPCI Central (aicode)"]
        direction TB
        AdminPortal["Admin Portal (React)"]
        FastAPI["FastAPI Backend (port 8000)"]
        ChangeStore["Change Request Store"]
        ManifestStore["Manifest Store"]
        Orchestrator["Orchestrator State"]
        XSDHost["XSD / OpenAPI Hosting"]
        AdminPortal --> FastAPI
        FastAPI --> ChangeStore
        FastAPI --> ManifestStore
        FastAPI --> Orchestrator
        FastAPI --> XSDHost
    end

    subgraph Agents["Partner PSP / Bank Agents"]
        Payer["Payer Agent (9001)"]
        Beneficiary["Beneficiary Agent (9002)"]
        Remitter["Remitter Agent (9003)"]
        Payee["Payee Agent (9004)"]
    end

    subgraph Repos["Code Repositories"]
        PayerPSP["PayerPSP (Java)"]
        PayeePSP["PayeePSP (Java)"]
        OtherRepos["BeneficiaryBank, RemitterBank, UPISim..."]
    end

    AdminPortal -->|"Submit CR, Approve, Publish"| FastAPI
    FastAPI -->|"POST /agent/manifest (signed)"| Payer
    FastAPI -->|"POST /agent/manifest"| Beneficiary
    FastAPI -->|"POST /agent/manifest"| Remitter
    FastAPI -->|"POST /agent/manifest"| Payee

    Payer -->|"POST /orchestrator/a2a/status"| FastAPI
    Beneficiary -->|"POST /orchestrator/a2a/status"| FastAPI
    Remitter -->|"POST /orchestrator/a2a/status"| FastAPI
    Payee -->|"POST /orchestrator/a2a/status"| FastAPI

    Payer -->|"Apply patch"| PayerPSP
    Payee -->|"Apply patch"| PayeePSP
    Beneficiary -->|"Apply patch"| OtherRepos
    Remitter -->|"Apply patch"| OtherRepos
```

---

## Component Overview

| Component | Location | Port | Role |
|-----------|----------|------|------|
| **NPCI AI Agent (Central)** | `aicode/` | **8000** | Change lifecycle, spec generation, XSD/OpenAPI, signed manifest creation, broadcast to partners, orchestrator. |
| **Admin Portal** | `aicode/frontend/` | Served by 8000 | Product/Developer UI: change requests, approve, view patch, publish manifest, status center. |
| **Payer Agent** | `Payer-agent/` | **9001** | Receives manifest, LLM-generated code patch, XSD update, tests; reports status to orchestrator. |
| **Beneficiary Agent** | `Beneficiary-agent/` | **9002** | Same flow as Payer (manifest → generate → approve → READY). |
| **Remitter Agent** | `Remitter-agent/` | **9003** | Same flow. |
| **Payee Agent** | `Payee-agent/` | **9004** | Same flow. |
| **Java codebases** | `javacoderepo/` or `UPIVerse/` | — | PayerPSP, PayeePSP, BeneficiaryBank, RemitterBank, UPISim; agents apply patches here. |

---

## Data Flow (Simplified)

```mermaid
sequenceDiagram
    participant Product as Product (Admin Portal)
    participant NPCI as NPCI Central (aicode)
    participant Dev as Developer
    participant Payer as Payer Agent
    participant Repo as Java Repo (e.g. PayerPSP)

    Product->>NPCI: Submit change request (XSD/XML/description)
    NPCI->>NPCI: Spec generate (LLM) → XSD, OpenAPI
    Product->>NPCI: Product approve
    Dev->>NPCI: Developer approve
    NPCI->>NPCI: Generate patch (Java diff)
    Dev->>NPCI: View code, approve
    NPCI->>NPCI: Create signed manifest
    Product->>NPCI: Broadcast manifest to partners

    NPCI->>Payer: POST /agent/manifest (signed)
    Payer->>Payer: Verify signature, validate, store → RECEIVED
    Payer->>NPCI: (optional) POST /orchestrator/a2a/status RECEIVED

    Payer->>Payer: User clicks "Generate" → LLM patch, XSD, tests
    Payer->>Repo: Apply patch (or save for manual apply)
    Payer->>Payer: User Approve → APPLIED
    Payer->>NPCI: POST /orchestrator/a2a/status READY

    NPCI->>Product: Status Center shows Payer: READY, etc.
```

---

## Key Endpoints

### NPCI Central (aicode – port 8000)

| Endpoint | Purpose |
|----------|---------|
| `GET /` | Admin Portal (SPA) |
| `POST /npciswitch/spec/generate` | Generate spec from change request |
| `POST /npciswitch/spec/approve/{changeId}` | Product approve |
| `PATCH /npciswitch/change-requests/{changeId}` | Developer approve (creates manifest when Approved) |
| `GET /npciswitch/dev/patch/{changeId}` | Get generated Java patch |
| `POST /npciswitch/manifest/broadcast/{changeId}` | Send manifest to all partners |
| `POST /npciswitch/manifest/send/{changeId}/{partnerId}` | Send manifest to one partner |
| `GET /orchestrator/status` | Full status (per change, per agent) |
| `POST /orchestrator/a2a/status` | Partners report status (RECEIVED, APPLIED, TESTED, READY) |
| `GET /npciswitch/xsd/{changeId}/{file}` | Serve XSD |
| `GET /npciswitch/openapi/{changeId}/{file}` | Serve OpenAPI spec |

### Partner agents (e.g. Payer – port 9001)

| Endpoint | Purpose |
|----------|---------|
| `GET /` | Agent UI |
| `GET /health` | Health + OpenAI configured |
| `POST /agent/manifest` | Receive signed manifest (RECEIVED) |
| `GET /agent/status` | List all changes and states |
| `GET /agent/status/{change_id}` | Get one change (state, artifacts) |
| `POST /agent/status/{change_id}/generate` | Run LLM: patch + XSD + tests |
| `POST /agent/status/{change_id}/approve` | Mark APPLIED, notify orchestrator READY |
| `POST /agent/status/{change_id}/generate-tests` | Generate unit tests, set TESTS_READY |
| `POST /agent/status/{change_id}/run-tests` | Mark TESTED, notify orchestrator |

---

## Partner Registry

Partners and endpoints are defined in **`aicode/partners.json`**:

- `PAYER_AGENT` → `http://localhost:9001/agent/manifest`
- `BENEFICIARY_AGENT` → `http://localhost:9002/agent/manifest`
- `REMITTER_AGENT` → `http://localhost:9003/agent/manifest`
- `PAYEE_AGENT` → `http://localhost:9004/agent/manifest`

Orchestrator URL for agents is set via **`ORCHESTRATOR_URL`** (default `http://localhost:8000`).

---

## Environment / Run Requirements

- **Python 3.x** (aicode + all agents); **Node.js** for frontends.
- **aicode**: `pip install -r requirements.txt`, set `OPENAI_API_KEY` in `aicode/.env`, run `uvicorn` (e.g. port 8000).
- **Each agent**: `pip install -r requirements.txt`, `OPENAI_API_KEY` and optionally `ORCHESTRATOR_URL`, `PAYER_PSP_REPO` (or equivalent) in `.env`; run on 9001, 9002, 9003, 9004.
- **Optional**: Build React frontends (`npm run build`) so backends serve `frontend/dist`.

This architecture supports the end-to-end demo: **change request at NPCI → spec & patch → signed manifest → broadcast to Payer/Payee/Remitter/Beneficiary → each agent generates and applies changes → status back to orchestrator**.
