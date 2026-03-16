# Signed manifest flow: generate keys → sign → send → verify

## 1. Generate keys (one-time)

From the project root:

```bash
python generate_keys.py
```

This creates:

- `keys/npci_private.pem` – used by the backend to **sign** manifests (keep secret).
- `keys/npci_public.pem` – shared with **users** so they can **verify** signatures.

## 2. Sign the manifest (backend)

Manifests are signed automatically when:

- **POST /npciswitch/manifest/create/{changeId}** is called (Developer approves), or
- The agent creates a manifest after approval (`_maybe_create_manifest`).

Stored file format (`artifacts/manifests/{changeId}.json`):

```json
{
  "manifest": {
    "changeId": "CHG-624",
    "issuer": "NPCI_UPI_SWITCH",
    "changeType": "api-addition",
    "apiName": "ReqPay",
    "summary": "...",
    "impactedPaths": [...],
    "xsd": { "path": "/npciswitch/xsd/CHG-624/ReqPay.xsd" },
    "npciStatus": "READY_FOR_ADOPTION",
    "timestamp": "2026-01-29T..."
  },
  "signature": {
    "algorithm": "RSA-SHA256",
    "signedBy": "NPCI",
    "value": "<base64-encoded-signature>"
  }
}
```

Signing uses the **crypto** module: `crypto.signing.sign_payload` and `crypto.key_loader.load_private_key`.

## 3. Send signed manifest to user

- **Download:** User fetches the signed manifest, e.g.  
  **GET /npciswitch/manifest/{changeId}/download**  
  or **GET /npciswitch/manifest/{changeId}** (JSON).
- **Broadcast/send:** Backend can send the same JSON to partners via  
  **POST /npciswitch/manifest/broadcast/{changeId}** or  
  **POST /npciswitch/manifest/send/{changeId}/{partnerId}**.

The payload the user receives is the full signed manifest: `{ "manifest": {...}, "signature": {...} }`.

## 4. User verifies signature and content

### Option A: Use the API

- **Get public key:**  
  **GET /npciswitch/keys/public**  
  Returns the NPCI public key PEM (so the user can verify without trusting the server for verification).

- **Verify a signed manifest:**  
  **POST /npciswitch/manifest/verify**  
  Body: the full signed manifest (`{ "manifest": {...}, "signature": {...} }`).

  Response:

  ```json
  {
    "verified": true,
    "contentValid": true
  }
  ```

  - `verified`: signature is valid for the given `manifest` using the NPCI public key.
  - `contentValid`: manifest has required fields (`changeId`, `issuer`, `timestamp`).

### Option B: Verify in user’s own code (Python)

User has the signed manifest and the public key PEM:

```python
import base64, json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend

def canonicalize(payload):
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

# Load public key (from GET /npciswitch/keys/public or keys/npci_public.pem)
with open("npci_public.pem", "rb") as f:
    public_key = load_pem_public_key(f.read(), backend=default_backend())

signed_manifest = { "manifest": {...}, "signature": { "value": "<base64>" } }
manifest = signed_manifest["manifest"]
signature_b64 = signed_manifest["signature"]["value"]

payload_bytes = canonicalize(manifest)
signature_bytes = base64.b64decode(signature_b64)
public_key.verify(signature_bytes, payload_bytes, padding.PKCS1v15(), hashes.SHA256())
# No exception => signature valid; then check manifest content (changeId, issuer, etc.)
```

Or use the same logic as in **crypto/signing.py** (`verify_signature`) and **crypto/key_loader.py** (`load_public_key`).

## Summary

| Step | Who | Action |
|------|-----|--------|
| 1 | Operator | Run `python generate_keys.py` once |
| 2 | Backend | Sign manifest when creating (crypto + private key) |
| 3 | Backend | Send signed manifest to user (download / broadcast / send) |
| 4 | User | Fetch public key; verify signature and content (API or own code) |
