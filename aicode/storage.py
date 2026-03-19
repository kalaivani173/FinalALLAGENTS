import os
import re
from fastapi import UploadFile

# Absolute path so files are always created under project root, not cwd
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_ARTIFACT_DIR = os.path.join(_SCRIPT_DIR, "artifacts")

# Map frontend artifact types to dirs; load_samples() expects "samples"
_TYPE_TO_DIR = {
    "xsd": "xsd",
    "samples": "samples",
    "specs": "specs",
    # OpenAPI/Swagger specs (aliases) -> artifacts/specs/<changeId>/
    "openapi": "specs",
    "swagger": "specs",
    "samplerequests": "samples",
    "existingxsd": "xsd",
    "proposedxsd": "xsd",
    "sampleresponses": "specs",
    "brddocuments": "specs",
    "productnotes": "product-notes",
    "productNotes": "product-notes",
}


def save_artifact(
    change_id: str,
    artifact_type: str,
    file: UploadFile,
    api_name: str | None = None
) -> str:
    """
    Saves uploaded artifacts. Uses absolute path so files are visible under project root.

    XSD rule: stored as <apiName>.xsd
    sampleRequests -> samples/ so agent.load_samples(change_id) finds them.
    """

    key = artifact_type.lower().strip()
    if key not in _TYPE_TO_DIR:
        raise ValueError(
            "Invalid artifact type. Must be one of: "
            + str(list(_TYPE_TO_DIR.keys()))
        )

    dir_name = _TYPE_TO_DIR[key]
    target_dir = os.path.join(BASE_ARTIFACT_DIR, dir_name, change_id)
    os.makedirs(target_dir, exist_ok=True)

    # Read content upfront so XSD uploads can self-derive their api_name
    content = file.file.read()

    if dir_name == "xsd" and key == "xsd":
        if not api_name:
            # Auto-derive api_name from the first xs:element/@name in the XSD,
            # falling back to the uploaded filename stem (without extension).
            m = re.search(rb'<(?:xs:|xsd:)?element\b[^>]+\bname="([^"]+)"', content)
            if m:
                api_name = m.group(1).decode("utf-8", errors="replace").strip()
            if not api_name:
                api_name = os.path.splitext(file.filename or "schema")[0] or "schema"
        filename = f"{api_name}.xsd"
    else:
        filename = file.filename or "uploaded"

    path = os.path.join(target_dir, filename)
    path = os.path.abspath(path)

    with open(path, "wb") as f:
        f.write(content)

    if not os.path.isfile(path):
        raise RuntimeError(f"File write reported success but not found at {path}")

    return path
