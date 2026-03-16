from lxml import etree

XS_NS = "http://www.w3.org/2001/XMLSchema"
NS = {"xs": XS_NS}


# -------------------------------------------------
# Internal utility
# -------------------------------------------------

def _clean_xsd(xsd: str) -> str:
    xsd = xsd.strip()

    if xsd.startswith("```"):
        xsd = xsd.strip("`")
        if xsd.startswith("xml"):
            xsd = xsd[3:]
        xsd = xsd.strip()

    idx = xsd.find("<")
    if idx > 0:
        xsd = xsd[idx:]

    return xsd


# -------------------------------------------------
# EXISTING: Generic attribute extraction (UNCHANGED)
# -------------------------------------------------

def extract_validation_rules(xsd: str) -> list:
    """
    Extracts ALL attributes from XSD (request + response).

    Example output:
    [
      {"parent": "Head", "field": "ver", "mandatory": True},
      {"parent": "Result", "field": "code", "mandatory": True}
    ]

    ⚠️ This is intentionally generic.
    """
    xsd = _clean_xsd(xsd)
    root = etree.XML(xsd.encode("utf-8"))

    rules = []

    for el in root.findall(".//xs:element", NS):
        parent = el.attrib.get("name")
        ct = el.find("xs:complexType", NS)
        if not parent or ct is None:
            continue

        for attr in ct.findall("xs:attribute", NS):
            rules.append({
                "parent": parent,
                "field": attr.attrib["name"],
                "mandatory": attr.attrib.get("use") == "required"
            })

    return rules


# -------------------------------------------------
# EXISTING: Block discovery (UNCHANGED)
# -------------------------------------------------

def extract_xsd_blocks(xsd: str) -> set:
    """
    Dynamically extracts ALL element names from XSD.

    Used for DTO patching decisions.
    """
    xsd = _clean_xsd(xsd)
    root = etree.XML(xsd.encode("utf-8"))

    blocks = set()

    for el in root.findall(".//xs:element", NS):
        name = el.attrib.get("name")
        if name:
            blocks.add(name)

    return blocks


# -------------------------------------------------
# ✅ NEW: Request-scoped validation extractor
# -------------------------------------------------

def extract_request_validation_rules(xsd: str, api_name: str) -> list:
    """
    Extracts ONLY mandatory validation rules under Req<API>.

    Output:
    [
      {"parent": "Head", "field": "ver"},
      {"parent": "Txn", "field": "id"},
      {"parent": "Criteria", "field": "category"}
    ]

    ✔ No hardcoding
    ✔ Safe for EXISTING + NEW XSD
    ✔ Ignores response blocks completely
    """
    xsd = _clean_xsd(xsd)
    root = etree.XML(xsd.encode("utf-8"))

    request_root = f"Req{api_name}"
    valid_parents = set()

    # 1️⃣ Discover which blocks belong to Req<API>
    for el in root.findall(".//xs:element", NS):
        if el.attrib.get("name") == request_root:
            for child in el.findall(".//xs:element", NS):
                name = child.attrib.get("name")
                if name:
                    valid_parents.add(name)

    if not valid_parents:
        return []

    # 2️⃣ Filter mandatory rules only for those blocks
    all_rules = extract_validation_rules(xsd)

    return [
        {
            "parent": r["parent"],
            "field": r["field"]
        }
        for r in all_rules
        if r["mandatory"] and r["parent"] in valid_parents
    ]
