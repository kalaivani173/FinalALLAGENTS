from datetime import datetime

def create_manifest(payload, decision):
    return {
        "changeId": payload["changeId"],
        "changeType": payload["changeType"],
        "fieldName": payload["fieldName"],
        "fieldPath": payload.get("fieldPath"),
        "decision": decision,
        "timestamp": datetime.utcnow().isoformat(),
        "npciStatus": "READY_AFTER_APPROVAL"
    }


# Canonical change type for manifest (backend/partner expectation)
MANIFEST_CHANGE_TYPE_ADD_ATTRIBUTE = "ADD_XML_ATTRIBUTE"


def _build_impacted_paths(payload: dict):
    """Build impactedPaths from payload: prefer fieldAdditions[]; fall back to single-field keys."""
    additions = payload.get("fieldAdditions")
    if isinstance(additions, list) and additions:
        paths = []
        for a in additions:
            if not isinstance(a, dict):
                continue
            xml_path = a.get("xmlPath") or a.get("xml_path")
            if not xml_path and (a.get("elementName") or a.get("element_name")) and (a.get("apiName") or a.get("api_name") or payload.get("apiName")):
                api = (a.get("apiName") or a.get("api_name") or payload.get("apiName") or "").strip()
                elem = (a.get("elementName") or a.get("element_name") or "").strip()
                if api and elem:
                    xml_path = f"{api}.{elem}"
            attr_name = a.get("attributeName") or a.get("attribute_name")
            if not xml_path or (attr_name is None or (isinstance(attr_name, str) and not attr_name.strip())):
                continue
            datatype = a.get("datatype") or "xs:string"
            mandatory = a.get("mandatory", False)
            allowed = a.get("allowedValues")
            if allowed is None:
                allowed = []
            if not isinstance(allowed, list):
                allowed = list(allowed) if allowed else []
            paths.append({
                "xmlPath": xml_path,
                "change": MANIFEST_CHANGE_TYPE_ADD_ATTRIBUTE,
                "attribute": {
                    "name": attr_name,
                    "datatype": datatype,
                    "mandatory": bool(mandatory),
                    "allowedValues": allowed,
                },
            })
        if paths:
            return paths
    # Single-field fallback (legacy / API that sends xmlPath, attributeName at top level)
    raw_change = payload.get("changeType") or payload.get("change_type")
    change_type = MANIFEST_CHANGE_TYPE_ADD_ATTRIBUTE if raw_change in ("field-addition", "ADD_XML_ATTRIBUTE") else raw_change
    xml_path = payload.get("xmlPath") or payload.get("xml_path")
    attr_name = payload.get("attributeName") or payload.get("attribute_name")
    datatype = payload.get("datatype") or "xs:string"
    mandatory = payload.get("mandatory", False)
    allowed = payload.get("allowedValues")
    if allowed is None:
        allowed = []
    if not isinstance(allowed, list):
        allowed = list(allowed) if allowed else []
    # Only include if we have required fields (avoid nulls in manifest)
    if xml_path and attr_name is not None and str(attr_name).strip():
        return [
            {
                "xmlPath": xml_path,
                "change": change_type,
                "attribute": {
                    "name": attr_name,
                    "datatype": datatype,
                    "mandatory": bool(mandatory),
                    "allowedValues": allowed,
                },
            }
        ]
    return []


def create_partner_manifest(
    payload: dict,
    xsd_path: str,
    openapi_path: str | None = None,
    product_note_path: str | None = None,
    product_note_summary: str | None = None,
):
    """Partner manifest for broadcast. impactedPaths built from fieldAdditions or single-field payload."""
    raw_change = payload.get("changeType") or payload.get("change_type")
    manifest_change_type = (
        MANIFEST_CHANGE_TYPE_ADD_ATTRIBUTE if raw_change in ("field-addition", "ADD_XML_ATTRIBUTE") else raw_change
    )
    manifest = {
        "changeId": payload.get("changeId"),
        "issuer": "NPCI_UPI_SWITCH",
        "changeType": manifest_change_type,
        "apiName": payload.get("apiName") or payload.get("api_name"),
        "summary": payload.get("description"),
        "impactedPaths": _build_impacted_paths(payload),
        "xsd": {"path": xsd_path},
        "npciStatus": "READY_FOR_ADOPTION",
        "timestamp": datetime.utcnow().isoformat(),
    }
    if openapi_path:
        manifest["openapi"] = {"path": openapi_path}
    if product_note_path or product_note_summary:
        manifest["productNote"] = {}
        if product_note_path:
            manifest["productNote"]["path"] = product_note_path
        if product_note_summary:
            manifest["productNote"]["summary"] = product_note_summary
    return manifest