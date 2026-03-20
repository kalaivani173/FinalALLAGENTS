import base64
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load .env first so OPENAI_API_KEY is set before agent/rag imports
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import FileResponse, PlainTextResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, AliasChoices

from models import ChangeRequest
from agent import generate_spec, approve_spec, generate_patch_after_approval, developer_approve_spec
from agent import CHANGE_STORE as AGENT_CHANGE_STORE
from patch_generator import sanitize_java_dto_code
from storage import save_artifact
from partner_registry import load_partners
from manifest_dispatcher import send_manifest
from manifest import create_partner_manifest
from manifest_store import save_signed_manifest
from paths import xsd_web_path, xsd_web_url, openapi_web_url, openapi_ui_url, product_note_web_url
from deploy_config import get_javacoderepo_root, DEPLOY_DRY_RUN
from deploy import (
    deploy_files,
    deploy_dry_run,
    git_commit_and_push,
    write_deploy_audit,
    DEPLOY_ALLOWED_CHANGE_TYPE,
)
from openapi_generator import write_openapi_spec
from product_note_generator import generate_product_note
from rag_xsd_generator import load_samples
from xml.etree import ElementTree as ET

# Product Kit Generator router
try:
    from product_kit_router import router as product_kit_router
    _PKG_AVAILABLE = True
except Exception as _pkg_err:
    product_kit_router = None
    _PKG_AVAILABLE = False
    print(f"[WARN] Product Kit Generator unavailable: {_pkg_err}")


try:
    from crypto.signing import sign_payload, verify_signature
    from crypto.key_loader import load_private_key, load_public_key
    _MANIFEST_SIGNING_AVAILABLE = True
except ImportError:
    _MANIFEST_SIGNING_AVAILABLE = False
    sign_payload = verify_signature = load_public_key = None

app = FastAPI(title="NPCI AI Agent")

# ---- CORS: allow chatbot UI on port 5500 (and any origin in dev) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Product Kit Generator router ----
if _PKG_AVAILABLE and product_kit_router:
    app.include_router(product_kit_router)

# ---- Change request store (for Developer dashboard; survives across Product submit) ----
class ChangeRequestRecord(BaseModel):
    changeId: str
    description: Optional[str] = None
    productNoteSummary: Optional[str] = None
    changeType: Optional[str] = None
    apiName: Optional[str] = None
    currentStatus: Optional[str] = None
    receivedDate: Optional[str] = None
    updatedOn: Optional[str] = None
    reviewComments: Optional[str] = None

CHANGE_REQUESTS_FILE = os.path.join(os.path.dirname(__file__), "artifacts", "change_requests.json")
CHANGE_REQUESTS_STORE: dict[str, dict] = {}


def _load_change_requests_store() -> None:
    """Load change requests from file so the list is maintained across restarts."""
    if not os.path.isfile(CHANGE_REQUESTS_FILE):
        return
    try:
        with open(CHANGE_REQUESTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            CHANGE_REQUESTS_STORE.update(data)
    except Exception:
        pass


def _save_change_requests_store() -> None:
    """Persist change requests to file."""
    os.makedirs(os.path.dirname(CHANGE_REQUESTS_FILE), exist_ok=True)
    with open(CHANGE_REQUESTS_FILE, "w", encoding="utf-8") as f:
        json.dump(CHANGE_REQUESTS_STORE, f, indent=2)


_load_change_requests_store()


# ---- Orchestrator: track when external parties action on our manifest ----
# We share the manifest with other parties (Payer, Payee, Banks) via our APIs.
# When they action upon receiving it, they call POST /orchestrator/a2a/status to report their status.
# This state is only populated by those external parties; we do not track internal Developer/Product here.
ORCHESTRATOR_STATE_FILE = os.path.join(os.path.dirname(__file__), "artifacts", "orchestrator_state.json")
ORCHESTRATOR_STATE: dict[str, dict[str, str]] = {}


def _load_orchestrator_state() -> None:
    if not os.path.isfile(ORCHESTRATOR_STATE_FILE):
        _save_orchestrator_state()  # create file with {} so it can be located in artifacts/
        return
    try:
        with open(ORCHESTRATOR_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            ORCHESTRATOR_STATE.update(data)
    except Exception:
        pass


def _save_orchestrator_state() -> None:
    os.makedirs(os.path.dirname(ORCHESTRATOR_STATE_FILE), exist_ok=True)
    with open(ORCHESTRATOR_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(ORCHESTRATOR_STATE, f, indent=2)


def _orchestrator_record(change_id: str, agent: str, status: str) -> None:
    """Record that an external party (Payer, Payee, Bank, etc.) has reported status for a change."""
    ORCHESTRATOR_STATE.setdefault(change_id, {})[agent] = status
    _save_orchestrator_state()


_load_orchestrator_state()


# ---- Manifest delivery: which CR was sent to which partner and result (persisted so Publish tab survives refresh) ----
# Shape: { partnerId: { changeId: { "statusCode": int, "response": str } } }
MANIFEST_DELIVERY_FILE = os.path.join(os.path.dirname(__file__), "artifacts", "manifest_delivery.json")
MANIFEST_DELIVERY_STATE: dict[str, dict[str, dict]] = {}


def _load_manifest_delivery() -> None:
    if not os.path.isfile(MANIFEST_DELIVERY_FILE):
        return
    try:
        with open(MANIFEST_DELIVERY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            MANIFEST_DELIVERY_STATE.update(data)
    except Exception:
        pass


def _save_manifest_delivery() -> None:
    os.makedirs(os.path.dirname(MANIFEST_DELIVERY_FILE), exist_ok=True)
    with open(MANIFEST_DELIVERY_FILE, "w", encoding="utf-8") as f:
        json.dump(MANIFEST_DELIVERY_STATE, f, indent=2)


def _delivery_record(partner_id: str, change_id: str, status_code: int, response: str) -> None:
    """Record that a manifest for change_id was sent to partner_id with given result."""
    MANIFEST_DELIVERY_STATE.setdefault(partner_id, {})[change_id] = {
        "statusCode": status_code,
        "response": str(response) if response is not None else "",
    }
    _save_manifest_delivery()


_load_manifest_delivery()


@app.post("/agent/artifact/upload")
async def upload_artifact(
    changeId: str = Form(...),
    artifactType: str = Form(...),
    file: UploadFile = File(...),
    apiName: Optional[str] = Form(None),
):
    api_name = (apiName or "").strip() or None
    try:
        path = save_artifact(changeId, artifactType, file, api_name)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except (OSError, RuntimeError) as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    return {
        "status": "UPLOADED",
        "changeId": changeId,
        "artifactType": artifactType,
        "path": path,
    }


def _strip_xml_ns(tag: str) -> str:
    """Return localname for tags like '{ns}ReqPay'."""
    if not tag:
        return ""
    if tag[0] == "{":
        return tag.split("}", 1)[1]
    return tag


def _xml_sample_to_xsd(xml_bytes: bytes) -> str:
    """
    Best-effort conversion of a sample XML document into an XSD.
    This is intentionally conservative and uses xs:string for leaf values.
    """
    if not xml_bytes:
        raise ValueError("Empty XML")

    try:
        root = ET.fromstring(xml_bytes)
    except Exception as e:
        raise ValueError(f"Invalid XML: {e}")

    XS_NS = "http://www.w3.org/2001/XMLSchema"
    ET.register_namespace("xs", XS_NS)
    xs = f"{{{XS_NS}}}"

    schema = ET.Element(xs + "schema", attrib={"elementFormDefault": "qualified"})

    def build(xsd_element: ET.Element, xml_node: ET.Element) -> None:
        children = [c for c in list(xml_node) if isinstance(c.tag, str)]
        attrs = dict(xml_node.attrib or {})

        # Determine if complex
        if children or attrs:
            ct = ET.SubElement(xsd_element, xs + "complexType")
            if children:
                seq = ET.SubElement(ct, xs + "sequence")
                # Preserve first-seen order of tags, and use maxOccurs=unbounded for repeats.
                seen_order: list[str] = []
                counts: dict[str, int] = {}
                first_child_by_tag: dict[str, ET.Element] = {}
                for ch in children:
                    t = _strip_xml_ns(ch.tag)
                    if t not in counts:
                        seen_order.append(t)
                        first_child_by_tag[t] = ch
                        counts[t] = 0
                    counts[t] += 1
                for t in seen_order:
                    child_xsd = ET.SubElement(
                        seq,
                        xs + "element",
                        attrib={
                            "name": t,
                            "minOccurs": "0",
                            "maxOccurs": "unbounded" if (counts.get(t, 0) > 1) else "1",
                        },
                    )
                    build(child_xsd, first_child_by_tag[t])
            for a in attrs.keys():
                if not a:
                    continue
                ET.SubElement(
                    ct,
                    xs + "attribute",
                    attrib={
                        "name": a,
                        "type": "xs:string",
                        "use": "optional",
                    },
                )
        else:
            # Leaf value
            xsd_element.set("type", "xs:string")

    root_name = _strip_xml_ns(root.tag) or "Root"
    root_el = ET.SubElement(schema, xs + "element", attrib={"name": root_name})
    build(root_el, root)

    xml_out = ET.tostring(schema, encoding="utf-8", xml_declaration=True)
    return xml_out.decode("utf-8")


@app.post("/agent/xsd/convert-sample-xml")
async def convert_sample_xml_to_xsd(file: UploadFile = File(...)):
    """Convert an uploaded sample XML into an XSD for Field Addition UI."""
    content = await file.read()
    try:
        xsd = _xml_sample_to_xsd(content)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert XML to XSD: {e}")
    return {"xsd": xsd}


@app.post("/npciswitch/spec/generate")
def spec_generate(payload: ChangeRequest):
    return generate_spec(payload.model_dump())


@app.post("/npciswitch/spec/approve/{changeId}")
def spec_approve(changeId: str):
    return approve_spec(changeId)


@app.post("/npciswitch/spec/devapprove/{changeId}")
def spec_developer_approve(changeId: str):
    return developer_approve_spec(changeId)


@app.get("/npciswitch/dev/patch/{changeId}")
def dev_patch(changeId: str):
    """Return generated code patch (Java diffs) for the change after spec is approved.
    On success, caches the result in CHANGE_REQUESTS_STORE so GET change-requests/{changeId}
    returns files and Developer 'View code' is instant on next open."""
    try:
        result = generate_patch_after_approval(changeId)
    except Exception as e:
        err_msg = str(e)
        raise HTTPException(
            status_code=500,
            detail=f"Patch generation failed: {err_msg}. Common causes: Java codebase path missing (see agent.py JAVA_CODEBASE_PATH), OPENAI_API_KEY not set, or XSD parse error.",
        )
    if "error" not in result and "results" in result and changeId in CHANGE_REQUESTS_STORE:
        files = []
        for r in result["results"]:
            new_code = (r.get("newCode") or r.get("diff")) or ""
            if new_code and "private " in new_code:
                new_code = sanitize_java_dto_code(new_code)
            files.append({
                "fileName": r.get("file") or "file",
                "filePath": r.get("file") or "file",
                "oldCode": r.get("oldCode") or "",
                "newCode": new_code,
                "diff": r.get("diff") or "",
            })
        CHANGE_REQUESTS_STORE[changeId]["files"] = files
        _save_change_requests_store()
    return result


@app.get("/npciswitch/change-requests")
def list_change_requests():
    """List all change requests (for Developer dashboard)."""
    items = list(CHANGE_REQUESTS_STORE.values())
    items.sort(key=lambda x: (x.get("updatedOn") or x.get("receivedDate") or ""), reverse=True)
    return {"data": items}


@app.post("/npciswitch/change-requests/clear")
def clear_change_requests():
    """Clear all change requests from the store (Change Management / Change Requests list)."""
    CHANGE_REQUESTS_STORE.clear()
    _save_change_requests_store()
    return {"success": True, "message": "All change requests cleared."}


@app.delete("/npciswitch/change-requests/{changeId}")
def delete_change_request(changeId: str):
    """Delete one change request by id."""
    if changeId not in CHANGE_REQUESTS_STORE:
        raise HTTPException(status_code=404, detail="Change request not found")
    CHANGE_REQUESTS_STORE.pop(changeId, None)
    _save_change_requests_store()
    return {"success": True, "changeId": changeId}


@app.get("/npciswitch/change-requests/{changeId}")
def get_change_request(changeId: str):
    """Get one change request by id. Sanitizes stored files' newCode to remove duplicate fields."""
    if changeId not in CHANGE_REQUESTS_STORE:
        raise HTTPException(status_code=404, detail="Change request not found")
    cr = dict(CHANGE_REQUESTS_STORE[changeId])
    files = cr.get("files") or []
    if files:
        sanitized = []
        for f in files:
            fc = dict(f)
            new_code = (fc.get("newCode") or "").strip()
            if new_code and "private " in new_code:
                fc["newCode"] = sanitize_java_dto_code(new_code)
            sanitized.append(fc)
        cr["files"] = sanitized
    return {"data": cr}


@app.post("/npciswitch/change-requests")
def save_change_request(payload: ChangeRequestRecord):
    """Create or update a change request (called after Product submits for approval)."""
    change_id = payload.changeId
    data = payload.model_dump(exclude_unset=True)
    if change_id in CHANGE_REQUESTS_STORE:
        CHANGE_REQUESTS_STORE[change_id].update(data)
    else:
        CHANGE_REQUESTS_STORE[change_id] = data
    _save_change_requests_store()
    return {"data": CHANGE_REQUESTS_STORE[change_id]}


@app.patch("/npciswitch/change-requests/{changeId}")
def update_change_request_status(changeId: str, payload: dict):
    """Update status/review comments (e.g. Developer approve/reject)."""
    if changeId not in CHANGE_REQUESTS_STORE:
        raise HTTPException(status_code=404, detail="Change request not found")
    new_status = None
    if "currentStatus" in payload:
        new_status = payload["currentStatus"]
        CHANGE_REQUESTS_STORE[changeId]["currentStatus"] = new_status
    if "reviewComments" in payload:
        CHANGE_REQUESTS_STORE[changeId]["reviewComments"] = payload["reviewComments"]
    CHANGE_REQUESTS_STORE[changeId]["updatedOn"] = datetime.now().isoformat()
    _save_change_requests_store()

    # If Developer marked this CR as Approved, ensure a signed manifest exists
    # so the UI can download/broadcast it immediately.
    manifest_info = None
    if isinstance(new_status, str) and new_status.strip().lower() == "approved":
        try:
            manifest_res = create_and_store_manifest(changeId)
            manifest_info = {"created": True, "path": manifest_res.get("path")}
        except Exception as e:
            # Don't block the status update (keep existing journey),
            # but surface the issue to the caller.
            manifest_info = {"created": False, "error": str(e)}

    return {"data": CHANGE_REQUESTS_STORE[changeId], "manifest": manifest_info}


# ---- Deploy to javacoderepo (Field Addition only) ----
@app.get("/npciswitch/deploy/eligibility/{changeId}")
def deploy_eligibility(changeId: str):
    """
    Whether this CR can be deployed to javacoderepo.
    Field Addition CRs are eligible when the developer has approved the code changes (status = Approved).
    No requirement for agents to be READY. Git behavior is controlled by env (DEPLOY_GIT_*) and does not affect eligibility.
    """
    if changeId not in CHANGE_REQUESTS_STORE:
        raise HTTPException(status_code=404, detail="Change request not found")
    cr = CHANGE_REQUESTS_STORE[changeId]
    change_type = (cr.get("changeType") or "").strip().lower()
    if change_type != DEPLOY_ALLOWED_CHANGE_TYPE:
        return {
            "eligible": False,
            "reason": f"Deploy is only supported for change type '{DEPLOY_ALLOWED_CHANGE_TYPE}', not '{change_type}'",
            "crStatus": cr.get("currentStatus"),
            "changeType": change_type,
        }
    status = (cr.get("currentStatus") or "").strip()
    if status.lower() != "approved":
        return {
            "eligible": False,
            "reason": "CR is not Approved (developer must approve code changes first)",
            "crStatus": status,
            "changeType": change_type,
        }
    return {
        "eligible": True,
        "reason": None,
        "crStatus": status,
        "changeType": change_type,
    }


@app.post("/npciswitch/deploy/{changeId}")
def deploy_to_javacoderepo(changeId: str, dryRun: bool = False):
    """
    Deploy approved code (Field Addition only) to javacoderepo.
    Existing files are renamed to *_old.* before writing.

    Response: success, changeId, deployedFiles, errors, javacoderepoRoot.
    When success: gitCommitPush { ok, message, branch?, remote?, commitHash?, pushed?, errorCode? }; optional warning if push failed.
    Dry-run (dryRun=true or DEPLOY_DRY_RUN=1): dryRun: true, wouldDeploy: [ { targetPath, wouldBackup } ], no writes or Git.
    """
    if changeId not in CHANGE_REQUESTS_STORE:
        raise HTTPException(status_code=404, detail="Change request not found")
    cr = CHANGE_REQUESTS_STORE[changeId]
    change_type = (cr.get("changeType") or "").strip().lower()
    if change_type != DEPLOY_ALLOWED_CHANGE_TYPE:
        raise HTTPException(
            status_code=400,
            detail=f"Deploy is only supported for change type '{DEPLOY_ALLOWED_CHANGE_TYPE}', not '{change_type}'",
        )
    status = (cr.get("currentStatus") or "").strip().lower()
    if status != "approved":
        raise HTTPException(
            status_code=400,
            detail="CR must be Approved by developer to deploy (already deployed CRs cannot be re-deployed via this endpoint)",
        )
    files = cr.get("files") or []
    if not files:
        raise HTTPException(status_code=400, detail="No approved files to deploy (run View code and Approve first)")

    if (cr.get("currentStatus") or "").strip().lower() == "deployed":
        raise HTTPException(status_code=409, detail="Change already deployed")

    javacoderepo_root = get_javacoderepo_root()

    if dryRun or DEPLOY_DRY_RUN:
        would_deploy, errors = deploy_dry_run(files, javacoderepo_root)
        return {
            "dryRun": True,
            "changeId": changeId,
            "wouldDeploy": would_deploy,
            "errors": errors,
            "javacoderepoRoot": javacoderepo_root,
        }

    deployed, errors = deploy_files(files, javacoderepo_root)
    success = len(errors) == 0
    git_result = None
    if success:
        git_result = git_commit_and_push(javacoderepo_root, changeId, deployed)
        write_deploy_audit(
            changeId,
            [e.get("targetPath") for e in deployed if e.get("targetPath")],
            git_result if isinstance(git_result, dict) else {"ok": True, "message": str(git_result), "pushed": False},
        )
        CHANGE_REQUESTS_STORE[changeId]["currentStatus"] = "Deployed"
        CHANGE_REQUESTS_STORE[changeId]["updatedOn"] = datetime.now().isoformat()
        _save_change_requests_store()
    out = {
        "success": success,
        "changeId": changeId,
        "deployedFiles": deployed,
        "errors": errors,
        "javacoderepoRoot": javacoderepo_root,
    }
    if success:
        out["gitCommitPush"] = git_result
        if isinstance(git_result, dict) and not git_result.get("ok"):
            out["warning"] = "Deploy succeeded but Git push failed; push manually if needed."
    return out


# ---- Orchestrator endpoints: parties report when they have actioned on our manifest ----
class OrchestratorPartyStatus(str, Enum):
    """Allowed status values when a party updates us after receiving our manifest."""
    RECEIVED = "RECEIVED"
    APPLIED = "APPLIED"
    TESTED = "TESTED"
    TESTS_READY = "TESTS_READY"  # used by external apps when tests are ready
    READY = "READY"


class OrchestratorA2AStatus(BaseModel):
    """Body: changeId (or change_id), agent (optional, default Payer), status or state. status: RECEIVED | APPLIED | TESTED | READY."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    changeId: Optional[str] = Field(None, validation_alias=AliasChoices("change_id", "changeId"))
    agent: Optional[str] = None  # default "Payer" when missing for backward compatibility with payer /agent/status/.../approve
    status: Optional[str] = Field(None, validation_alias=AliasChoices("status", "state"))


def _normalize_orchestrator_status(s: str) -> str:
    """Accept RECEIVED/APPLIED/TESTED/READY in any case; return canonical value or raise."""
    u = (s or "").strip().upper()
    for e in OrchestratorPartyStatus:
        if e.value == u:
            return e.value
    allowed = [e.value for e in OrchestratorPartyStatus]
    raise HTTPException(status_code=422, detail=f"status must be one of: {allowed}")


@app.post("/orchestrator/a2a/status")
def receive_a2a_status(body: dict = Body(...)):
    """
    Receive status from a party (Payer, Payee, Bank, etc.) that we shared the manifest with.
    Body (JSON): { "changeId": "CHG-624", "agent": "Payer", "status": "RECEIVED" }
    or snake_case: { "change_id": "CHG-624", "agent": "Payer", "status": "RECEIVED" }.
    status: RECEIVED | APPLIED | TESTED | READY (case-insensitive).
    """
    if not isinstance(body, dict):
        raise HTTPException(
            status_code=422,
            detail="Body must be a JSON object with changeId (or change_id) and status (or state)",
        )
    change_id = (body.get("changeId") or body.get("change_id") or "").strip()
    agent = (body.get("agent") or "").strip() or "Payer"
    status_val = (body.get("status") or body.get("state") or "").strip()
    if not change_id:
        raise HTTPException(
            status_code=422,
            detail="changeId (or change_id) is required and must be non-empty",
        )
    if not status_val:
        raise HTTPException(status_code=422, detail="status (or state) is required")
    status = _normalize_orchestrator_status(status_val)
    _orchestrator_record(change_id, agent, status)
    return {"ack": "RECEIVED"}


@app.get("/orchestrator/change/{change_id}")
def get_change_status(change_id: str):
    """View which parties have reported status for this change (after receiving/actioning our manifest)."""
    return {
        "changeId": change_id,
        "agents": ORCHESTRATOR_STATE.get(change_id, {}),
    }


@app.get("/orchestrator/status")
def get_orchestrator_status():
    """
    Return full orchestration state for the frontend: all change IDs and each party's status.
    Response: { "CHG-624": { "Payer": "RECEIVED", "Bank_A": "TESTED" }, ... }
    """
    return ORCHESTRATOR_STATE


# ------------------------------------------------
# Manifest endpoints (from main_new merge)
# ------------------------------------------------

def _partner_id_to_agent_name(partner_id: str) -> str:
    """Map partner IDs to user-friendly orchestrator agent names."""
    pid = (partner_id or "").strip().upper()
    return {
        # Use canonical party keys so later updates (APPLIED/TESTED/READY) naturally overwrite.
        # Downgrades are prevented in _record_delivery_as_orchestrator_status.
        "PAYER_AGENT": "Payer",
        "PAYEE_AGENT": "Payee",
        "REMITTER_AGENT": "Remitter",
        "BENEFICIARY_AGENT": "Beneficiary",
    }.get(pid, partner_id or "Partner")


def _record_delivery_as_orchestrator_status(change_id: str, partner_id: str, status_code: int, response_text: str) -> None:
    """
    Demo-friendly behavior:
    - When we successfully POST a manifest to a partner, record RECEIVED in orchestrator state.
    - If partner returns JSON with {status/state}, prefer that.
    This keeps the Status Center aligned with the "manifest sent" reality without requiring
    every external agent to explicitly call /orchestrator/a2a/status.
    """
    try:
        if int(status_code or 0) != 200:
            return
    except Exception:
        return

    agent_name = _partner_id_to_agent_name(partner_id)
    status = "RECEIVED"
    try:
        if response_text:
            parsed = json.loads(response_text)
            if isinstance(parsed, dict):
                status_val = parsed.get("status") or parsed.get("state")
                if isinstance(status_val, str) and status_val.strip():
                    status = _normalize_orchestrator_status(status_val)
    except Exception:
        # Ignore parsing/normalization issues and fall back to RECEIVED.
        status = "RECEIVED"

    # Never downgrade an existing status (e.g. APPLIED -> RECEIVED).
    try:
        order = {"RECEIVED": 1, "APPLIED": 2, "TESTED": 3, "TESTS_READY": 4, "READY": 5}
        prev = ORCHESTRATOR_STATE.get(change_id, {}).get(agent_name)
        if prev and order.get(str(prev).upper(), 0) > order.get(str(status).upper(), 0):
            return
    except Exception:
        pass

    _orchestrator_record(change_id, agent_name, status)


@app.get("/npciswitch/partners")
def list_partners():
    return load_partners()


def _save_partners(data: dict):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "partners.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class PartnerBody(BaseModel):
    partnerId: str
    endpoint: str


@app.post("/npciswitch/partners")
def add_partner(body: PartnerBody):
    partners = load_partners()
    pid = body.partnerId.strip().upper().replace(" ", "_")
    if not pid:
        raise HTTPException(status_code=422, detail="partnerId is required")
    if pid in partners:
        raise HTTPException(status_code=409, detail=f"Partner '{pid}' already exists")
    partners[pid] = {"endpoint": body.endpoint.strip()}
    _save_partners(partners)
    return {"status": "CREATED", "partnerId": pid, "endpoint": body.endpoint.strip()}


@app.patch("/npciswitch/partners/{partnerId}")
def update_partner(partnerId: str, body: PartnerBody):
    partners = load_partners()
    pid = partnerId.strip().upper()
    if pid not in partners:
        raise HTTPException(status_code=404, detail=f"Partner '{pid}' not found")
    partners[pid]["endpoint"] = body.endpoint.strip()
    _save_partners(partners)
    return {"status": "UPDATED", "partnerId": pid, "endpoint": body.endpoint.strip()}


@app.delete("/npciswitch/partners/{partnerId}")
def delete_partner(partnerId: str):
    partners = load_partners()
    pid = partnerId.strip().upper()
    if pid not in partners:
        raise HTTPException(status_code=404, detail=f"Partner '{pid}' not found")
    del partners[pid]
    _save_partners(partners)
    return {"status": "DELETED", "partnerId": pid}


@app.get("/npciswitch/xsd/{changeId}/{filename}")
def get_xsd_file(changeId: str, filename: str):
    """Serve XSD file for same-service hosting. Path in manifest uses xsd_web_path (paths.py)."""
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not filename.endswith(".xsd"):
        filename = f"{filename}.xsd"
    path = os.path.join("artifacts", "xsd", changeId, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="XSD not found")
    return FileResponse(path, media_type="application/xml", filename=filename)


@app.get("/npciswitch/openapi/{changeId}/{filename}")
def get_openapi_file(changeId: str, filename: str):
    """Serve OpenAPI/Swagger spec for same-service hosting."""
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    path = os.path.join("artifacts", "specs", changeId, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="OpenAPI spec not found")

    ext = os.path.splitext(filename.lower())[1]
    media_type = "text/plain"
    if ext in (".yaml", ".yml"):
        media_type = "application/yaml"
    elif ext == ".json":
        media_type = "application/json"

    # Don't force attachment download; let browsers render inline when possible.
    return FileResponse(path, media_type=media_type)


_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.get("/npciswitch/product-note/{changeId}/{filename}")
def get_product_note_file(changeId: str, filename: str):
    """Serve product note document for same-service hosting."""
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    path = os.path.join(_BASE_DIR, "artifacts", "product-notes", changeId, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Product note not found")

    ext = os.path.splitext(filename.lower())[1]
    media_type = "text/plain"
    if ext == ".pdf":
        media_type = "application/pdf"
    elif ext == ".md":
        media_type = "text/markdown"
    elif ext in (".docx", ".doc"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return FileResponse(path, media_type=media_type, filename=filename)


@app.get("/npciswitch/openapi-ui/{changeId}", response_class=HTMLResponse)
def openapi_ui(changeId: str):
    """
    Render Swagger UI for a given changeId.
    Regenerates spec from XSD when available so Swagger reflects XSD structure.
    """
    specs_dir = os.path.join("artifacts", "specs", changeId)
    xsd_dir = os.path.join("artifacts", "xsd", changeId)
    filename = ""

    # Prefer apiName from change request store; else derive from XSD filename.
    api_name = "API"
    xsd_filename = ""
    if os.path.isdir(xsd_dir):
        for f in os.listdir(xsd_dir):
            if f.endswith(".xsd"):
                xsd_filename = f
                if api_name == "API":
                    api_name = f[:-4]  # e.g. ReqPay.xsd -> ReqPay
                break
    if changeId in CHANGE_REQUESTS_STORE:
        stored = (CHANGE_REQUESTS_STORE[changeId].get("apiName") or "").strip()
        if stored:
            api_name = stored

    # When XSD exists, regenerate openapi.json from XSD so Swagger reflects XSD structure.
    if xsd_filename:
        try:
            xsd_url = xsd_web_url(changeId, xsd_filename)
            _base_dir = os.path.dirname(os.path.abspath(__file__))
            write_openapi_spec(
                base_dir=_base_dir,
                change_id=changeId,
                api_name=api_name,
                xsd_url=xsd_url,
            )
            filename = "openapi.json"
        except Exception:
            pass

    if not filename and os.path.isdir(specs_dir):
        preferred = ["openapi.yaml", "openapi.yml", "openapi.json", "swagger.yaml", "swagger.yml", "swagger.json"]
        for name in preferred:
            if os.path.isfile(os.path.join(specs_dir, name)):
                filename = name
                break
        if not filename:
            for f in os.listdir(specs_dir):
                if f.lower().endswith((".yaml", ".yml", ".json")):
                    filename = f
                    break

    if not filename:
        raise HTTPException(status_code=404, detail="No OpenAPI spec found for this changeId")

    spec_url = f"/npciswitch/openapi/{changeId}/{filename}"
    html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Swagger UI - {changeId}</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
    <style>body {{ margin: 0; }}</style>
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
      window.onload = function() {{
        SwaggerUIBundle({{
          url: "{spec_url}",
          dom_id: "#swagger-ui",
          deepLinking: true,
          presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
          layout: "StandaloneLayout"
        }});
      }};
    </script>
  </body>
</html>"""
    return HTMLResponse(content=html)


@app.post("/npciswitch/mock/{changeId}/{apiName}")
async def mock_api(changeId: str, apiName: str, body: bytes = Body(b"")):
    """
    Simple mock endpoint so Swagger UI 'Try it out' has a real backend to call.
    Returns a minimal XML response root derived from apiName.
    """
    api = (apiName or "API").strip() or "API"
    if api.startswith("Req") and len(api) > 3:
        resp_root = "Resp" + api[3:]
    else:
        resp_root = f"{api}Response"
    xml = f"<{resp_root}></{resp_root}>"
    return PlainTextResponse(xml, media_type="application/xml")


@app.post("/npciswitch/manifest/create/{changeId}")
def create_and_store_manifest(changeId: str):
    """Create partner manifest from change request and store it (called when Developer approves code changes)."""
    if changeId not in CHANGE_REQUESTS_STORE:
        raise HTTPException(status_code=404, detail="Change request not found")
    cr = CHANGE_REQUESTS_STORE[changeId]
    # Prefer agent's payload (has fieldAdditions from spec generate) so impactedPaths are correct
    payload = None
    if changeId in AGENT_CHANGE_STORE and isinstance(AGENT_CHANGE_STORE[changeId].get("payload"), dict):
        payload = dict(AGENT_CHANGE_STORE[changeId]["payload"])
        payload["changeId"] = changeId
        payload["description"] = payload.get("description") or cr.get("description")
        payload["productNoteSummary"] = payload.get("productNoteSummary") or cr.get("productNoteSummary")
    if not payload:
        payload = {
            "changeId": changeId,
            "changeType": cr.get("changeType"),
            "apiName": cr.get("apiName"),
            "description": cr.get("description"),
            "productNoteSummary": cr.get("productNoteSummary"),
            "xmlPath": cr.get("xmlPath"),
            "attributeName": cr.get("attributeName"),
            "datatype": cr.get("datatype"),
            "mandatory": cr.get("mandatory"),
            "allowedValues": cr.get("allowedValues"),
        }
    xsd_dir = os.path.join("artifacts", "xsd", changeId)
    xsd_fs_path = ""
    xsd_filename = ""
    if os.path.isdir(xsd_dir):
        for f in os.listdir(xsd_dir):
            if f.endswith(".xsd"):
                xsd_fs_path = os.path.join(xsd_dir, f)
                xsd_filename = f
                break
    if not xsd_fs_path:
        xsd_filename = f"{payload.get('apiName') or 'schema'}.xsd"
        xsd_fs_path = os.path.join(xsd_dir, xsd_filename)
    xsd_path_for_manifest = xsd_web_url(changeId, xsd_filename)

    # Optional: include OpenAPI/Swagger spec in manifest if present under artifacts/specs/<changeId>/.
    # If missing, auto-generate a minimal openapi.json based on the hosted XSD URL.
    openapi_filename = ""
    openapi_dir = os.path.join("artifacts", "specs", changeId)
    if os.path.isdir(openapi_dir):
        preferred = [
            "openapi.yaml",
            "openapi.yml",
            "openapi.json",
            "swagger.yaml",
            "swagger.yml",
            "swagger.json",
        ]
        for name in preferred:
            if os.path.isfile(os.path.join(openapi_dir, name)):
                openapi_filename = name
                break
        if not openapi_filename:
            for f in os.listdir(openapi_dir):
                if f.lower().endswith((".yaml", ".yml", ".json")):
                    openapi_filename = f
                    break

    if not openapi_filename:
        # Auto-generate openapi.json (best-effort; do not fail manifest creation).
        try:
            _base_dir = os.path.dirname(os.path.abspath(__file__))
            api_name_for_openapi = (payload.get("apiName") or "API").strip() or "API"
            write_openapi_spec(
                base_dir=_base_dir,
                change_id=changeId,
                api_name=api_name_for_openapi,
                xsd_url=xsd_path_for_manifest,
            )
            openapi_filename = "openapi.json"
        except Exception:
            openapi_filename = ""

    # Use Swagger UI URL (interactive) instead of raw openapi.json
    openapi_path_for_manifest = openapi_ui_url(changeId) if (openapi_filename or xsd_path_for_manifest) else None

    # Product note: Option A - generate if none exists; else use uploaded file
    product_note_filename = ""
    product_note_dir = os.path.join("artifacts", "product-notes", changeId)
    if os.path.isdir(product_note_dir):
        preferred = ["product_note.pdf", "product_note.md", "product_note.docx"]
        for name in preferred:
            if os.path.isfile(os.path.join(product_note_dir, name)):
                product_note_filename = name
                break
        if not product_note_filename:
            for f in os.listdir(product_note_dir):
                if f.lower().endswith((".pdf", ".md", ".docx")):
                    product_note_filename = f
                    break

    if not product_note_filename:
        # Option A: generate product note via agent
        try:
            xsd_content = None
            if os.path.isfile(xsd_fs_path):
                with open(xsd_fs_path, "r", encoding="utf-8") as f:
                    xsd_content = f.read()
            samples = None
            try:
                samples = load_samples(changeId)
            except Exception:
                pass
            md_content = generate_product_note(changeId, payload, xsd_content, samples)
            os.makedirs(product_note_dir, exist_ok=True)
            product_note_path_fs = os.path.join(product_note_dir, "product_note.md")
            with open(product_note_path_fs, "w", encoding="utf-8") as f:
                f.write(md_content)
            product_note_filename = "product_note.md"
        except Exception:
            pass

    product_note_path_for_manifest = (
        product_note_web_url(changeId, product_note_filename) if product_note_filename else None
    )
    product_note_summary = payload.get("productNoteSummary") or payload.get("description")

    partner_manifest = create_partner_manifest(
        payload,
        xsd_path_for_manifest,
        openapi_path_for_manifest,
        product_note_path=product_note_path_for_manifest,
        product_note_summary=product_note_summary,
    )
    if _MANIFEST_SIGNING_AVAILABLE:
        try:
            signature_bytes = sign_payload(partner_manifest, load_private_key())
            signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")
            signed_manifest = {
                "manifest": partner_manifest,
                "signature": {"algorithm": "RSA-SHA256", "signedBy": "NPCI", "value": signature_b64},
            }
        except Exception:
            signed_manifest = {"manifest": partner_manifest, "signature": None}
    else:
        signed_manifest = {"manifest": partner_manifest, "signature": None}
    path = save_signed_manifest(changeId, signed_manifest)
    return {"status": "CREATED", "changeId": changeId, "path": path}


@app.post("/npciswitch/manifest/upload")
async def upload_manifest(changeId: str = Form(...), file: UploadFile = File(...)):
    """Save uploaded manifest for a change ID (artifacts/manifests/{changeId}.json)."""
    manifest_dir = "artifacts/manifests"
    os.makedirs(manifest_dir, exist_ok=True)
    path = os.path.join(manifest_dir, f"{changeId}.json")
    content = await file.read()
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail=f"Invalid JSON manifest: {e}")
    with open(path, "wb") as f:
        f.write(content)
    return {"status": "UPLOADED", "changeId": changeId, "path": path}


@app.get("/npciswitch/manifest/delivery-status")
def get_manifest_delivery_status():
    """Return persisted delivery status: { partnerId: { changeId: { statusCode, response } } }. Used so Publish tab survives refresh."""
    return MANIFEST_DELIVERY_STATE


@app.get("/npciswitch/manifest/{changeId}")
def get_signed_manifest(changeId: str):
    path = f"artifacts/manifests/{changeId}.json"
    if not os.path.exists(path):
        return {"error": "MANIFEST_NOT_FOUND"}
    with open(path) as f:
        return json.load(f)


@app.get("/npciswitch/manifest/{changeId}/download")
def download_manifest(changeId: str):
    """Return manifest file for download (Content-Disposition: attachment)."""
    path = f"artifacts/manifests/{changeId}.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Manifest not found")
    return FileResponse(
        path,
        media_type="application/json",
        filename=f"{changeId}.json",
    )


@app.post("/npciswitch/manifest/broadcast/{changeId}")
def broadcast_manifest(changeId: str):
    path = f"artifacts/manifests/{changeId}.json"
    if not os.path.exists(path):
        return {"error": "MANIFEST_NOT_FOUND"}
    with open(path) as f:
        signed_manifest = json.load(f)
    partners = load_partners()
    report = {}
    for pid, cfg in partners.items():
        try:
            status, msg = send_manifest(cfg["endpoint"], signed_manifest)
            report[pid] = {"statusCode": status, "response": msg}
            _delivery_record(pid, changeId, status, msg)
            _record_delivery_as_orchestrator_status(changeId, pid, status, msg)
        except Exception as e:
            report[pid] = {"statusCode": 0, "response": str(e)}
            _delivery_record(pid, changeId, 0, str(e))
    return {"changeId": changeId, "mode": "BROADCAST", "deliveryReport": report}


@app.post("/npciswitch/manifest/send/{changeId}/{partnerId}")
def send_manifest_to_partner(changeId: str, partnerId: str):
    path = f"artifacts/manifests/{changeId}.json"
    if not os.path.exists(path):
        return {"error": "MANIFEST_NOT_FOUND"}
    partners = load_partners()
    if partnerId not in partners:
        return {"error": "UNKNOWN_PARTNER"}
    with open(path) as f:
        signed_manifest = json.load(f)
    status, msg = send_manifest(partners[partnerId]["endpoint"], signed_manifest)
    _delivery_record(partnerId, changeId, status, msg)
    _record_delivery_as_orchestrator_status(changeId, partnerId, status, msg)
    return {"changeId": changeId, "partnerId": partnerId, "statusCode": status, "response": msg}


# ---- Public key and manifest verification (for users to verify signed manifests) ----
@app.get("/npciswitch/keys/public")
def get_public_key():
    """Return NPCI public key PEM so users can verify manifest signatures."""
    if not _MANIFEST_SIGNING_AVAILABLE or load_public_key is None:
        raise HTTPException(status_code=503, detail="Signing/verification not configured")
    try:
        with open("keys/npci_public.pem", "rb") as f:
            pem = f.read().decode("utf-8")
        return PlainTextResponse(pem, media_type="application/x-pem-file")
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Public key not found. Run: python generate_keys.py",
        )


@app.post("/npciswitch/manifest/verify")
def verify_manifest(signed_manifest: dict):
    """
    Verify a signed manifest. Body: { "manifest": {...}, "signature": { "algorithm", "signedBy", "value": "<base64>" } }.
    Returns verified (signature valid) and contentValid (manifest has required fields).
    """
    if not _MANIFEST_SIGNING_AVAILABLE or verify_signature is None or load_public_key is None:
        return {"verified": False, "contentValid": False, "error": "Verification not configured"}
    manifest = signed_manifest.get("manifest")
    sig = signed_manifest.get("signature")
    if not manifest or not sig or not isinstance(sig.get("value"), str):
        return {"verified": False, "contentValid": False, "error": "Missing manifest or signature.value"}
    try:
        public_key = load_public_key()
        verified = verify_signature(manifest, sig["value"], public_key)
    except Exception as e:
        return {"verified": False, "contentValid": False, "error": str(e)}
    content_valid = bool(
        manifest.get("changeId") and manifest.get("issuer") and manifest.get("timestamp")
    )
    return {"verified": verified, "contentValid": content_valid}


# ---- Serve frontend from same service (port 8000) when frontend/dist exists ----
_FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.isdir(_FRONTEND_DIST):
    _assets_dir = os.path.join(_FRONTEND_DIST, "assets")
    if os.path.isdir(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="frontend_assets")
    _index_path = os.path.join(_FRONTEND_DIST, "index.html")
    if os.path.isfile(_index_path):

        @app.get("/", include_in_schema=False)
        def serve_index():
            return FileResponse(_index_path, media_type="text/html")

        @app.get("/{full_path:path}", include_in_schema=False)
        def serve_spa(full_path: str):
            return FileResponse(_index_path, media_type="text/html")
