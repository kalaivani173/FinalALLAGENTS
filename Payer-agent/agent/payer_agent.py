from datetime import datetime
from agent.signature_verifier import verify_signature
from agent.manifest_validator import validate_manifest
from agent.state_store import set_state
from agent.code_updater import apply_code
from agent.xsd_updater import update_xsd
from agent.test_runner import run_tests
from agent.artifact_store import store
from config import NPCI_PUBLIC_KEY, SKIP_SIGNATURE_VERIFY

async def process_manifest(manifest: dict):
    # Verify only flat manifest with inline signature; envelope is verified in app
    if not SKIP_SIGNATURE_VERIFY and "signature" in manifest:
        verify_signature(manifest, NPCI_PUBLIC_KEY)
    validate_manifest(manifest)

    cid = manifest["changeId"]

    set_state(cid, "RECEIVED")
    set_state(cid, "ACCEPTED")

    patch = apply_code(manifest)
    set_state(cid, "APPLIED")

    xsd = update_xsd(manifest)

    set_state(cid, "TESTED")
    tests = run_tests(cid)

    store(cid, patch, xsd or "", tests, manifest)
    # Leave status as RECEIVED until user approves; then /approve sets APPLIED
    set_state(cid, "RECEIVED")

    return {
        "changeId": cid,
        "agent": "PAYER_PSP",
        "status": "RECEIVED",
        "artifacts": {
            "gitPatch": patch,
            "updatedXsd": xsd,
            "testResults": tests,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
