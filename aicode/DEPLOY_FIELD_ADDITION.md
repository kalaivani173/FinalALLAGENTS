# Deploy to javacoderepo (Field Addition only)

Deploy copies **Field Addition** approved code from aicode into the javacoderepo. Only change type **field-addition** is supported.

## Prerequisites

- CR is **Approved** (developer has approved the code).
- All agents (Payer, Payee, Remitter, Beneficiary) have reported status **READY** via `POST /orchestrator/a2a/status`.
- CR has **files** (code was generated and stored when developer viewed/approved).

## Flow

1. **Product portal** → Status Center → tab **By Change Request**.
2. For each **Field Addition** CR, eligibility is checked (Approved + all agents READY).
3. If **eligible**, a **Deploy** button is shown in the Actions column.
4. Click **Deploy** → confirm → backend writes approved files into javacoderepo:
   - Existing file at target path is renamed to `{name}_old.{ext}`.
   - New content is written to the same path.

## Config

- **JAVACODEREPO_ROOT** (optional): Absolute path to the javacoderepo directory. Default: sibling of the aicode directory named `javacoderepo` (e.g. `d:\UPI-Hackathon-2\Allagents\javacoderepo`).

## APIs

- **GET /npciswitch/deploy/eligibility/{changeId}**  
  Returns `{ eligible, reason, crStatus, changeType, agents }`. Only Field Addition CRs can be eligible.

- **POST /npciswitch/deploy/{changeId}**  
  Deploys approved files to javacoderepo. Returns `{ success, changeId, deployedFiles, errors, javacoderepoRoot }`.

---

## Testing after deploy (javacoderepo frontend)

After deploying a Field Addition to javacoderepo:

1. **Start javacoderepo services** (e.g. UPISim on 8081, PayerPSP on 8080, etc.) and the **javacoderepo frontend** (e.g. `npm start` under `javacoderepo/frontend/frontend`).

2. **Open the frontend** (e.g. http://localhost:3000) and go to the **Payment** / transaction page.

3. **Initiate a transaction** (e.g. enter Payer VPA, Payee VPA, amount and submit). This triggers the payment flow that uses the updated DTOs in javacoderepo.

4. **Verify**:
   - Transaction completes without errors (new field is accepted if it was added to request/response).
   - In logs or response payload, confirm the new field is present where expected (e.g. in ReqPay or related DTOs).

5. **Optional**: Run javacoderepo tests (e.g. `mvn test` in UPISim or PayerPSP) to ensure nothing is broken.

If something fails, check that the deployed files are under the correct module (e.g. UPISim) and that the service was restarted after deploy so it loads the new code.
