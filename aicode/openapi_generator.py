import json
import os
from datetime import datetime
from lxml import etree

XS_NS = "http://www.w3.org/2001/XMLSchema"
NS = {"xs": XS_NS}


def _read_first_sample_xml(samples_dir: str) -> str | None:
    """Best-effort: return the first *.xml file contents (trimmed) for examples."""
    try:
        if not os.path.isdir(samples_dir):
            return None
        for f in os.listdir(samples_dir):
            if f.lower().endswith(".xml"):
                p = os.path.join(samples_dir, f)
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    txt = fh.read().strip()
                return txt[:20000] if txt else None
    except Exception:
        return None
    return None


def _xsd_type_to_json_type(xsd_type: str) -> str:
    """Map XSD type to JSON/OpenAPI type."""
    if not xsd_type:
        return "string"
    t = (xsd_type.split(":")[-1] if ":" in xsd_type else xsd_type).lower()
    if t in ("integer", "positiveinteger", "nonnegativeinteger", "int", "long"):
        return "integer"
    if t in ("decimal", "float", "double"):
        return "number"
    if t == "boolean":
        return "boolean"
    return "string"


def _xsd_to_openapi_schema(xsd_content: str, root_element_name: str) -> dict | None:
    """
    Parse XSD and build OpenAPI schema with properties reflecting elements and attributes.
    Returns schema dict or None on parse error.
    """
    if not xsd_content or not isinstance(xsd_content, str):
        return None
    xsd_clean = xsd_content.strip().lstrip("\ufeff")
    try:
        root = etree.XML(xsd_clean.encode("utf-8"))
    except Exception:
        return None

    def find_root_element():
        for el in root.findall(".//xs:element", NS):
            if el.attrib.get("name") == root_element_name:
                return el
        return None

    root_el = find_root_element()
    if root_el is None:
        return None

    def build_schema_from_element(el) -> dict:
        """Recursively build OpenAPI schema from xs:element."""
        ct = el.find("xs:complexType", NS)
        if ct is None:
            # Simple type
            typ = el.attrib.get("type", "xs:string")
            return {"type": _xsd_type_to_json_type(typ), "xml": {"name": el.attrib.get("name", "")}}

        props = {}

        # Attributes first (XML attributes on element)
        for attr in ct.findall("xs:attribute", NS):
            name = attr.attrib.get("name")
            if not name:
                continue
            typ = _xsd_type_to_json_type(attr.attrib.get("type", "xs:string"))
            props[name] = {
                "type": typ,
                "description": f"Attribute: {name}",
                "xml": {"name": name, "attribute": True},
            }

        # Child elements (sequence)
        seq = ct.find("xs:sequence", NS)
        if seq is not None:
            for child in seq.findall("xs:element", NS):
                cname = child.attrib.get("name")
                if not cname:
                    continue
                max_occurs = child.attrib.get("maxOccurs", "1")
                child_schema = build_schema_from_element(child)
                if max_occurs == "unbounded":
                    child_schema = {
                        "type": "array",
                        "items": child_schema,
                        "xml": {"name": cname, "wrapped": False},
                    }
                else:
                    child_schema["xml"] = child_schema.get("xml", {})
                    child_schema["xml"]["name"] = cname
                props[cname] = child_schema

        # choice (take first option)
        choice = ct.find("xs:choice", NS)
        if choice is not None and not props:
            for child in choice.findall("xs:element", NS):
                cname = child.attrib.get("name")
                if cname:
                    props[cname] = build_schema_from_element(child)
                    props[cname]["xml"] = props[cname].get("xml", {})
                    props[cname]["xml"]["name"] = cname
                    break

        return {
            "type": "object",
            "properties": props,
            "xml": {"name": el.attrib.get("name", "")},
        }

    schema = build_schema_from_element(root_el)
    schema["xml"] = schema.get("xml", {})
    schema["xml"]["name"] = root_element_name
    return schema


def _xsd_to_sample_xml(xsd_content: str, root_element_name: str, depth_limit: int = 4) -> str | None:
    """Generate a sample XML string from XSD structure (for Swagger example)."""
    try:
        root = etree.XML(xsd_content.encode("utf-8") if isinstance(xsd_content, str) else xsd_content)
    except Exception:
        return None

    def find_root_element():
        for el in root.findall(".//xs:element", NS):
            if el.attrib.get("name") == root_element_name:
                return el
        return None

    root_el = find_root_element()
    if root_el is None:
        return None

    def build_element_xml(el, depth: int) -> str:
        if depth > depth_limit:
            return ""
        el_name = el.attrib.get("name", "")
        ct = el.find("xs:complexType", NS)
        if ct is None:
            return f"<{el_name}></{el_name}>"
        attr_parts = [f' {a.attrib.get("name")}=""' for a in ct.findall("xs:attribute", NS) if a.attrib.get("name")]
        attrs_str = "".join(attr_parts)
        child_parts = []
        seq = ct.find("xs:sequence", NS)
        if seq is not None:
            for child in seq.findall("xs:element", NS):
                cname = child.attrib.get("name")
                if cname:
                    child_parts.append(build_element_xml(child, depth + 1))
        children_str = "".join(child_parts)
        return f"<{el_name}{attrs_str}>{children_str}</{el_name}>"

    return build_element_xml(root_el, 1)


def build_openapi_spec(
    *,
    change_id: str,
    api_name: str,
    xsd_url: str,
    sample_xml: str | None = None,
    xsd_content: str | None = None,
) -> dict:
    """
    Build OpenAPI spec for XML payloads.
    When xsd_content is provided, schema and example are derived from XSD.
    """
    api_name = (api_name or "API").strip() or "API"
    title = f"{api_name} (Change {change_id})"

    if api_name.startswith("Req") and len(api_name) > 3:
        resp_name = "Resp" + api_name[3:]
    else:
        resp_name = f"{api_name}Response"

    # Derive schema and example from XSD when available
    request_schema = None
    req_example = sample_xml

    if xsd_content and xsd_content.strip():
        request_schema = _xsd_to_openapi_schema(xsd_content, api_name)
        if not req_example:
            req_example = _xsd_to_sample_xml(xsd_content, api_name)

    if request_schema is None:
        request_schema = {
            "type": "object",
            "description": f"XML payload. Validate against XSD at: {xsd_url}",
            "xml": {"name": api_name},
            "additionalProperties": True,
        }

    if not request_schema.get("description"):
        request_schema["description"] = f"XML payload. Validate against XSD at: {xsd_url}"

    req_example = req_example or f"<{api_name}></{api_name}>"
    resp_example = f"<{resp_name}></{resp_name}>"

    path_key = f"/npciswitch/mock/{change_id}/{api_name}"
    op_id = f"post{''.join(ch for ch in api_name if ch.isalnum())}"

    return {
        "openapi": "3.0.3",
        "info": {
            "title": title,
            "version": change_id,
            "description": "Auto-generated from XSD for change communication. "
            "Schema reflects XSD structure; payloads are XML.",
            "x-generatedAt": datetime.utcnow().isoformat(),
        },
        "servers": [{"url": "http://localhost:8000", "description": "Example server (update per partner)"}],
        "paths": {
            path_key: {
                "post": {
                    "operationId": op_id,
                    "summary": f"{api_name} operation",
                    "description": f"Request/response are XML. Authoritative schema: {xsd_url}",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/xml": {
                                "schema": request_schema,
                                "example": req_example,
                                "examples": {"sample": {"value": req_example}},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/xml": {
                                    "schema": {
                                        "type": "object",
                                        "description": f"XML response. Validate against XSD at: {xsd_url}",
                                        "xml": {"name": resp_name},
                                        "additionalProperties": True,
                                    },
                                    "example": resp_example,
                                    "examples": {"sample": {"value": resp_example}},
                                }
                            },
                        },
                        "400": {"description": "Bad Request"},
                        "401": {"description": "Unauthorized"},
                        "500": {"description": "Server Error"},
                    },
                    "security": [{"bearerAuth": []}],
                    "x-npci-xsd": xsd_url,
                }
            }
        },
        "components": {"securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}}},
    }


def write_openapi_spec(
    *,
    base_dir: str,
    change_id: str,
    api_name: str,
    xsd_url: str,
) -> tuple[str, dict]:
    """
    Generate and write artifacts/specs/<changeId>/openapi.json under base_dir.
    Reads XSD from artifacts/xsd/<changeId>/ when available to build schema from XSD.
    Returns (file_path, spec_dict).
    """
    artifacts_dir = os.path.join(base_dir, "artifacts")
    samples_dir = os.path.join(artifacts_dir, "samples", change_id)
    specs_dir = os.path.join(artifacts_dir, "specs", change_id)
    xsd_dir = os.path.join(artifacts_dir, "xsd", change_id)
    os.makedirs(specs_dir, exist_ok=True)

    sample_xml = _read_first_sample_xml(samples_dir)
    xsd_content = None
    if os.path.isdir(xsd_dir):
        for f in os.listdir(xsd_dir):
            if f.endswith(".xsd"):
                xsd_path = os.path.join(xsd_dir, f)
                with open(xsd_path, "r", encoding="utf-8", errors="replace") as fh:
                    xsd_content = fh.read()
                break

    spec = build_openapi_spec(
        change_id=change_id,
        api_name=api_name,
        xsd_url=xsd_url,
        sample_xml=sample_xml,
        xsd_content=xsd_content,
    )

    out_path = os.path.join(specs_dir, "openapi.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)
    return out_path, spec
