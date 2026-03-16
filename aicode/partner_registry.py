import json
import os


def load_partners():
    """
    Load partner endpoints from partners.json.

    Use an absolute path relative to this module so uvicorn working directory
    doesn't affect which file is loaded.
    """
    path = os.path.join(os.path.dirname(__file__), "partners.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
