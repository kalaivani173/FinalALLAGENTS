import base64
import os

from rag import validate_with_attachments
from diff_util import generate_diff
from patch_generator import (
    generate_java_patch,
    generate_validator_patch,
    sanitize_java_dto_code,
)
from xsd_transformer import transform_xsd
from rag_xsd_generator import generate_xsd_from_samples, load_samples
from api_builder import build_new_api

from java_index import index_java_codebase
from java_mapper import map_xml_to_java
from mapping_store import get_mapped_class, save_mapping

# 🔹 Deterministic helpers (NO hardcoding)
from xsd_request_extractor import extract_request_blocks
from xsd_attribute_extractor import extract_xsd_attributes
from dto_patch_builder import patch_dto_from_xsd

# 🔹 XSD-driven validation
from xsd_validation_extractor import extract_request_validation_rules
from validation_builder import generate_api_validator

# 🔹 XSD persistence (FIX)
from xsd_store import store_xsd

# 🔹 XSD web path (same-service hosting)
from paths import xsd_web_path, xsd_web_url, openapi_web_url, openapi_ui_url, product_note_web_url
from product_note_generator import generate_product_note
from openapi_generator import write_openapi_spec

# 🔹 Manifest (optional; from agent_new merge)
try:
    from manifest import create_partner_manifest
    from manifest_store import save_signed_manifest
    from crypto.signing import sign_payload
    from crypto.key_loader import load_private_key
    _MANIFEST_AVAILABLE = True
except ImportError:
    _MANIFEST_AVAILABLE = False


# ------------------------------------------------
# CONFIG
# ------------------------------------------------

BASE_XSD_PATH = os.path.join("schemas", "base", "UPI-Payment.xsd")
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _get_java_codebase_path() -> str:
    """JAVA_CODEBASE_PATH from env, or javacoderepo/UPISimnew/src/main/java, or legacy UPIVerse path."""
    path = os.environ.get("JAVA_CODEBASE_PATH", "").strip()
    if path and os.path.isdir(path):
        return os.path.normpath(path)
    # Try javacoderepo (sibling of aicode)
    try:
        from deploy_config import get_javacoderepo_root
        jcr = get_javacoderepo_root()
        # Prefer explicit UPISim path if present
        cand = os.path.join(jcr, "UPISim", "src", "main", "java")
        if os.path.isdir(cand):
            return os.path.normpath(cand)
        # Fallback: support renamed repo folder, e.g. UPISimnew
        cand_new = os.path.join(jcr, "UPISimnew", "src", "main", "java")
        if os.path.isdir(cand_new):
            return os.path.normpath(cand_new)
    except Exception:
        pass
    # Legacy fallback
    legacy_root = os.path.join(_BASE_DIR, "..", "javacoderepo")
    legacy_upisim = os.path.join(legacy_root, "UPISim", "src", "main", "java")
    if os.path.isdir(legacy_upisim):
        return os.path.normpath(legacy_upisim)
    legacy_upisim_new = os.path.join(legacy_root, "UPISimnew", "src", "main", "java")
    return os.path.normpath(legacy_upisim_new) if os.path.isdir(legacy_upisim_new) else os.path.normpath(legacy_upisim)


JAVA_CODEBASE_PATH = _get_java_codebase_path()

# In-memory state (hackathon safe)
CHANGE_STORE = {}


# ------------------------------------------------
# UTIL
# ------------------------------------------------

def load_existing_xsd(change_id: str):
    artifact_dir = os.path.join("artifacts", "xsd", change_id)

    if os.path.exists(artifact_dir):
        for f in os.listdir(artifact_dir):
            if f.endswith(".xsd"):
                path = os.path.join(artifact_dir, f)
                with open(path, "r", encoding="utf-8") as x:
                    return x.read(), path

    with open(BASE_XSD_PATH, "r", encoding="utf-8") as f:
        return f.read(), BASE_XSD_PATH


def _write_baseline_xsd_for_change(change_id: str, api_name: str | None, xsd_text: str) -> str:
    """Persist baseline XSD for this change so transformer can read it from disk."""
    safe_api = (api_name or "schema").strip() or "schema"
    artifact_dir = os.path.join("artifacts", "xsd", change_id)
    os.makedirs(artifact_dir, exist_ok=True)
    path = os.path.join(artifact_dir, f"{safe_api}_baseline.xsd")
    with open(path, "w", encoding="utf-8") as f:
        f.write(xsd_text)
    return path


def should_update_validator(payload: dict) -> bool:
    """
    Legacy behavior (payload-driven validation), extended to support multi-field additions.
    """
    if payload.get("allowedValues"):
        return True
    additions = payload.get("fieldAdditions")
    if isinstance(additions, list):
        for a in additions:
            if isinstance(a, dict) and a.get("allowedValues"):
                # non-empty list/string counts
                if isinstance(a["allowedValues"], list) and len(a["allowedValues"]) > 0:
                    return True
                if isinstance(a["allowedValues"], str) and a["allowedValues"].strip():
                    return True
    return False


def find_java_file(java_index, class_name: str):
    return next((j for j in java_index if j["className"] == class_name), None)


def normalize_api_name(api_name: str) -> str:
    if api_name.startswith("Req"):
        return api_name[3:]
    if api_name.startswith("Resp"):
        return api_name[4:]
    return api_name


def _compute_java_path_from_xml_path(xml_path: str, java_index: list, root_var: str = "reqPay") -> str | None:
    """
    Derive a Java object access path (e.g., reqPay.getPayer().getDevice())
    from an XML path like "ReqPay.Payer.Device" using the same DTO index
    we use for DTO mapping. This keeps validator generation schema-driven
    instead of hardcoding paths.
    """
    if not xml_path:
        return None

    parts = [p for p in xml_path.split(".") if p]
    if len(parts) < 2:
        return None

    root_xml = parts[0]

    # Find the root DTO (e.g., ReqPay) by @XmlRootElement name
    root_candidates = [
        j for j in java_index if root_xml in (j.get("xmlRoot") or [])
    ]
    if not root_candidates:
        return None

    current_dto = root_candidates[0]
    java_path = root_var

    # Walk each subsequent XML segment via field → type mapping
    for element in parts[1:]:
        # Our index maps Java field name -> type. For elements like "Payer",
        # the field is usually "payer".
        field_name = element[0].lower() + element[1:] if element else ""
        field_type = current_dto["fields"].get(field_name)
        if not field_type:
            # Can't resolve this segment; stop and return the path so far.
            break

        # Append getter for this element (e.g., getPayer(), getDevice())
        java_path += f".get{element}()"

        next_dto = next(
            (j for j in java_index if j["className"] == field_type),
            None,
        )
        if not next_dto:
            break

        current_dto = next_dto

    return java_path


def _maybe_create_manifest(change_id: str, payload: dict) -> None:
    """Create and save signed manifest if deps available (from agent_new merge). No-op on failure.
    XSD path is a URL path on the same backend so XSD hosting happens with the backend service."""
    if not _MANIFEST_AVAILABLE:
        return
    try:
        manifest_dir = os.path.join(_BASE_DIR, "artifacts", "manifests")
        os.makedirs(manifest_dir, exist_ok=True)
        xsd_dir = os.path.join(_BASE_DIR, "artifacts", "xsd", change_id)
        xsd_filename = ""
        if os.path.isdir(xsd_dir):
            for f in os.listdir(xsd_dir):
                if f.endswith(".xsd"):
                    xsd_filename = f
                    break
        if not xsd_filename:
            api_name = (payload.get("apiName") or payload.get("api_name") or "schema").strip() or "schema"
            xsd_filename = f"{api_name}.xsd"
        xsd_path_for_manifest = xsd_web_url(change_id, xsd_filename)

        # Optional: include OpenAPI/Swagger spec in manifest if present under artifacts/specs/<changeId>/.
        # If missing, auto-generate a minimal openapi.json based on the hosted XSD URL.
        openapi_filename = ""
        openapi_dir = os.path.join(_BASE_DIR, "artifacts", "specs", change_id)
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
            try:
                api_name_for_openapi = (payload.get("apiName") or payload.get("api_name") or "API").strip() or "API"
                write_openapi_spec(
                    base_dir=_BASE_DIR,
                    change_id=change_id,
                    api_name=api_name_for_openapi,
                    xsd_url=xsd_path_for_manifest,
                )
                openapi_filename = "openapi.json"
            except Exception:
                openapi_filename = ""

        # Use Swagger UI URL (interactive) instead of raw openapi.json
        openapi_path_for_manifest = openapi_ui_url(change_id) if (openapi_filename or xsd_path_for_manifest) else None

        # Product note: Option A - generate if none exists; else use uploaded file
        product_note_filename = ""
        product_note_dir = os.path.join(_BASE_DIR, "artifacts", "product-notes", change_id)
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
            try:
                xsd_content = None
                xsd_fs_path = os.path.join(xsd_dir, xsd_filename)
                if os.path.isfile(xsd_fs_path):
                    with open(xsd_fs_path, "r", encoding="utf-8") as f:
                        xsd_content = f.read()
                samples = None
                try:
                    samples = load_samples(change_id)
                except Exception:
                    pass
                md_content = generate_product_note(change_id, payload, xsd_content, samples)
                os.makedirs(product_note_dir, exist_ok=True)
                with open(os.path.join(product_note_dir, "product_note.md"), "w", encoding="utf-8") as f:
                    f.write(md_content)
                product_note_filename = "product_note.md"
            except Exception:
                pass

        product_note_path_for_manifest = (
            product_note_web_url(change_id, product_note_filename) if product_note_filename else None
        )
        product_note_summary = payload.get("productNoteSummary") or payload.get("description")

        partner_manifest = create_partner_manifest(
            payload,
            xsd_path_for_manifest,
            openapi_path_for_manifest,
            product_note_path=product_note_path_for_manifest,
            product_note_summary=product_note_summary,
        )
        signature_bytes = sign_payload(partner_manifest, load_private_key())
        signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")
        signed_manifest = {
            "manifest": partner_manifest,
            "signature": {
                "algorithm": "RSA-SHA256",
                "signedBy": "NPCI",
                "value": signature_b64,
            },
        }
        save_signed_manifest(change_id, signed_manifest)
    except Exception:
        pass


# ------------------------------------------------
# STEP 1: SPEC GENERATION
# ------------------------------------------------

def generate_spec(payload: dict):
    change_id = payload.get("changeId") or payload.get("change_id")
    change_type = payload.get("changeType") or payload.get("change_type")

    if not change_id or not change_type:
        raise ValueError("changeId and changeType are mandatory")

    # ---------------- NEW API ----------------
    if change_type == "ADD_NEW_API":
        samples = load_samples(change_id)
        old_xsd = None
        new_xsd = generate_xsd_from_samples(
            payload["apiName"],
            samples
        )

    # ---------------- EXISTING API ----------------
    else:
        api_name = payload.get("apiName") or payload.get("api_name")
        baseline = payload.get("xsdContent") or payload.get("baselineXsd") or payload.get("currentXsd")
        if isinstance(baseline, str) and baseline.strip():
            old_xsd = baseline
            xsd_path = _write_baseline_xsd_for_change(change_id, api_name, baseline)
        else:
            old_xsd, xsd_path = load_existing_xsd(change_id)
        new_xsd = transform_xsd(xsd_path, payload)

    # ✅ STORE XSD (THIS WAS MISSING EARLIER)
    api_name = payload.get("apiName")
    if api_name and new_xsd:
        store_xsd(change_id, api_name, new_xsd)

    # Skip slow LLM validation for field-addition; return immediately so XSD appears without delay
    ct = (payload.get("changeType") or payload.get("change_type") or "").strip()
    if ct == "ADD_XML_ATTRIBUTE":
        attachment_notes = {"notes": [], "warnings": []}
    else:
        attachment_notes = validate_with_attachments(
            change_id,
            payload.get("description", "")
        )

    CHANGE_STORE[change_id] = {
        "payload": payload,
        "oldXsd": old_xsd,
        "newXsd": new_xsd,
        "approvalStatus": "PENDING"
    }

    return {
        "changeId": change_id,
        "oldXsd": old_xsd,
        "newXsd": new_xsd,
        "attachmentReview": attachment_notes,
        "approvalStatus": "PENDING"
    }


# ------------------------------------------------
# STEP 2: APPROVAL
# ------------------------------------------------

def approve_spec(change_id: str):
    if change_id not in CHANGE_STORE:
        return {"error": "INVALID_CHANGE_ID"}

    CHANGE_STORE[change_id]["approvalStatus"] = "APPROVED"
    return {"status": "Waiting for Developer Approval"}


def developer_approve_spec(change_id: str):
    if change_id not in CHANGE_STORE:
        return {"error": "INVALID_CHANGE_ID"}

    CHANGE_STORE[change_id]["approvalStatus"] = "APPROVED"
    return {"status": "Approved"}

# ------------------------------------------------
# STEP 3: JAVA PATCH / CODE GENERATION
# ------------------------------------------------

def _sanitize_results_java(results: list) -> None:
    """Remove duplicate field declarations from every result's newCode (all DTOs)."""
    for r in results:
        code = r.get("newCode")
        if code and isinstance(code, str) and "private " in code:
            r["newCode"] = sanitize_java_dto_code(code)
            if r.get("oldCode") != code and r.get("diff"):
                r["diff"] = generate_diff(r.get("oldCode", ""), r["newCode"], r.get("file", ""))


def generate_patch_after_approval(change_id: str):
    entry = CHANGE_STORE.get(change_id)

    if not entry:
        return {"error": "INVALID_CHANGE_ID"}

    if entry["approvalStatus"] != "APPROVED":
        return {"error": "SPEC_NOT_APPROVED"}

    payload = entry["payload"]
    change_type = payload.get("changeType") or payload.get("change_type")

    # ==========================================================
    # 🆕 NEW API → FULL CODE + DTO PATCH + XSD VALIDATION
    # ==========================================================
    if change_type == "ADD_NEW_API":
        xsd = entry["newXsd"]
        api_name = normalize_api_name(payload["apiName"])

        results = []

        # 1️⃣ Generate NEW API Java files
        generated = build_new_api(api_name, xsd)

        for file_name, code in generated["generatedFiles"].items():
            # New file: no existing code on left, full file on right
            results.append({
                "type": "NEW_FILE",
                "file": file_name,
                "oldCode": "",
                "newCode": code,
                "diff": generate_diff("", code, file_name)
            })

        # 2️⃣ Patch EXISTING shared DTOs deterministically
        java_index = index_java_codebase(JAVA_CODEBASE_PATH)
        request_blocks = extract_request_blocks(xsd, api_name)
        xsd_attributes = extract_xsd_attributes(xsd)

        for block in request_blocks:
            dto = find_java_file(java_index, block)
            if not dto:
                continue

            attrs = xsd_attributes.get(block, [])
            patched_code = patch_dto_from_xsd(dto["code"], attrs)

            if patched_code != dto["code"]:
                # Existing DTO patch: show old vs new in UI
                results.append({
                    "type": "DTO_PATCH",
                    "class": block,
                    "file": dto["path"],
                    "oldCode": dto["code"],
                    "newCode": patched_code,
                    "diff": generate_diff(dto["code"], patched_code, dto["path"])
                })

        # 3️⃣ ✅ XSD-DRIVEN REQUEST VALIDATOR
        rules = extract_request_validation_rules(xsd, api_name)

        if rules:
            validator_code = generate_api_validator(api_name, rules)
            # New validator file
            results.append({
                "type": "NEW_FILE",
                "file": f"Req{api_name}Validator.java",
                "oldCode": "",
                "newCode": validator_code,
                "diff": generate_diff("", validator_code, f"Req{api_name}Validator.java")
            })

        _maybe_create_manifest(change_id, payload)
        _sanitize_results_java(results)
        return {
            "changeId": change_id,
            "apiName": payload.get("apiName"),
            "approvedXsd": xsd,
            "results": results,
            "message": "NEW_API_WITH_DYNAMIC_DTO_PATCH_AND_VALIDATION"
        }

    # ==========================================================
    # ♻ EXISTING API → PATCH FLOW (UNCHANGED)
    # ==========================================================

    # Multi-field support: allow fieldAdditions[]; fall back to single-field payload keys.
    additions = payload.get("fieldAdditions")
    if not (isinstance(additions, list) and additions):
        xml_path = payload.get("xmlPath")
        attribute = payload.get("attributeName")
        if not xml_path or not attribute:
            return {
                "error": "INVALID_PAYLOAD",
                "message": "xmlPath and attributeName required"
            }
        additions = [{
            "xmlPath": xml_path,
            "attributeName": attribute,
            "datatype": payload.get("datatype"),
            "mandatory": payload.get("mandatory", False),
            "allowedValues": payload.get("allowedValues"),
        }]

    # Group additions by xmlPath so we patch the right DTO(s)
    grouped: dict[str, list[dict]] = {}
    for a in additions:
        if not isinstance(a, dict):
            continue
        xp = (a.get("xmlPath") or "").strip()
        an = (a.get("attributeName") or "").strip()
        if not xp or not an:
            continue
        grouped.setdefault(xp, []).append(a)

    if not grouped:
        return {"error": "INVALID_PAYLOAD", "message": "No valid fieldAdditions found"}

    java_index = index_java_codebase(JAVA_CODEBASE_PATH)
    results = []

    for xml_path, group in grouped.items():
        # Use first attribute only for mapping heuristics
        attribute = (group[0].get("attributeName") or "").strip()

        mapped_class = get_mapped_class(xml_path)
        if not mapped_class:
            mapping = map_xml_to_java(
                xml_path=xml_path,
                attribute=attribute,
                java_index=java_index
            )
            if not mapping:
                return {
                    "error": "JAVA_MAPPING_NOT_FOUND",
                    "message": f"Unable to map XML path to Java class: {xml_path}"
                }
            mapped_class = mapping["className"]
            save_mapping(xml_path, mapped_class)

        dto = find_java_file(java_index, mapped_class)
        if not dto:
            return {"error": "JAVA_FILE_NOT_FOUND"}

        # For Device DTO under ReqPay.Payer.Device, attributes are represented as Tag{name,value}
        # entries, not as direct fields on Device. In that case we SHOULD NOT patch Device.java
        # to add new @XmlAttribute fields or getters/setters; validation must be tag-based only.
        is_device_path = xml_path.endswith(".Payer.Device")
        if is_device_path and mapped_class == "Device":
            # Skip DTO patch for Device; validator generation below will still handle tag-based logic.
            continue

        # Patch this DTO once using grouped changes
        grouped_payload = dict(payload)
        grouped_payload["xmlPath"] = xml_path
        grouped_payload["fieldAdditions"] = group
        new_dto = generate_java_patch(dto["code"], grouped_payload)

        results.append({
            "type": "DTO",
            "class": mapped_class,
            "file": dto["path"],
            "oldCode": dto["code"],
            "newCode": new_dto,
            "diff": generate_diff(dto["code"], new_dto, dto["path"])
        })

    # Legacy payload-driven validation, now enriched with javaPath and tag/field hints when possible
    if should_update_validator(payload):
        validator = find_java_file(java_index, "ReqPayValidator")
        rules = find_java_file(java_index, "ValidationRules")

        if validator and rules:
            # Try to compute a representative javaPath and attribute metadata
            # for the first xmlPath in this change. This feeds structured
            # context into the validator prompt so the LLM can choose the
            # correct pattern (direct field vs tag-based lookup).
            validator_payload = dict(payload)
            try:
                first_xml_path = next(iter(grouped.keys()))
            except StopIteration:
                first_xml_path = None

            if first_xml_path:
                # Attach xmlPath so prompt can mention the concrete hierarchy.
                validator_payload["xmlPath"] = first_xml_path

                # Compute Java object path, e.g. reqPay.getPayer().getDevice()
                java_path = _compute_java_path_from_xml_path(first_xml_path, java_index)
                if java_path:
                    validator_payload["javaPath"] = java_path

                # Derive attributeName for this xmlPath (first grouped entry).
                first_additions = grouped.get(first_xml_path) or []
                if first_additions and isinstance(first_additions[0], dict):
                    attr_name = (first_additions[0].get("attributeName") or "").strip()
                    if attr_name:
                        validator_payload["attributeName"] = attr_name

                # Hint whether this should be treated as a tag-based Device attribute.
                # We avoid hardcoding any particular attribute name (like BINDINGMODE)
                # and instead rely on the XML path and DTO structure.
                is_device_path = first_xml_path.endswith(".Payer.Device")
                mapped_class_for_first = get_mapped_class(first_xml_path)
                if not mapped_class_for_first:
                    # Best-effort: try to map again if store is empty for this xmlPath.
                    mapping = map_xml_to_java(
                        xml_path=first_xml_path,
                        attribute=(validator_payload.get("attributeName") or ""),
                        java_index=java_index,
                    )
                    if mapping:
                        mapped_class_for_first = mapping.get("className")
                        save_mapping(first_xml_path, mapped_class_for_first)

                is_device_dto = mapped_class_for_first == "Device"

                if is_device_path and is_device_dto:
                    # Tag-based pattern: Device has List<Tag> tags; logical
                    # "attributes" are represented as Tag{name, value} rows.
                    validator_payload["tagBased"] = True
                    validator_payload["fieldBased"] = False
                    validator_payload["tagContainerField"] = "tags"
                    validator_payload["tagClass"] = "Tag"
                    validator_payload["tagNameField"] = "name"
                    validator_payload["tagValueField"] = "value"
                else:
                    # Default hint: treat as direct field on the mapped DTO.
                    validator_payload.setdefault("fieldBased", True)

            updated_rules, updated_validator = generate_validator_patch(
                rules["code"],
                validator["code"],
                validator_payload,
            )

            # Validation rules file patch
            results.append({
                "type": "VALIDATION_RULES",
                "file": rules["path"],
                "oldCode": rules["code"],
                "newCode": updated_rules,
                "diff": generate_diff(rules["code"], updated_rules, rules["path"])
            })

            # Validator file patch
            results.append({
                "type": "VALIDATOR",
                "file": validator["path"],
                "oldCode": validator["code"],
                "newCode": updated_validator,
                "diff": generate_diff(validator["code"], updated_validator, validator["path"])
            })

    _maybe_create_manifest(change_id, payload)
    _sanitize_results_java(results)
    return {
        "changeId": change_id,
        "approvedXsd": entry["newXsd"],
        "results": results
    }
