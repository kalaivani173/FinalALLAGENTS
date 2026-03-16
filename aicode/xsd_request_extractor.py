from lxml import etree

XS_NS = "http://www.w3.org/2001/XMLSchema"
NS = {"xs": XS_NS}


def strip_code_fences(xsd: str) -> str:
    xsd = xsd.strip()
    if xsd.startswith("```"):
        xsd = xsd.strip("`")
        xsd = xsd.replace("xml", "", 1).strip()
    return xsd


def extract_request_blocks(xsd: str, api_name: str) -> set:
    """
    Returns all element names under Req<API>
    Example: Head, Txn, Criteria
    """
    root = etree.XML(strip_code_fences(xsd).encode("utf-8"))

    req_root = f"Req{api_name}"
    blocks = set()

    for el in root.findall(".//xs:element", NS):
        if el.attrib.get("name") == req_root:
            for child in el.findall(".//xs:element", NS):
                name = child.attrib.get("name")
                if name:
                    blocks.add(name)

    return blocks
