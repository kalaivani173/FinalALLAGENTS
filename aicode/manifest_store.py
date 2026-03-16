import json, os

BASE_DIR = "artifacts/manifests"

def save_signed_manifest(change_id: str, signed_manifest: dict) -> str:
    os.makedirs(BASE_DIR, exist_ok=True)
    path = os.path.join(BASE_DIR, f"{change_id}.json")

    with open(path, "w") as f:
        json.dump(signed_manifest, f, indent=2)

    return path
