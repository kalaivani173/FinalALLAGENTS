import base64
import json
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# NPCI Switch uses this canonical form (must match npci-switch-agent aicode/crypto/signing.py)
def _npci_canonical(payload: dict) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _load_public_key(public_key_path: str):
    key_path = Path(public_key_path)
    if not key_path.is_absolute():
        key_path = (Path(__file__).resolve().parent.parent / key_path).resolve()
    if not key_path.exists():
        raise FileNotFoundError(
            f"NPCI public key not found at {key_path}. "
            "Place npci_public.pem in project root or set NPCI_PUBLIC_KEY."
        )
    return serialization.load_pem_public_key(key_path.read_bytes())


def verify_signature_npci(manifest: dict, signature_b64: str, public_key_path: str) -> None:
    """Verify NPCI-style signature: base64, canonical json with separators=(',', ':')."""
    payload = _npci_canonical(manifest)
    signature = base64.b64decode(signature_b64)
    public_key = _load_public_key(public_key_path)
    public_key.verify(signature, payload, padding.PKCS1v15(), hashes.SHA256())


def verify_signature(manifest: dict, public_key_path: str) -> None:
    """
    Verify manifest signature. Supports:
    1. Flat manifest with "signature" as hex (legacy).
    2. Use verify_signature_npci when caller passes envelope { manifest, signature: { value } }.
    """
    # Legacy: signature inside manifest as hex
    sig_hex = manifest.get("signature")
    if isinstance(sig_hex, str) and sig_hex and " " not in sig_hex:
        payload_manifest = {k: v for k, v in manifest.items() if k != "signature"}
        payload = json.dumps(payload_manifest, sort_keys=True).encode()
        signature = bytes.fromhex(sig_hex)
        public_key = _load_public_key(public_key_path)
        public_key.verify(signature, payload, padding.PKCS1v15(), hashes.SHA256())
        return

    raise ValueError("Missing or unsupported signature in manifest")
