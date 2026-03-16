# Payer Agent – Journey & Behind the Scenes (Demo Talking Points)

Short sentences to say **what is actually happening** when each button/action is clicked during a Payer agent demo.

---

## Journey Overview

1. **Manifest arrives** – NPCI Central broadcasts (or sends to partner) → `POST /agent/manifest` hits Payer agent.
2. **User opens Payer Agent** (http://localhost:9001) → sees list of received changes.
3. **User opens a change** → views manifest, then clicks **Generate**.
4. **Generate** → AI produces code patch, XSD update, runs tests; user reviews diff.
5. **(Optional) Test** → LLM generates unit tests; status becomes TESTS_READY.
6. **(Optional) TEST NOW** → marks as tested; notifies orchestrator.
7. **Approve** → status APPLIED; agent notifies orchestrator with READY.
8. **(Optional) Deploy** → marks as DEPLOYED (UI-only status).

---

## Behind the Scenes per Click

### List Page

| Action | Behind the Scenes |
|--------|-------------------|
| **Page load / Refresh** | `GET /agent/status` – lists all change IDs and their state (RECEIVED, APPLIED, TESTS_READY, TESTED, DEPLOYED) from local artifacts. |
| **Open** (or click row / Change ID) | Navigates to `/changes/{changeId}` (detail page). |
| **Manifest receipt** *(not a UI click)* | When NPCI broadcasts: central calls `POST /agent/manifest` → agent verifies signature, validates manifest, saves it, sets state RECEIVED. |

### Change Detail Page

| Action | Behind the Scenes |
|--------|-------------------|
| **Page load** | `GET /agent/status/{changeId}` – loads state, manifest, and artifacts (patch, XSD, tests) for this change. |
| **← Back to list** | Navigates back to list page. |
| **Manifest / Diff / Tests / Artifacts tabs** | Client-side tab switch; no API call. |
| **Generate** | `POST /agent/status/{changeId}/generate` → runs `process_manifest`: (1) scans repo, builds vector index, (2) retrieves relevant code via RAG, (3) LLM generates Java patch, (4) updates XSD, (5) runs Maven/Gradle tests, (6) stores patch/XSD/tests, sets state RECEIVED. Switches to Diff tab. |
| **Test** | `POST /agent/status/{changeId}/generate-tests` → LLM generates unit tests (GeneratedTest.java), saves to artifacts, sets state TESTS_READY, notifies orchestrator with APPLIED. Switches to Tests tab. |
| **TEST NOW** | `POST /agent/status/{changeId}/run-tests` → sets state TESTED, notifies orchestrator with TESTED. |
| **Approve** | `POST /agent/status/{changeId}/approve` → sets state APPLIED, notifies orchestrator with READY via `POST /orchestrator/a2a/status`. |
| **Deploy** | `POST /agent/status/{changeId}/deploy` → sets state DEPLOYED (UI status only; no file deployment in this endpoint). |

---

## State Flow

```
RECEIVED ──(Generate)──► RECEIVED (with patch)
      │
      └──(Test)────► TESTS_READY ──(TEST NOW)──► TESTED ──(Approve)──► APPLIED ──(Deploy)──► DEPLOYED
```

---

## One-Liner Summary for Payer Agent

**NPCI sends manifest to Payer agent → agent verifies and stores it → user clicks Generate → AI produces Java patch, XSD update, and test output → user reviews, optionally generates tests, approves → agent notifies orchestrator READY.**
