from pathlib import Path
from lxml import etree

def update_xsd(manifest: dict) -> str | None:
    """Update XSD per manifest. Returns path to updated XSD or None if skipped."""
    xsd_cfg = manifest.get("xsd")
    if not xsd_cfg or not xsd_cfg.get("path"):
        return None

    raw_path = xsd_cfg["path"]
    if isinstance(raw_path, str) and raw_path.strip().startswith("http"):
        return None  # NPCI may send XSD URL; we don't write to URL
    xsd_path = Path(raw_path)
    if not xsd_path.exists():
        return None

    tree = etree.parse(str(xsd_path))
    root = tree.getroot()
    ns = "http://www.w3.org/2001/XMLSchema"

    impacted = manifest.get("impactedPaths") or []
    for item in impacted:
        attr = item.get("attribute")
        if not attr or not attr.get("name"):
            continue
        dtype = attr.get("datatype") or attr.get("type") or "xs:string"
        elem = etree.Element(
            f"{{{ns}}}attribute",
            name=attr["name"],
            type=dtype,
            use="required" if attr.get("mandatory") else "optional",
        )
        root.append(elem)

    tree.write(str(xsd_path), pretty_print=True)
    return str(xsd_path)
