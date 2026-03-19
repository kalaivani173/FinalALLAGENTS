import json


def _find_by_name(java_index: list, name: str):
    """Find a DTO by exact class name (case-insensitive fallback)."""
    # Exact match first
    for j in java_index:
        if j["className"] == name:
            return j
    # Case-insensitive
    nl = name.lower()
    for j in java_index:
        if j["className"].lower() == nl:
            return j
    return None


def _find_by_xmlroot(java_index: list, name: str):
    """Find a DTO whose @XmlRootElement name matches (case-insensitive)."""
    nl = name.lower()
    for j in java_index:
        for r in (j.get("xmlRoot") or []):
            if r.lower() == nl:
                return j
    return None


def _find_by_substring(java_index: list, name: str):
    """Fuzzy fallback: class name contains segment or segment contains class name."""
    nl = name.lower()
    for j in java_index:
        cn = j["className"].lower()
        # Skip tiny names that would match everything
        if len(cn) < 3:
            continue
        if nl in cn or cn in nl:
            return j
    return None


def map_xml_to_java(xml_path: str, attribute: str, java_index: list):
    """
    Maps XML path like "ReqPay.Txn" or "UPIPayRequest.Payer.Device" to
    the correct Java DTO.

    Strategy:
    1. Walk the path using @XmlRootElement and nested field-type resolution.
    2. When the root segment doesn't match any @XmlRootElement (e.g. the
       uploaded XSD uses "UPIPayRequest" but the DTO says "ReqPay"), fall back
       to matching the LAST path segment by:
         a. Exact class name
         b. @XmlRootElement value
         c. Substring match
    """
    parts = xml_path.split(".")
    if len(parts) < 2:
        return None

    root_xml = parts[0]
    target_xml = parts[-1]   # deepest segment — the element to patch

    # ── Path-walk strategy ──────────────────────────────────────────────────
    root_candidates = [j for j in java_index if root_xml in (j.get("xmlRoot") or [])]

    if root_candidates:
        current_dto = root_candidates[0]

        # Walk each subsequent path segment through nested field types
        for element in parts[1:]:
            field_type = current_dto["fields"].get(element.lower())
            if not field_type:
                break
            next_dto = next((j for j in java_index if j["className"] == field_type), None)
            if not next_dto:
                break
            current_dto = next_dto

        # If we never moved past root and still can't resolve, try fallback below
        if current_dto is not root_candidates[0]:
            return {
                "className": current_dto["className"],
                "path": current_dto["path"],
                "reason": "Resolved via nested DTO field type walk",
            }

        # Stayed at root — check if at least the immediate child is a field
        field_type = current_dto["fields"].get(parts[1].lower())
        if field_type:
            child = _find_by_name(java_index, field_type)
            if child:
                return {
                    "className": child["className"],
                    "path": child["path"],
                    "reason": f"Resolved child field '{parts[1]}' from root",
                }
        # Root resolved but can't walk further; return the root DTO
        return {
            "className": current_dto["className"],
            "path": current_dto["path"],
            "reason": "Resolved to root DTO (could not walk further)",
        }

    # ── Fallback: root element name didn't match any @XmlRootElement ────────
    # This happens when the user's XSD uses a custom root name (e.g.
    # "UPIPayRequest") while the Java DTOs use the UPI standard name ("ReqPay").
    # We resolve by matching the DEEPEST path segment against class / xmlRoot names.

    hit = (
        _find_by_name(java_index, target_xml)
        or _find_by_xmlroot(java_index, target_xml)
        or _find_by_substring(java_index, target_xml)
    )
    if hit:
        return {
            "className": hit["className"],
            "path": hit["path"],
            "reason": f"Fallback: matched target segment '{target_xml}' to class '{hit['className']}'",
        }

    return None
