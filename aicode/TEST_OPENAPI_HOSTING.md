# How to test OpenAPI/Swagger hosting (same service)

OpenAPI/Swagger spec files are served by the backend at **GET /npciswitch/openapi/{changeId}/{filename}**.
Swagger UI for a specific change is available at **GET /npciswitch/openapi-ui/{changeId}**.

Specs should be uploaded under `artifacts/specs/<changeId>/` (you can upload via **POST /agent/artifact/upload** with `artifactType` = `openapi`, `swagger`, or `specs`).

## 1. Start the backend

From the project root (e.g. `aicode`):

```bash
python -m uvicorn main:app --reload --port 8000
```

## 2. Upload an OpenAPI spec (optional)

If you don’t already have a spec file for a change, upload one:

**PowerShell example:**

```powershell
$form = @{
  changeId = "CHG-624"
  artifactType = "openapi"
  file = Get-Item ".\openapi.yaml"
}
Invoke-RestMethod -Uri "http://localhost:8000/agent/artifact/upload" -Method Post -Form $form
```

This saves it to `artifacts/specs/CHG-624/openapi.yaml`.

## 3. Fetch the hosted spec (browser / curl)

**Browser:** open  
`http://localhost:8000/npciswitch/openapi/CHG-624/openapi.yaml`

**curl (if available):**

```bash
curl -s http://localhost:8000/npciswitch/openapi/CHG-624/openapi.yaml
```

Expected: HTTP 200 and the spec content. For missing file: 404.

## 3b. View Swagger UI for the spec

Open in browser:

`http://localhost:8000/npciswitch/openapi-ui/CHG-624`

## 4. Verify manifest includes openapi.path (when present)

Create a manifest (e.g. **POST /npciswitch/manifest/create/CHG-624**) and open:

- `artifacts/manifests/CHG-624.json`

You should see (in the `manifest` object) something like:

```json
"openapi": {
  "path": "http://localhost:8000/npciswitch/openapi/CHG-624/openapi.yaml"
}
```

If no OpenAPI file exists under `artifacts/specs/CHG-624/`, the `openapi` field is omitted.

### Note: auto-generation from XSD

If `artifacts/specs/<changeId>/` has **no** OpenAPI file, the backend will **auto-generate**
`artifacts/specs/<changeId>/openapi.json` when you call **POST /npciswitch/manifest/create/{changeId}**,
as long as the change has an XSD (so the generated spec can link to the hosted XSD URL).

