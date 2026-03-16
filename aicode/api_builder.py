from lxml import etree
from typing import List

XS_NS = "http://www.w3.org/2001/XMLSchema"
NS = {"xs": XS_NS}


def strip_code_fences(xsd: str) -> str:
    xsd = xsd.strip()
    if xsd.startswith("```"):
        xsd = xsd.strip("`")
        xsd = xsd.replace("xml", "", 1).strip()
    return xsd


def parse_xsd(xsd: str):
    return etree.XML(strip_code_fences(xsd).encode("utf-8"))


def java_name(name: str) -> str:
    return name[0].upper() + name[1:]


def normalize_api_name(api_name: str) -> str:
    if api_name.startswith("Req"):
        return api_name[3:]
    if api_name.startswith("Resp"):
        return api_name[4:]
    return api_name


def get_complex_type_for_element(element, type_map):
    ct = element.find("xs:complexType", NS)
    if ct is not None:
        return ct

    type_name = element.attrib.get("type")
    type_name = type_name.replace("xs:", "")
    return type_map[type_name]


def _dedupe_preserve_order(items: List[str]) -> List[str]:
    """Remove duplicate field names while preserving first occurrence order."""
    seen = set()
    out = []
    for x in items:
        key = (x or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(x)
    return out


def generate_java_class(class_name: str, fields: List[str], root=False) -> str:
    imports = "import jakarta.xml.bind.annotation.*;\n"

    annotations = []
    if root:
        annotations.append(f'@XmlRootElement(name = "{class_name}")')
    annotations.append("@XmlAccessorType(XmlAccessType.FIELD)")

    # Avoid duplicate fields (e.g. from XSD with repeated element names)
    fields = _dedupe_preserve_order(list(fields))

    field_blocks = []
    methods = []

    for f in fields:
        fname = f[0].lower() + f[1:]
        field_blocks.append(
            f'    @XmlElement(name = "{f}")\n'
            f'    private {f} {fname};\n'
        )

        methods.append(
            f"""
    public {f} get{f}() {{
        return {fname};
    }}

    public void set{f}({f} {fname}) {{
        this.{fname} = {fname};
    }}
"""
        )

    return f"""package com.npci.upi.dto;

{imports}
{chr(10).join(annotations)}
public class {class_name} {{

{chr(10).join(field_blocks)}
{chr(10).join(methods)}
}}
"""


def generate_controller(api_name: str) -> str:
    return f"""package com.npci.upi.controller;

import com.npci.upi.dto.*;
import com.npci.upi.service.{api_name}Service;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/upi/{api_name}")
public class {api_name}Controller {{

    private final {api_name}Service service;

    public {api_name}Controller({api_name}Service service) {{
        this.service = service;
    }}

    @PostMapping
    public Resp{api_name} handle(@RequestBody Req{api_name} request) {{
        return service.process(request);
    }}
}}
"""


def generate_service(api_name: str) -> str:
    return f"""package com.npci.upi.service;

import com.npci.upi.dto.*;
import org.springframework.stereotype.Service;

@Service
public class {api_name}Service {{

    public Resp{api_name} process(Req{api_name} request) {{
        return new Resp{api_name}();
    }}
}}
"""


def generate_validator(api_name: str) -> str:
    return f"""package com.npci.upi.validation;

import com.npci.upi.dto.*;

public class {api_name}Validator {{

    public static String validate(Req{api_name} req) {{
        return null;
    }}
}}
"""


def build_new_api(api_name: str, xsd: str) -> dict:
    api_name = normalize_api_name(api_name)
    root = parse_xsd(xsd)

    type_map = {
        ct.attrib["name"]: ct
        for ct in root.findall("xs:complexType", NS)
        if "name" in ct.attrib
    }

    elements = root.findall("xs:element", NS)
    generated = {}

    for el in elements:
        name = el.attrib["name"]
        ct = get_complex_type_for_element(el, type_map)
        raw_fields = [java_name(e.attrib["name"]) for e in ct.findall("xs:sequence/xs:element", NS)]
        fields = _dedupe_preserve_order(raw_fields)
        generated[f"{name}.java"] = generate_java_class(name, fields, root=True)

    generated[f"{api_name}Controller.java"] = generate_controller(api_name)
    generated[f"{api_name}Service.java"] = generate_service(api_name)
   # generated[f"{api_name}Validator.java"] = generate_validator(api_name)

    return {
        "apiName": api_name,
        "generatedFiles": generated
    }
