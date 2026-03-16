ALLOWED_TYPES = {
    "ADD_XML_FIELD",
    "ADD_XML_ATTRIBUTE",
    "ADD_VALIDATION",
    "ADD_NEW_API",
    "api-addition",  # NPCI switch may send kebab-case
    "field-addition",  # NPCI switch may send kebab-case
}

def validate_manifest(m: dict) -> None:
    required = ["changeId", "issuer", "changeType", "apiName"]
    for r in required:
        if r not in m:
            raise ValueError(f"Missing required field: {r}")

    if m["issuer"] != "NPCI_UPI_SWITCH":
        raise ValueError("Untrusted issuer: must be NPCI_UPI_SWITCH")

    if m["changeType"] not in ALLOWED_TYPES:
        raise ValueError(f"Invalid changeType: {m['changeType']}. Allowed: {sorted(ALLOWED_TYPES)}")

    # For ADD_XML_FIELD / ADD_XML_ATTRIBUTE / ADD_VALIDATION / field-addition we expect impactedPaths
    if m["changeType"] in ("ADD_XML_FIELD", "ADD_XML_ATTRIBUTE", "ADD_VALIDATION", "field-addition"):
        raw_paths = m.get("impactedPaths")
        if not raw_paths:
            raise ValueError("impactedPaths required for this changeType")
        # Normalize: allow list or dict (e.g. {"0": {...}}) so iteration yields path objects
        if isinstance(raw_paths, dict):
            paths = [raw_paths[k] for k in sorted(raw_paths.keys(), key=lambda k: int(k) if str(k).isdigit() else 0)]
        else:
            paths = list(raw_paths) if raw_paths else []
        for i, p in enumerate(paths):
            if not isinstance(p, dict):
                raise ValueError(f"impactedPaths[{i}] must be an object")
            attr = p.get("attribute")
            # attribute can be dict or list (take first element's name)
            attr_name = None
            if attr is not None:
                if isinstance(attr, dict):
                    attr_name = attr.get("name")
                elif isinstance(attr, list) and len(attr) > 0 and isinstance(attr[0], dict):
                    attr_name = attr[0].get("name")
            has_attr_name = bool(attr_name)
            has_field_name = bool(p.get("fieldName"))
            has_xml_path = bool(p.get("xmlPath") or p.get("path"))
            if not (has_attr_name or has_field_name or has_xml_path):
                raise ValueError(
                    f"impactedPaths[{i}] must have attribute.name, fieldName, or xmlPath"
                )
