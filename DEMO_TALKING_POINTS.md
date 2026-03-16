# UPI AI Hackathon – Demo Talking Points

Use this as a checklist of **main required things to mention** during a demo of the project.

---

## 1. Problem & Goal

- **Problem**: NPCI publishes UPI specification changes (XSD, new/updated APIs). PSPs and banks must integrate these changes into their codebases quickly and correctly.
- **Goal**: Automate the **change communication and integration** flow: from change request → spec/XSD/OpenAPI → signed manifest → delivery to Payer/Payee/Remitter/Beneficiary agents → **AI-assisted code updates and tests** → status back to NPCI.

---

## 2. High-Level Flow (What to Show)

1. **Central (NPCI) – Admin Portal**
   - Product/Developer submits a **change request** (e.g. new API or field addition).
   - System **generates spec** (XSD, OpenAPI) using AI.
   - **Product approval** → **Developer approval** → system generates **Java patch**.
   - Developer can **view diff** and approve; then system creates **signed manifest**.
   - **Publish**: broadcast manifest to all partners (or send to selected partner).

2. **Partner agents (e.g. Payer)**
   - Agent **receives manifest** (signature verified), stores it, status = RECEIVED.
   - User clicks **Generate**: AI produces **code patch**, **XSD update**, and **unit tests**.
   - User **reviews and approves** → status APPLIED; agent notifies orchestrator with **READY**.
   - Optional: **Generate tests** → TESTS_READY → **Test now** → TESTED → orchestrator updated.

3. **Orchestrator (Status Center)**
   - Central view of **per-change, per-partner status** (RECEIVED, APPLIED, TESTED, READY).
   - Shows that partners have received and actioned the manifest.

---

## 3. Technical Highlights to Mention

- **Signed manifests**: NPCI signs manifests; agents verify with NPCI public key (RSA-SHA256).
- **Single source of truth**: XSD and OpenAPI are **hosted by the central service**; manifest carries URLs so partners always use the same spec.
- **Agent–orchestrator contract**: Partners report status via `POST /orchestrator/a2a/status` (RECEIVED, APPLIED, TESTED, READY).
- **AI usage**: LLM used for spec generation, Java patch generation, XSD updates, and unit test generation (OpenAI; key in `.env`).
- **Multi-role**: Same agent pattern for Payer, Payee, Remitter, Beneficiary; each has its own port and (optionally) its own Java repo.

---

## 4. What to Demo (Checklist)

- [ ] **Admin Portal** (http://localhost:8000): Login/role, submit change request, run spec generate.
- [ ] **Product approve** → **Developer approve** → **View code (patch)** → approve.
- [ ] **Create manifest** (on Developer approve) → **Publish** → **Broadcast** or **Send to one partner**.
- [ ] **Payer Agent** (http://localhost:9001): Show received change, click **Generate**, show generated patch/XSD/tests.
- [ ] **Approve** on Payer → confirm **orchestrator** shows Payer: READY (Status Center on central).
- [ ] Optionally show **Payee / Remitter / Beneficiary** agents receiving the same manifest.
- [ ] **Swagger UI**: Open OpenAPI UI for a change (e.g. `/npciswitch/openapi-ui/{changeId}`) and show mock API.

---

## 5. Prerequisites to Call Out

- **Services running**: NPCI Central (8000), at least one agent (e.g. Payer 9001). For full demo: all four agents (9001–9004).
- **Environment**: `OPENAI_API_KEY` set in `aicode/.env` and each agent’s `.env`.
- **Partner registry**: `aicode/partners.json` with correct agent URLs (localhost and ports).
- **Optional**: Java repos (e.g. PayerPSP) available for applying patches; agents can still generate and show patches without applying.

---

## 6. One-Liner Summary

**“NPCI defines changes and publishes signed manifests; partner agents receive them, use AI to generate code patches and tests, and report readiness back to a central orchestrator—so the whole UPI change lifecycle is visible and automated end-to-end.”**

---

## 7. Architecture Reference

- **Architecture diagram and endpoints**: see [ARCHITECTURE.md](./ARCHITECTURE.md).
- **Ports**: Central **8000**; Payer **9001**, Beneficiary **9002**, Remitter **9003**, Payee **9004**.
