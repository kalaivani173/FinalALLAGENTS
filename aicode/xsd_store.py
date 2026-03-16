import os

# Absolute path so XSD is always under project root (same as storage.py)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_XSD_DIR = os.path.join(_SCRIPT_DIR, "artifacts", "xsd")


def store_xsd(change_id: str, api_name: str, xsd_content: str) -> str:
    """
    Stores XSD as:
    <project_root>/artifacts/xsd/<changeId>/<apiName>.xsd
    """

    target_dir = os.path.join(BASE_XSD_DIR, change_id)
    os.makedirs(target_dir, exist_ok=True)

    path = os.path.join(target_dir, f"{api_name}.xsd")

    with open(path, "w", encoding="utf-8") as f:
        f.write(xsd_content)

    return path
