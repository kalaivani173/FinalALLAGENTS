# Field Addition – Behind the Scenes (Demo Talking Points per Click)

Short sentences to say **what is actually happening** when each button/action is clicked during a Field Addition demo.

---

## Product Side (Create Change Request → Field Addition)

| Action | Behind the Scenes |
|--------|-------------------|
| **Select "Field Addition"** | Switches to the Field Addition workflow; form shows schema upload and fields editor. |
| **Upload XSD** (radio + file picker) | File is read in the browser and parsed; elements and attributes are extracted for the field dropdowns. |
| **Upload sample XML** (radio + file picker) | Calls `POST /agent/xsd/convert-sample-xml`; backend converts XML to XSD; result becomes baseline schema. |
| **Add field** | Adds a row to the `fieldAdditions` list; XSD is recomputed in the browser with the new attribute. |
| **Remove** (on a field row) | Removes that field from the list; XSD updates automatically. |
| **Submit** | (1) Uploads BRD and XSD artifacts → (2) `POST /npciswitch/spec/generate` (generates updated XSD with new attributes) → (3) `POST /npciswitch/change-requests` (saves CR) → (4) `POST /npciswitch/spec/approve` (approves spec) → (5) Optionally pre-generates Java patch. CR is sent to Developer. |
| **View in Change Management** | Navigates to the Change Management tab to track the CR. |
| **Create another request** | Resets the form so you can submit a new CR. |

---

## Developer Side (Change Requests tab)

| Action | Behind the Scenes |
|--------|-------------------|
| **Refresh** | Calls `GET /npciswitch/change-requests` to reload the list of CRs. |
| **View code** (or click Change ID) | (1) `GET /npciswitch/change-requests/{id}` loads CR details → (2) If no code yet: `GET /npciswitch/dev/patch/{id}` generates Java DTO patch from XSD changes. Opens Code Comparison modal. |
| **Approve** (in Code Comparison modal) | (1) Uploads product note if selected → (2) `POST /npciswitch/spec/approve` → (3) `PATCH /npciswitch/change-requests/{id}` with status `Approved` → Backend creates and stores the signed manifest. |
| **Reject** (in Code Comparison modal) | `PATCH /npciswitch/change-requests/{id}` with status `Rejected`; no manifest is created. |
| **Deploy** (Field Addition only, after Approved) | Deploys approved Java changes to javacoderepo; existing files are renamed with `_old` extension. |

---

## One-Liner Summary for Field Addition

**Product uploads baseline XSD (or converts sample XML), adds fields in the UI, and submits → backend generates updated XSD and Java patch → Developer views code, approves → manifest is created → optionally Deploy pushes code to javacoderepo.**
