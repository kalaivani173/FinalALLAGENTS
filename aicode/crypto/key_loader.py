from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.backends import default_backend


def load_private_key():
    """Load NPCI private key from PEM file; returns a key object for signing."""
    with open("keys/npci_private.pem", "rb") as f:
        pem_bytes = f.read()
    return load_pem_private_key(pem_bytes, password=None, backend=default_backend())


def load_public_key():
    """Load NPCI public key from PEM file; returns a key object for signature verification."""
    with open("keys/npci_public.pem", "rb") as f:
        pem_bytes = f.read()
    return load_pem_public_key(pem_bytes, backend=default_backend())
