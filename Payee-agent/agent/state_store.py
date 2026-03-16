import json
from datetime import datetime
from pathlib import Path
from config import ARTIFACTS_PATH

def set_state(change_id: str, state: str) -> None:
    path = ARTIFACTS_PATH / change_id
    path.mkdir(parents=True, exist_ok=True)
    data = {"state": state, "updatedAt": datetime.utcnow().isoformat() + "Z"}
    (path / "state.json").write_text(json.dumps(data, indent=2), encoding="utf-8", errors="replace")

def get_state(change_id: str) -> str | None:
    path = ARTIFACTS_PATH / change_id / "state.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return data.get("state")

def get_state_full(change_id: str) -> dict | None:
    path = ARTIFACTS_PATH / change_id / "state.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())
