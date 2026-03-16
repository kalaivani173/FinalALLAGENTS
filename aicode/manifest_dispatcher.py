import requests

# Timeout for POST to partner (seconds). Increase if partners are slow to respond.
MANIFEST_SEND_TIMEOUT = 15


def send_manifest(endpoint: str, signed_manifest: dict):
    """
    POST signed manifest to partner endpoint. Returns (status_code, message).
    On timeout or connection error, returns (0, error_message) so broadcast can continue.
    """
    try:
        response = requests.post(
            endpoint,
            json=signed_manifest,
            timeout=MANIFEST_SEND_TIMEOUT,
        )
        return response.status_code, response.text
    except requests.exceptions.Timeout as e:
        return 0, f"Timeout after {MANIFEST_SEND_TIMEOUT}s: {e}"
    except requests.exceptions.ConnectionError as e:
        return 0, f"Connection failed (partner may be down): {e}"
    except Exception as e:
        return 0, f"Error: {e}"
