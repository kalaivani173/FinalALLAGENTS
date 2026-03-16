# How to test XSD hosting (same service)

XSD files are served by the backend at **GET /npciswitch/xsd/{changeId}/{filename}**. No separate XSD server is needed.

## 1. Start the backend

From the project root (e.g. `aicode`):

```bash
python -m uvicorn main:app --reload --port 8000
```

## 2. Test XSD hosting (curl or browser)

Use a change ID and XSD file that exist under `artifacts/xsd/` (e.g. CHG-624, ReqPay.xsd).

**Browser:** open  
`http://localhost:8000/npciswitch/xsd/CHG-624/ReqPay.xsd`  
You should see the XSD XML or a download.

**PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/npciswitch/xsd/CHG-624/ReqPay.xsd" -UseBasicParsing | Select-Object -ExpandProperty Content
```

**curl (if available):**
```bash
curl -s http://localhost:8000/npciswitch/xsd/CHG-624/ReqPay.xsd
```

Expected: HTTP 200 and XSD content. For missing file: 404.

## 3. Test manifest uses the web path

After creating a manifest (e.g. via **POST /npciswitch/manifest/create/CHG-624** or through the Product/Developer flow), open `artifacts/manifests/CHG-624.json` and check:

```json
"xsd": {
  "path": "/npciswitch/xsd/CHG-624/ReqPay.xsd"
}
```

The path should be the web path (starts with `/npciswitch/xsd/`), not a filesystem path like `artifacts\xsd\...`.

## 4. Optional: run a small Python check

From project root:

```bash
python -c "
from paths import xsd_web_path, XSD_WEB_PATH_PREFIX
p = xsd_web_path('CHG-624', 'ReqPay.xsd')
assert p == '/npciswitch/xsd/CHG-624/ReqPay.xsd', p
print('xsd_web_path OK:', p)
print('XSD_WEB_PATH_PREFIX:', XSD_WEB_PATH_PREFIX)
"
```
