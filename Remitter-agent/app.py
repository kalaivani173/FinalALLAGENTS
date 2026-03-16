import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project directory so OPENAI_API_KEY is set regardless of cwd
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

# Ensure OPENAI_API_KEY is in os.environ so LLM/embeddings always see it (e.g. uvicorn workers)
import config as _config
if _config.get_openai_api_key():
    os.environ["OPENAI_API_KEY"] = _config.get_openai_api_key()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from agent.remitter_agent import process_manifest
from agent.state_store import get_state, set_state
from agent.signature_verifier import verify_signature_npci
from agent.manifest_validator import validate_manifest
from agent.artifact_store import save_manifest_only, load_manifest
from config import ARTIFACTS_PATH, REPO_PATH, NPCI_PUBLIC_KEY, SKIP_SIGNATURE_VERIFY, PORT, ORCHESTRATOR_URL, AGENT_NAME, AGENT_ORCHESTRATOR_NAME, PATCH_FILENAME

async def _notify_orchestrator_status(change_id: str, status: str):
    """POST to orchestrator/a2a/status with payload { changeId, agent, status }. Returns (success, error_msg)."""
    import logging
    import httpx
    _log = logging.getLogger(__name__)
    url = f"{ORCHESTRATOR_URL}/orchestrator/a2a/status"
    payload = {"changeId": change_id, "agent": AGENT_ORCHESTRATOR_NAME, "status": status}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(url, json=payload)
            if r.status_code == 422:
                _log.warning("Orchestrator 422 for %s (payload=%s): %s", change_id, payload, r.text)
            r.raise_for_status()
        _log.info("Orchestrator notified: %s -> %s", change_id, status)
        return True, None
    except Exception as e:
        _log.warning("Orchestrator notify failed for %s (payload=%s): %s", change_id, payload, e)
        return False, str(e)

app = FastAPI(
    title="Remitter Bank AI Agent",
    description="Phase 2: AI agent for Remitter Bank – updates debit/CBS integration logic and validators per change.",
)

# CORS for React dev server (e.g. http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175", "http://127.0.0.1:5175", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend: prefer React build (frontend/dist), else static (vanilla)
BASE_DIR = Path(__file__).resolve().parent
REACT_BUILD_DIR = BASE_DIR / "frontend" / "dist"
STATIC_DIR = BASE_DIR / "static"

if REACT_BUILD_DIR.exists() and (REACT_BUILD_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(REACT_BUILD_DIR / "assets")), name="assets")


@app.get("/")
def serve_ui():
    """Serve the Remitter-agent UI (React build if present, else static)."""
    if REACT_BUILD_DIR.exists():
        index_path = REACT_BUILD_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="UI not found")
    return FileResponse(index_path)


if not REACT_BUILD_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

def _extract_manifest(body: dict) -> dict:
    """Accept NPCI envelope { manifest, signature: { value } } or flat manifest."""
    if "manifest" in body:
        return body["manifest"]
    return body

def _verify_signed_envelope(body: dict) -> dict:
    """If body is NPCI envelope, verify and return inner manifest."""
    manifest = _extract_manifest(body)
    if "manifest" not in body:
        return manifest  # flat manifest; verification in payer_agent if needed
    sig = body.get("signature")
    if not sig or not isinstance(sig, dict):
        return manifest
    value = sig.get("value")
    if not value or not isinstance(value, str):
        return manifest
    if not SKIP_SIGNATURE_VERIFY:
        verify_signature_npci(manifest, value, NPCI_PUBLIC_KEY)
    return manifest

@app.get("/health")
def health():
    from config import get_openai_api_key
    key_set = bool(get_openai_api_key())
    return {"status": "ok", "agent": AGENT_NAME, "openai_configured": key_set}

@app.post("/agent/manifest")
async def receive_manifest(body: dict):
    """Receive change manifest: verify signature, validate, store manifest, set status RECEIVED. Does not run code generation."""
    manifest = _verify_signed_envelope(body)
    validate_manifest(manifest)
    cid = manifest["changeId"]
    set_state(cid, "RECEIVED")
    save_manifest_only(cid, manifest)
    return {
        "changeId": cid,
        "agent": AGENT_NAME,
        "status": "RECEIVED",
        "message": "Manifest received. Use Generate to create code changes.",
    }

@app.get("/agent/status")
def list_status():
    """Status board: list all change IDs and their state (RECEIVED → APPLIED → TESTED → READY_FOR_APPROVAL)."""
    if not ARTIFACTS_PATH.exists():
        return {"changes": []}
    changes = []
    for d in ARTIFACTS_PATH.iterdir():
        if d.is_dir():
            state_file = d / "state.json"
            if state_file.exists():
                data = json.loads(state_file.read_text())
                changes.append({
                    "changeId": d.name,
                    "state": data.get("state", "UNKNOWN"),
                    "updatedAt": data.get("updatedAt"),
                })
    changes.sort(key=lambda x: x.get("updatedAt") or "", reverse=True)
    return {"changes": changes}

def _patch_content(change_id: str, git_patch_value: str | None) -> str | None:
    """Return patch content. If git_patch_value is a file path (e.g. .../remitter.patch), read file."""
    if not git_patch_value or not git_patch_value.strip():
        return git_patch_value
    s = git_patch_value.strip()
    if s.endswith(".patch") and (s.find("\\") >= 0 or s.find("/") >= 0):
        path = ARTIFACTS_PATH / change_id / PATCH_FILENAME
        if path.exists():
            return path.read_text(encoding="utf-8", errors="replace")
    return git_patch_value

@app.get("/agent/status/{change_id}")
def get_change_status(change_id: str):
    """Get state, manifest, and artifacts for a single change."""
    from agent.state_store import get_state_full
    state_data = get_state_full(change_id)
    if state_data is None:
        raise HTTPException(status_code=404, detail=f"Change {change_id} not found")
    path = ARTIFACTS_PATH / change_id
    artifacts = None
    if (path / "artifacts.json").exists():
        artifacts = json.loads((path / "artifacts.json").read_text())
    manifest = load_manifest(change_id)
    if manifest is not None and artifacts is not None and "manifest" not in artifacts:
        artifacts = {**(artifacts or {}), "manifest": manifest}
    elif manifest is not None and artifacts is None:
        artifacts = {"manifest": manifest}
    if artifacts and artifacts.get("gitPatch") is not None:
        artifacts = {**artifacts, "gitPatch": _patch_content(change_id, artifacts.get("gitPatch")) or artifacts.get("gitPatch")}
    # Resolve test output: if tests.txt exists, return its content
    tests_file = path / "tests.txt"
    if artifacts is not None and tests_file.exists():
        artifacts = {**artifacts, "tests": tests_file.read_text(encoding="utf-8", errors="replace")}
    return {
        "changeId": change_id,
        "state": state_data.get("state", "UNKNOWN"),
        "updatedAt": state_data.get("updatedAt"),
        "artifacts": artifacts,
    }


@app.post("/agent/status/{change_id}/generate")
async def generate_changes(change_id: str):
    """Run process_manifest for this change (code updates, tests). Status stays RECEIVED until user approves."""
    manifest = load_manifest(change_id)
    if manifest is None:
        raise HTTPException(status_code=404, detail=f"Change {change_id} not found or manifest missing")
    try:
        result = await process_manifest(manifest)
        return result
    except Exception as e:
        err_msg = str(e)
        err_type = type(e).__name__
        if (
            "getaddrinfo failed" in err_msg
            or "ConnectError" in err_type
            or "Connection" in err_msg
            or "APIConnectionError" in err_type
        ):
            raise HTTPException(
                status_code=503,
                detail="OpenAI API unreachable (network/DNS). Check internet and OPENAI_API_KEY in .env.",
            ) from e
        raise HTTPException(status_code=500, detail=err_msg or "Generate failed") from e

@app.post("/agent/status/{change_id}/run-tests")
async def run_tests_endpoint(change_id: str):
    """Only change status from TESTS_READY to TESTED (no Maven run). Used by TEST NOW button. Notifies orchestrator with status TESTED."""
    state = get_state(change_id)
    if state is None:
        raise HTTPException(status_code=404, detail=f"Change {change_id} not found")
    if state != "TESTS_READY":
        raise HTTPException(
            status_code=400,
            detail=f"Status must be TESTS_READY to mark as tested (current: {state})",
        )
    set_state(change_id, "TESTED")
    orchestrator_ok, orchestrator_error = await _notify_orchestrator_status(change_id, "TESTED")
    out = {"changeId": change_id, "state": "TESTED", "message": "Status updated to TESTED.", "orchestratorNotified": orchestrator_ok}
    if orchestrator_error:
        out["orchestratorError"] = orchestrator_error
    return out


@app.post("/agent/status/{change_id}/generate-tests")
async def generate_tests_endpoint(change_id: str):
    """LLM generates unit tests, saves to GeneratedTest.java and tests.txt; set status to TESTS_READY (no Maven run)."""
    if get_state(change_id) is None:
        raise HTTPException(status_code=404, detail=f"Change {change_id} not found")
    manifest = load_manifest(change_id)
    if manifest is None:
        raise HTTPException(status_code=404, detail=f"Change {change_id} not found or manifest missing")

    path_dir = ARTIFACTS_PATH / change_id
    patch_content = ""
    if (path_dir / "artifacts.json").exists():
        art = json.loads((path_dir / "artifacts.json").read_text())
        patch_content = _patch_content(change_id, art.get("gitPatch")) or art.get("gitPatch") or ""
    if not patch_content and (path_dir / PATCH_FILENAME).exists():
        patch_content = (path_dir / PATCH_FILENAME).read_text(encoding="utf-8", errors="replace")

    from agent.test_generator import generate_unit_tests
    try:
        generated_tests = generate_unit_tests(manifest, patch_content or "")
    except Exception as e:
        err_msg = str(e)
        if "OPENAI_API_KEY" in err_msg or "api_key" in err_msg.lower():
            raise HTTPException(status_code=503, detail="OpenAI API key not set or invalid. Check .env") from e
        raise HTTPException(status_code=500, detail=f"Test generation failed: {err_msg}") from e

    path_dir.mkdir(parents=True, exist_ok=True)
    (path_dir / "GeneratedTest.java").write_text(generated_tests, encoding="utf-8", errors="replace")

    tests_content = (
        "=== LLM-generated unit tests (saved to GeneratedTest.java) ===\n\n" + generated_tests
    )
    (path_dir / "tests.txt").write_text(tests_content, encoding="utf-8", errors="replace")

    set_state(change_id, "TESTS_READY")
    orchestrator_notified, orchestrator_error = await _notify_orchestrator_status(change_id, "APPLIED")
    return {
        "changeId": change_id,
        "state": "TESTS_READY",
        "testOutput": tests_content,
        "message": "Unit tests generated. Status set to TESTS_READY. Use TEST NOW to mark as tested.",
        "orchestratorNotified": orchestrator_notified,
        "orchestratorUrl": f"{ORCHESTRATOR_URL}/orchestrator/a2a/status",
        **({"orchestratorError": orchestrator_error} if orchestrator_error else {}),
    }


@app.post("/agent/status/{change_id}/approve")
async def approve_change(change_id: str):
    """Mark a change as APPLIED after user approves the diff. Notifies orchestrator with status READY."""
    if get_state(change_id) is None:
        raise HTTPException(status_code=404, detail=f"Change {change_id} not found")
    set_state(change_id, "APPLIED")
    orchestrator_ok, orchestrator_error = await _notify_orchestrator_status(change_id, "READY")
    out = {"changeId": change_id, "state": "APPLIED", "message": "Status updated to APPLIED", "orchestratorNotified": orchestrator_ok}
    if orchestrator_error:
        out["orchestratorError"] = orchestrator_error
    return out

@app.post("/agent/status/{change_id}/deploy")
def deploy_change(change_id: str):
    """Mark a change as DEPLOYED (status change for UI)."""
    if get_state(change_id) is None:
        raise HTTPException(status_code=404, detail=f"Change {change_id} not found")
    set_state(change_id, "DEPLOYED")
    return {"changeId": change_id, "state": "DEPLOYED", "message": "Status updated to DEPLOYED"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=PORT, reload=True)
