from lxml import etree
import os

XS_NS = "http://www.w3.org/2001/XMLSchema"
NSMAP = {"xs": XS_NS}


def load_schema_with_includes(base_xsd_path: str):
    if not os.path.exists(base_xsd_path):
        raise FileNotFoundError(f"Base XSD not found: {base_xsd_path}")

    base_dir = os.path.dirname(base_xsd_path)
    parser = etree.XMLParser(remove_blank_text=True)

    tree = etree.parse(base_xsd_path, parser)
    root = tree.getroot()

    includes = root.xpath(".//xs:include", namespaces=NSMAP)
    for inc in includes:
        location = inc.attrib.get("schemaLocation")
        if not location:
            continue

        include_path = os.path.join(base_dir, location)
        included_tree = etree.parse(include_path, parser)
        included_root = included_tree.getroot()

        for child in included_root:
            if child.tag != f"{{{XS_NS}}}annotation":
                root.append(child)

    return tree


def transform_xsd(base_xsd_path: str, payload: dict) -> str:
    tree = load_schema_with_includes(base_xsd_path)
    root = tree.getroot()

    if payload["changeType"] == "ADD_XML_ATTRIBUTE":
        additions = payload.get("fieldAdditions")
        if isinstance(additions, list) and additions:
            for item in additions:
                if not isinstance(item, dict):
                    continue
                sub = dict(payload)
                sub.update(item)
                _add_xml_attribute(root, sub)
        else:
            _add_xml_attribute(root, payload)
    else:
        raise ValueError("Unsupported changeType")

    return etree.tostring(
        tree,
        pretty_print=True,
        xml_declaration=True,
        encoding="UTF-8"
    ).decode("utf-8")


def _create_enum_simple_type(root, type_name, base_type, allowed_values):
    existing = root.xpath(
        f".//xs:simpleType[@name='{type_name}']",
        namespaces=NSMAP
    )
    if existing:
        return

    simple_type = etree.Element(f"{{{XS_NS}}}simpleType", name=type_name)
    restriction = etree.SubElement(
        simple_type, f"{{{XS_NS}}}restriction", base=base_type
    )

    for val in allowed_values:
        etree.SubElement(
            restriction,
            f"{{{XS_NS}}}enumeration",
            value=str(val)
        )

    root.append(simple_type)


def _add_xml_attribute(root, payload):
    xml_path = payload["xmlPath"]
    attribute_name = payload["attributeName"]
    datatype = payload["datatype"]
    mandatory = payload.get("mandatory", False)
    if isinstance(mandatory, str):
        mandatory = mandatory.strip().lower() in ("true", "1", "yes", "y", "mandatory", "required")
    allowed_values = payload.get("allowedValues")
    if isinstance(allowed_values, str):
        allowed_values = [v.strip() for v in allowed_values.split(",") if v.strip()]

    target_element = xml_path.split(".")[-1]

    complex_types = root.xpath(
        f".//xs:element[@name='{target_element}']/xs:complexType",
        namespaces=NSMAP
    )

    if not complex_types:
        element = root.xpath(
            f".//xs:element[@name='{target_element}']",
            namespaces=NSMAP
        )[0]

        type_name = element.attrib["type"].split(":")[-1]
        complex_types = root.xpath(
            f".//xs:complexType[@name='{type_name}']",
            namespaces=NSMAP
        )

    target_complex_type = complex_types[0]

    if target_complex_type.xpath(
        f"./xs:attribute[@name='{attribute_name}']",
        namespaces=NSMAP
    ):
        return

    attr = etree.Element(f"{{{XS_NS}}}attribute")
    attr.attrib["name"] = attribute_name
    attr.attrib["use"] = "required" if mandatory else "optional"

    if allowed_values:
        enum_type = f"{attribute_name}Type"
        _create_enum_simple_type(
            root, enum_type, datatype, allowed_values
        )
        attr.attrib["type"] = enum_type
    else:
        attr.attrib["type"] = datatype

    target_complex_type.append(attr)
