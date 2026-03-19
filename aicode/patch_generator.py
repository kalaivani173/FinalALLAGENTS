import json
import re
from langchain_openai import ChatOpenAI

# ------------------------------------------------
# LLM Configuration
# ------------------------------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# ------------------------------------------------
# Deterministic DTO patch (no LLM required)
# ------------------------------------------------
_XSD_TO_JAVA_TYPE = {
    "xs:string": "String",
    "xs:integer": "Integer",
    "xs:int": "int",
    "xs:long": "Long",
    "xs:decimal": "Double",
    "xs:float": "Float",
    "xs:boolean": "Boolean",
    "xs:date": "String",
    "xs:dateTime": "String",
    "xs:token": "String",
    "xs:positiveInteger": "Integer",
    "xs:nonNegativeInteger": "Integer",
    "xs:anyURI": "String",
}

_FIELD_RE = re.compile(r'^\s*private\s+\S+\s+(\w+)\s*;')


def _deterministic_dto_patch(java_code: str, payload: dict) -> str:
    """
    Adds @XmlAttribute field + getter/setter to a Java DTO without calling an LLM.
    Works for single-field (attributeName) and multi-field (fieldAdditions) payloads.
    """
    additions = payload.get("fieldAdditions") or []
    if not additions:
        attr = (payload.get("attributeName") or "").strip()
        if not attr:
            return java_code
        additions = [{
            "attributeName": attr,
            "datatype": payload.get("datatype") or "xs:string",
            "mandatory": bool(payload.get("mandatory", False)),
            "allowedValues": payload.get("allowedValues") or [],
        }]

    # Collect existing field names to avoid duplicates
    existing = set()
    for line in java_code.splitlines():
        m = _FIELD_RE.match(line)
        if m:
            existing.add(m.group(1))

    new_blocks = []
    for a in additions:
        name = (a.get("attributeName") or "").strip()
        if not name or name in existing:
            continue
        java_type = _XSD_TO_JAVA_TYPE.get(a.get("datatype") or "xs:string", "String")
        use = "required" if a.get("mandatory") else "optional"
        cap = name[0].upper() + name[1:]
        block = (
            f'\n    @XmlAttribute(name = "{name}")\n'
            f'    private {java_type} {name};\n'
            f'\n'
            f'    public {java_type} get{cap}() {{\n'
            f'        return {name};\n'
            f'    }}\n'
            f'\n'
            f'    public void set{cap}({java_type} {name}) {{\n'
            f'        this.{name} = {name};\n'
            f'    }}\n'
        )
        new_blocks.append(block)
        existing.add(name)

    if not new_blocks:
        return java_code

    insert_at = java_code.rfind("}")
    if insert_at == -1:
        return java_code + "".join(new_blocks) + "\n}"
    return java_code[:insert_at] + "".join(new_blocks) + "}\n"


def _balance_java_braces(code: str) -> str:
    """
    Ensures Java braces are balanced.
    Adds missing closing braces at the end if necessary.
    """
    open_count = code.count("{")
    close_count = code.count("}")

    if close_count < open_count:
        missing = open_count - close_count
        code = code.rstrip() + "\n" + ("}\n" * missing)

    return code


# ------------------------------------------------
# Java Patch Generator (DTO / Generic)
# ------------------------------------------------
def generate_java_patch(java_code: str, payload: dict) -> str:
    """
    Generates UPDATED Java source code for ONE Java file.

    Used for:
    - DTOs
    - Any non-validator Java file

    Output MUST be compilable Java.
    """

    prompt = f"""
You are a senior NPCI UPI Switch Java developer.

=================================================
EXISTING JAVA FILE (FULL CONTENT):
=================================================
{java_code}

=================================================
APPROVED CHANGE PAYLOAD:
=================================================
{json.dumps(payload, indent=2)}

=================================================
MANDATORY RULES:
=================================================
1. Output ONLY valid compilable Java code
2. NO explanations, NO markdown, NO code fences (no ```)
3. Output the ENTIRE file exactly ONCE — do not repeat the file, do not repeat any line or block
4. Modify ONLY this file if relevant; preserve package, imports, and style

=================================================
DOMAIN RULES:
=================================================
- DTOs define structure ONLY
- ALWAYS add getters and setters for new fields
- NEVER add validation logic in DTOs

=================================================
TASK:
=================================================
Apply the approved change to THIS FILE ONLY.
If not applicable, return the file UNCHANGED.
"""

    try:
        response = llm.invoke(prompt)
        return _sanitize(response.content)
    except Exception:
        # LLM unavailable (e.g. no OPENAI_API_KEY) — fall back to deterministic patch
        return _deterministic_dto_patch(java_code, payload)


# ------------------------------------------------
# Validator Patch Generator (NEW)
# ------------------------------------------------
def generate_validator_patch(
    validation_rules_code: str,
    validator_code: str,
    payload: dict
):
    """
    Generates UPDATED versions of:
    - ValidationRules.java
    - ReqPayValidator.java

    Triggered ONLY when allowedValues exist.
    """

    java_path = payload.get("javaPath")
    xml_path = payload.get("xmlPath")
    attribute_name = (payload.get("attributeName") or "").strip()

    field_based = bool(payload.get("fieldBased"))
    tag_based = bool(payload.get("tagBased"))

    java_path_block = ""
    extra_rules_block = ""
    tag_rules_block = ""

    if java_path:
        java_path_block = f"""
=================================================
JAVA OBJECT PATH FOR NEW FIELD(S)
=================================================
All validations for the newly added field(s) MUST be written by starting from:
{java_path}
and navigating from that object. Do NOT attach the new validation to unrelated
objects (for example, do not put it under Txn if the xmlPath is under Payer.Device).
"""

        extra_rules_block = f"""
F. For new field(s), ALWAYS anchor validation logic on this Java path:
   {java_path}
G. Do NOT hang new validations off unrelated objects (e.g., avoid using Txn
   if the xmlPath is under Payer.Device).
"""

    # Optional tag-based context for Device attributes represented as Tag{name,value}
    if tag_based and java_path and attribute_name:
        tag_container = payload.get("tagContainerField") or "tags"
        tag_name_field = payload.get("tagNameField") or "name"
        tag_value_field = payload.get("tagValueField") or "value"
        # e.g. Payer.Device.BINDINGMODE -> field path for error messages
        device_attr_path = f"Payer.Device.{attribute_name}"

        tag_rules_block = f"""
=================================================
TAG-BASED ATTRIBUTE CONTEXT
=================================================
Some attributes (for example under ReqPay.Payer.Device) are NOT direct Java fields.
Instead, the logical attribute is represented as a Tag inside a list on the container DTO.

- Container object: {java_path}  (e.g. reqPay.getPayer().getDevice())
- Tag list field: {tag_container} (List<Tag>)
- Tag name field: {tag_name_field}
- Tag value field: {tag_value_field}
- Logical attribute name for THIS change: {attribute_name}

When tagBased=true in the payload you MUST:

1. NOT add any new field or getter/setter to the DTO.
2. Read the logical attribute value using EXACTLY this structure (loop then checks):

   STEP A — Declare a variable and find the tag in ONE loop only:
   - If reqPay.getPayer() is null, return "MISSING_FIELD:Payer".
   - If reqPay.getPayer().getDevice() is null, return "MISSING_FIELD:Payer.Device".
   - Let device = {java_path}.
   - Declare: String <attr>Value = null;
   - If device.{tag_container} != null, loop: for (Tag tag : device.{tag_container})
     - Inside the loop ONLY: if ("{attribute_name}".equalsIgnoreCase(tag.{tag_name_field})) {{ <attr>Value = tag.{tag_value_field}; break; }}
   - Close the for-loop. Do NOT put mandatory or allowedValues checks inside the loop.

   STEP B — After the loop (outside it), apply checks:
   - If mandatory and <attr>Value == null, return "MISSING_FIELD:{device_attr_path}".
   - If <attr>Value != null and not in ValidationRules set, return "INVALID_FIELD_VALUE:{device_attr_path}=" + <attr>Value.

   CRITICAL: Do NOT put the mandatory check or the allowedValues check inside the for-loop.
   The for-loop must contain ONLY the tag lookup and break. All return statements for
   MISSING_FIELD and INVALID_FIELD_VALUE must appear AFTER the for-loop closes.

   CORRECT snippet pattern (use this structure; replace BINDINGMODE with {attribute_name} as needed).
   Pay very close attention to brace placement and if-statement formatting:

   String bindingModeValue = null;
   if (device.getTags() != null) {{
       for (Tag tag : device.getTags()) {{
           if ("BINDINGMODE".equalsIgnoreCase(tag.getName())) {{
               bindingModeValue = tag.getValue();
               break;
           }}
       }}
   }}

   if (bindingModeValue == null) {{
       return "MISSING_FIELD:{device_attr_path}";
   }}

   if (!ValidationRules.REQPAY_PAYER_DEVICE_BINDINGMODE_ALLOWED_VALUES.contains(bindingModeValue)) {{
       return "INVALID_FIELD_VALUE:{device_attr_path}=" + bindingModeValue;
   }}

3. Keep existing validations unchanged.
"""

    prompt = f"""
You are a senior NPCI UPI Switch validation expert.

=================================================
VALIDATIONRULES.JAVA (FULL):
=================================================
{validation_rules_code}

=================================================
REQPAYVALIDATOR.JAVA (FULL):
=================================================
{validator_code}

{java_path_block}
{tag_rules_block}

=================================================
APPROVED CHANGE PAYLOAD:
=================================================
{json.dumps(payload, indent=2)}

=================================================
STRICT RULES (NON-NEGOTIABLE):
=================================================
1. Output ONLY Java code
2. Output TWO FILES separated by:
   ========FILE_BREAK========
3. NO markdown, NO explanations
4. DO NOT change unrelated validations
5. Follow existing error formats EXACTLY
6. NEVER split an if-statement header across lines. The entire header must be on
   a single line in this exact form:
       if (<condition>) {{
           ...
       }}
   In particular, never emit:
       if
       (<condition>) {{
           ...
       }}

=================================================
VALIDATION LOGIC RULES:
=================================================
A. allowedValues: use ValidationRules. Name format:
   <API>_<XMLPATH>_<FIELD>_ALLOWED_VALUES (e.g. REQPAY_PAYER_DEVICE_BINDINGMODE_ALLOWED_VALUES)
B. BEFORE adding a new constant in ValidationRules.java:
   - CHECK the existing ValidationRules.java content for a public static final Set
     that already matches this attribute (same name or same path, e.g. REQPAY_PAYER_DEVICE_<ATTRIBUTE>_ALLOWED_VALUES).
   - If such a constant ALREADY EXISTS, do NOT add it again. Only add/update the
     ReqPayValidator logic that USES that existing constant.
   - Only ADD a new constant if no matching one exists.
C. Use String or Integer based on datatype for the Set.

D. In ReqPayValidator:
   - If fieldBased=true: treat the attribute as a direct Java field on the DTO
     reachable from the javaPath (e.g. txn.getSubProduct()).
   - If tagBased=true: derive the logical value from the container's Tag list
     as described in the TAG-BASED ATTRIBUTE CONTEXT (loop only to find value, then checks after the loop).
   - Null check if mandatory
   - allowedValues check using ValidationRules
   - Return error strings (do NOT throw)
{extra_rules_block}

=================================================
TASK:
=================================================
Update BOTH files correctly. Do not duplicate existing ValidationRules constants.
"""

    response = llm.invoke(prompt)
    output = _sanitize(response.content)

    if "========FILE_BREAK========" not in output:
        raise ValueError("Validator output missing FILE_BREAK")

    rules, validator = output.split("========FILE_BREAK========", 1)
    return rules.strip(), validator.strip()


# ------------------------------------------------
# SAFETY: avoid overwriting with duplicated/conflicting code
# ------------------------------------------------
def _extract_first_code_block(text: str) -> str:
    """Take only the first markdown code block so we never merge two blocks."""
    text = text.strip()
    if not text.startswith("```"):
        return text
    # Find end of opening fence (e.g. ``` or ```java)
    first = text.find("\n")
    if first == -1:
        return text.strip("`").replace("java", "", 1).strip()
    start = first + 1
    # Find closing ```
    rest = text[start:]
    close = rest.find("```")
    if close != -1:
        rest = rest[:close]
    return rest.strip()


def _normalize_line_for_compare(line: str) -> str:
    """Normalize line for duplicate comparison: strip and collapse internal whitespace."""
    return " ".join((line or "").strip().split())


def _deduplicate_consecutive_lines(text: str) -> str:
    """Remove consecutive duplicate lines (LLM sometimes repeats every line)."""
    lines = text.splitlines()
    out = []
    for line in lines:
        prev_norm = _normalize_line_for_compare(out[-1]) if out else None
        if prev_norm is not None and _normalize_line_for_compare(line) == prev_norm:
            continue
        out.append(line)
    return "\n".join(out)


def _remove_whole_content_duplicate(text: str) -> str:
    """If the entire content is repeated (first half of lines == second half), return only first half."""
    lines = text.splitlines()
    n = len(lines)
    if n < 2:
        return text
    half = n // 2
    if lines[:half] == lines[half : 2 * half]:
        return "\n".join(lines[:half])
    return text


# Match "private Type fieldName;" in Java (allow trailing comment/whitespace)
_JAVA_PRIVATE_FIELD_RE = re.compile(r"^\s*private\s+\S+\s+(\w+)\s*;")
_JAVA_ANNOTATION_RE = re.compile(r"^\s*@(XmlAttribute|XmlElement)(\s*\(|\s|$)")


def _remove_duplicate_java_fields(text: str) -> str:
    """
    Remove duplicate field declarations in Java DTOs.
    Keeps the first declaration of each field; drops later ones and their @XmlAttribute/@XmlElement line.
    """
    lines = text.splitlines()
    seen_fields = set()
    skip_indices = set()
    for i, line in enumerate(lines):
        stripped = line.strip()
        m = _JAVA_PRIVATE_FIELD_RE.match(stripped)
        if m:
            name = m.group(1)
            if name in seen_fields:
                skip_indices.add(i)
                # Skip the annotation line above if it's an XML binding annotation
                if i > 0 and _JAVA_ANNOTATION_RE.match(lines[i - 1].strip()):
                    skip_indices.add(i - 1)
            else:
                seen_fields.add(name)
    if not skip_indices:
        return text
    return "\n".join(line for j, line in enumerate(lines) if j not in skip_indices)


def sanitize_java_dto_code(code: str) -> str:
    """Remove duplicate field declarations from Java DTO code. Safe to call on any Java snippet."""
    if not code or "private " not in code:
        return code
    return _remove_duplicate_java_fields(code)



import re

def _fix_tag_loop_structure(code: str) -> str:
    """
    Fix broken Tag loops where the closing braces for
    the if and for blocks are missing after break;
    """

    lines = code.splitlines()
    fixed = []
    inside_tag_loop = False
    break_seen = False

    for line in lines:
        stripped = line.strip()

        if "for (Tag " in stripped:
            inside_tag_loop = True
            break_seen = False

        if inside_tag_loop and "break;" in stripped:
            break_seen = True

        fixed.append(line)

        # if break was seen and next line is NOT closing brace
        if inside_tag_loop and break_seen:
            if stripped.endswith("break;"):
                fixed.append("                }")
                fixed.append("            }")
                inside_tag_loop = False
                break_seen = False

    return "\n".join(fixed)

def _sanitize(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        text = _extract_first_code_block(text)

    text = text.strip().strip("`").strip()

    if text.startswith("java"):
        text = text[4:].lstrip()

    text = _deduplicate_consecutive_lines(text)
    text = _remove_whole_content_duplicate(text)

    # FIX TAG LOOP STRUCTURE
    text = _fix_tag_loop_structure(text)

    # BALANCE BRACES
    text = _balance_java_braces(text)

    if "private " in text and ("class " in text or "package " in text):
        text = _remove_duplicate_java_fields(text)

    return text