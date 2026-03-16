import json
from pathlib import Path
from config import ARTIFACTS_PATH

def store(change_id: str, patch: str, xsd: str, tests: str, manifest: dict | None = None) -> None:
    path = ARTIFACTS_PATH / change_id / "artifacts.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"gitPatch": patch, "xsd": xsd, "tests": tests}
    if manifest is not None:
        data["manifest"] = manifest
    path.write_text(json.dumps(data, indent=2), encoding="utf-8", errors="replace")


def save_manifest_only(change_id: str, manifest: dict) -> None:
    """Save manifest when request is only received (state RECEIVED), before generate."""
    path = ARTIFACTS_PATH / change_id / "manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8", errors="replace")


def load_manifest(change_id: str) -> dict | None:
    """Load stored manifest (from manifest.json or artifacts.json). Returns None if not found."""
    base = ARTIFACTS_PATH / change_id
    manifest_path = base / "manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text())
    artifacts_path = base / "artifacts.json"
    if artifacts_path.exists():
        data = json.loads(artifacts_path.read_text())
        return data.get("manifest")
    return None
