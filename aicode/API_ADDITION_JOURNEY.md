# Api Addition – Journey & APIs

## Product portal (Create Change Request → Api Addition)

### 1. Upload sample dump (before Generate XSD)
- **When:** User selects a file in "Sample dump" for Api Addition.
- **API:** `POST /agent/artifact/upload`
  - Body: FormData with `changeId`, `artifactType: 'sampleRequests'`, `file`.
- **Purpose:** Store the sample request so backend can use it for spec generation.

### 2. Generate XSD (optional step – can be done before Submit)
- **When:** User clicks "Generate XSD" (Api Addition).
- **API:** `POST /npciswitch/spec/generate`
  - Body: `{ change_id, apiName, changeType: 'ADD_NEW_API', description }`.
- **Purpose:** Generate new XSD from the uploaded sample; backend uses it for the new API spec.

### 3. Submit for approval (main submit)
- **When:** User clicks "Submit" on the Api Addition form (after sample dump uploaded and optionally XSD generated).
- **APIs (in order):**
  1. **`POST /npciswitch/spec/generate`**  
     - Same as step 2; ensures XSD/spec is generated with current payload.
  2. **`POST /npciswitch/spec/approve/{changeId}`**  
     - Marks spec as approved in backend so patch can be generated.
  3. **`POST /npciswitch/change-requests`**  
     - Saves the change request (changeId, description, changeType, currentStatus, etc.) so it appears in Developer dashboard and Status Center.
  4. **`GET /npciswitch/dev/patch/{changeId}`**  
     - Generates and returns Java code changes (and backend persists them on the CR).
- **Purpose:** One-shot flow: generate spec → approve spec → save CR → get (and store) code patch. Product may also see the "Code changes" modal from the returned patch.

---

## Developer portal

### 1. List change requests
- **When:** Developer opens the "Change Requests" tab (or tab becomes active).
- **API:** `GET /npciswitch/change-requests`
- **Purpose:** Load the list of CRs (same source as Status Center).

### 2. View code (click "View code" on a row)
- **When:** Developer clicks "View code" for a change request.
- **APIs (in order):**
  1. **`GET /npciswitch/change-requests/{changeId}`**  
     - Load CR details. If the CR already has `files` (from Product submit), those are used and no further call is made.
  2. **`GET /npciswitch/dev/patch/{changeId}`** (only if `cr.files` is empty)  
     - Fallback: get (or regenerate) code patch; backend persists result on the CR.
- **Purpose:** Show code diff in the modal; prefer stored `files`, else fetch patch once.

### 3. Approve (in Code Changes modal)
- **When:** Developer clicks "Approve" in the Code Comparison modal.
- **APIs (in order):**
  1. **`POST /npciswitch/spec/approve/{changeId}`**  
     - Ensures spec is approved (e.g. if it wasn’t already from Product submit).
  2. **`PATCH /npciswitch/change-requests/{changeId}`**  
     - Body: `{ currentStatus: 'Approved', reviewComments? }`.  
     - Backend also creates and stores the manifest when status is set to Approved.
- **Purpose:** Mark CR as Approved and trigger manifest creation.

### 4. Reject (in Code Changes modal)
- **When:** Developer clicks "Reject".
- **API:** `PATCH /npciswitch/change-requests/{changeId}`
  - Body: `{ currentStatus: 'Rejected', reviewComments? }`.
- **Purpose:** Mark CR as Rejected.

---

## Summary table

| Step | Portal   | Action              | APIs triggered |
|------|----------|---------------------|--------------------------------------------------------|
| 1    | Product  | Select sample dump  | `POST /agent/artifact/upload`                          |
| 2    | Product  | Generate XSD        | `POST /npciswitch/spec/generate`                       |
| 3    | Product  | Submit              | `POST /npciswitch/spec/generate` → `POST /npciswitch/spec/approve/{id}` → `POST /npciswitch/change-requests` → `GET /npciswitch/dev/patch/{id}` |
| 4    | Developer| Open Change Requests| `GET /npciswitch/change-requests`                      |
| 5    | Developer| View code           | `GET /npciswitch/change-requests/{id}` → (if no files) `GET /npciswitch/dev/patch/{id}` |
| 6    | Developer| Approve             | `POST /npciswitch/spec/approve/{id}` → `PATCH /npciswitch/change-requests/{id}` (manifest created by backend on approve) |
| 7    | Developer| Reject              | `PATCH /npciswitch/change-requests/{id}`               |

---

## Backend routes (main.py)

- `POST /agent/artifact/upload` – upload artifacts (e.g. sample requests).
- `POST /npciswitch/spec/generate` – generate spec/XSD (uses agent).
- `POST /npciswitch/spec/approve/{changeId}` – approve spec (uses agent).
- `GET /npciswitch/dev/patch/{changeId}` – get (and persist) code patch (uses agent).
- `GET /npciswitch/change-requests` – list CRs.
- `GET /npciswitch/change-requests/{changeId}` – get one CR.
- `POST /npciswitch/change-requests` – create/update CR.
- `PATCH /npciswitch/change-requests/{changeId}` – update CR status (and trigger manifest create on Approved).
