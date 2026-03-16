# Field Addition – Journey & APIs

## Product portal (Create Change Request → Field Addition)

### 1. Schema input (baseline XSD)
Product must provide a baseline XSD in one of two ways:

- **Option A – Upload XSD file**  
  - **When:** User uploads an `.xsd` file in the schema section.  
  - **API:** None (file is read in the browser and parsed for elements/attributes).  
  - **Purpose:** Set `currentXsdContent` and drive the field-additions editor.

- **Option B – Upload sample XML (convert to XSD)**  
  - **When:** User uploads a sample XML and triggers conversion.  
  - **API:** `POST /agent/xsd/convert-sample-xml`  
    - Body: FormData with `file` (the sample XML).  
  - **Response:** `{ xsd }` – generated XSD used as baseline.  
  - **Purpose:** Derive baseline XSD from a sample so Product can then add fields in the UI.

### 2. Add fields (client-side)
- **When:** User adds rows (element, attribute, datatype, mandatory, allowed values, etc.) in the Field Addition editor.  
- **API:** None.  
- **Purpose:** Build the `fieldAdditions` list; updated XSD is computed in the browser via `applyFieldAdditionsToXsd`.

### 3. Submit for approval
- **When:** User clicks **Submit** on the Field Addition form (after baseline XSD and at least one field addition).  
- **APIs (in order):**

  1. **`POST /agent/artifact/upload`** (optional, if BRD document is attached)  
     - FormData: `changeId`, `artifactType: 'brdDocuments'`, `file`.  

  2. **`POST /agent/artifact/upload`** (baseline XSD)  
     - FormData: `changeId`, `artifactType: 'xsd'`, `file` (XSD as File), `apiName`.  

  3. **`POST /npciswitch/spec/generate`**  
     - Body: `change_id`, `apiName`, `changeType: 'ADD_XML_ATTRIBUTE'`, `description`, `xsdContent` (baseline), `fieldAdditions` (array of `{ xmlPath, elementName, attributeName, datatype, mandatory, allowedValues }`), plus first addition’s fields for backward compatibility.  
     - **Purpose:** Generate updated XSD with new attributes and store spec in backend (agent `CHANGE_STORE`).  

  4. **`POST /npciswitch/change-requests`**  
     - Body: `changeId`, `description`, `changeType: 'field-addition'`, `apiName`, `currentStatus: 'Waiting for Developer Approval'`, `receivedDate`, `updatedOn`.  
     - **Purpose:** Persist the CR so it appears in Developer dashboard and Status Center.  

  5. **`POST /npciswitch/spec/approve/{changeId}`**  
     - **Purpose:** Approve the spec in the backend so a later `dev/patch` call can return code changes.  

  6. **`GET /npciswitch/dev/patch/{changeId}`** (if implemented on submit)  
     - **Purpose:** Pre-generate Java patch and persist it on the CR so Developer “View code” can show results without calling patch again.  
     - *Note: If this is not called on submit, the first patch generation happens when Developer clicks “View code”.*

- **No API:** The “Get Dev Patch” button in the Product UI (for spec flows) calls `GET /npciswitch/dev/patch/{changeId}` when Product wants to see the code diff before or after submit.

---

## Developer portal (same as Api Addition for viewing / approving)

### 1. List change requests
- **When:** Developer opens the Change Requests tab.  
- **API:** `GET /npciswitch/change-requests`.  
- **Purpose:** Load list of CRs (including Field Addition CRs).

### 2. View code
- **When:** Developer clicks **View code** on a Field Addition CR.  
- **APIs:**  
  1. **`GET /npciswitch/change-requests/{changeId}`** – load CR details (if backend stored `files` on the CR, code changes are shown from here).  
  2. **`GET /npciswitch/dev/patch/{changeId}`** – called only if `cr.files` is empty; returns (and backend can persist) Java code changes.  
- **Purpose:** Show code diff in the modal; avoid a second patch call when `files` are already on the CR.

### 3. Approve
- **When:** Developer clicks **Approve** in the Code Comparison modal.  
- **APIs:**  
  1. **`POST /npciswitch/spec/approve/{changeId}`**  
  2. **`PATCH /npciswitch/change-requests/{changeId}`** with `currentStatus: 'Approved'`, `reviewComments?`.  
     - Backend creates and stores the manifest when status is set to Approved.  
- **Purpose:** Mark CR as Approved and trigger manifest creation.

### 4. Reject
- **When:** Developer clicks **Reject**.  
- **API:** `PATCH /npciswitch/change-requests/{changeId}` with `currentStatus: 'Rejected'`, `reviewComments?`.  
- **Purpose:** Mark CR as Rejected.

---

## Summary table (Field Addition)

| Step | Portal   | Action                    | APIs triggered |
|------|----------|---------------------------|--------------------------------------------------------------------------------------------------|
| 1a   | Product  | Upload XSD                | None (client-side parse)                                                                         |
| 1b   | Product  | Convert sample XML → XSD   | `POST /agent/xsd/convert-sample-xml`                                                            |
| 2    | Product  | Add fields in UI           | None (client-side)                                                                               |
| 3    | Product  | Submit                    | `POST /agent/artifact/upload` (BRD, XSD) → `POST /npciswitch/spec/generate` → `POST /npciswitch/change-requests` → `POST /npciswitch/spec/approve/{id}` → optionally `GET /npciswitch/dev/patch/{id}` |
| 4    | Developer| Open Change Requests      | `GET /npciswitch/change-requests`                                                                |
| 5    | Developer| View code                 | `GET /npciswitch/change-requests/{id}` → if no files: `GET /npciswitch/dev/patch/{id}`           |
| 6    | Developer| Approve                   | `POST /npciswitch/spec/approve/{id}` → `PATCH /npciswitch/change-requests/{id}`                   |
| 7    | Developer| Reject                    | `PATCH /npciswitch/change-requests/{id}`                                                         |

---

## Differences from Api Addition

| Aspect              | Api Addition                    | Field Addition                                      |
|---------------------|----------------------------------|-----------------------------------------------------|
| Input               | Sample dump (XML)                | Baseline XSD (upload or from sample XML conversion) |
| Spec generate       | `changeType: 'ADD_NEW_API'`      | `changeType: 'ADD_XML_ATTRIBUTE'` + `fieldAdditions` |
| Artifacts on submit | Sample uploaded earlier          | BRD (optional), baseline XSD                        |
| XSD generation      | Backend from sample               | Backend from baseline XSD + field additions          |
| Approve / patch     | Same pattern                     | Same pattern (spec/approve, then dev/patch when needed) |

Developer-side flow (list CRs, View code, Approve/Reject) is the same for both change types; only the Product-side inputs and `spec/generate` payload differ.
