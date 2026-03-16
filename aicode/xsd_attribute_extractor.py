from lxml import etree

XS_NS = "http://www.w3.org/2001/XMLSchema"
NS = {"xs": XS_NS}


def strip_code_fences(xsd: str) -> str:
    xsd = xsd.strip()
    if xsd.startswith("```"):
        xsd = xsd.strip("`")
        xsd = xsd.replace("xml", "", 1).strip()
    return xsd


def extract_xsd_attributes(xsd: str) -> dict:
    """
    Returns:
    {
      "Head": ["ver", "ts"],
      "Txn": ["id", "type"],
      "Criteria": ["category"]
    }
    """
    root = etree.XML(strip_code_fences(xsd).encode("utf-8"))
    result = {}

    for el in root.findall(".//xs:element", NS):
        name = el.attrib.get("name")
        ct = el.find("xs:complexType", NS)
        if not name or ct is None:
            continue

        attrs = [
            a.attrib["name"]
            for a in ct.findall("xs:attribute", NS)
        ]

        if attrs:
            result[name] = attrs

    return result
