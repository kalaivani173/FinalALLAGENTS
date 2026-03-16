import base64
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def _canonicalize(payload: dict) -> bytes:
    """Same canonical form used for signing and verification."""
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def sign_payload(payload: dict, private_key) -> bytes:
    """Sign a manifest/payload dict; returns raw signature bytes."""
    payload_bytes = _canonicalize(payload)
    return private_key.sign(
        payload_bytes,
        padding.PKCS1v15(),
        hashes.SHA256(),
    )


def verify_signature(payload: dict, signature_b64: str, public_key) -> bool:
    """
    Verify that signature_b64 (base64) is a valid signature of payload with public_key.
    payload must be the same dict that was signed (e.g. the "manifest" object).
    Returns True if valid, False if invalid or malformed.
    """
    try:
        payload_bytes = _canonicalize(payload)
        signature_bytes = base64.b64decode(signature_b64)
        public_key.verify(
            signature_bytes,
            payload_bytes,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False
