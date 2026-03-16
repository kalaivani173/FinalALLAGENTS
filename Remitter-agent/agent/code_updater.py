from pathlib import Path
from agent.repo_scanner import scan_repo
from agent.vector_index import build_index
from agent.retriever import retrieve
from agent.llm_chain import generate_patch
from agent.patch_applier import apply_diff_to_dir
from config import REPO_PATH, ARTIFACTS_PATH, PATCH_FILENAME

_DOCS = None
_VECTOR_STORE = None

def _get_vector_store():
    global _DOCS, _VECTOR_STORE
    if _VECTOR_STORE is None:
        _DOCS = scan_repo(REPO_PATH)
        _VECTOR_STORE = build_index(_DOCS)
    return _DOCS, _VECTOR_STORE

def apply_code(manifest: dict) -> str:
    """Apply manifest change to Remitter Bank local repo. Returns patch content (also written to remitter.patch). No git required."""
    cid = manifest["changeId"]
    path = ARTIFACTS_PATH / cid
    path.mkdir(parents=True, exist_ok=True)
    patch_file = path / PATCH_FILENAME

    if not REPO_PATH.exists():
        placeholder = f"# Change {cid}\n# Place Remitter Bank repo at {REPO_PATH} and re-run.\n"
        patch_file.write_text(placeholder, encoding="utf-8", errors="replace")
        return placeholder

    docs, vector_store = _get_vector_store()
    if not docs:
        placeholder = f"# Change {cid}\n# No Java/XSD files in {REPO_PATH}. Add Remitter Bank code and re-run.\n"
        patch_file.write_text(placeholder, encoding="utf-8", errors="replace")
        return placeholder

    try:
        retrieved = retrieve(vector_store, manifest)
        diff = generate_patch(manifest, retrieved)
    except (KeyError, Exception) as e:
        placeholder = f"# Change {cid}\n# Patch generation failed: {e}\n"
        patch_file.write_text(placeholder, encoding="utf-8", errors="replace")
        return placeholder

    patch_file.write_text(diff, encoding="utf-8", errors="replace")

    try:
        modified = apply_diff_to_dir(diff, REPO_PATH)
        if modified:
            (path / "applied_files.txt").write_text("\n".join(modified), encoding="utf-8")
    except Exception:
        # Patch did not apply cleanly; diff is saved for manual review
        pass
    return diff
