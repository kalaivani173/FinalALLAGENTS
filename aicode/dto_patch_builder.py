import re

# Match "private Type fieldName;" so we detect existing fields of any type (String, double, int, etc.)
_PRIVATE_FIELD_RE = re.compile(r"^\s*private\s+\S+\s+(\w+)\s*;\s*$")


def patch_dto_from_xsd(dto_code: str, attributes: list) -> str:
    """
    Adds missing @XmlAttribute fields only.
    Never invents new fields. Skips any attribute that already has a field (any type).
    """

    existing_fields = set()
    for line in dto_code.splitlines():
        m = _PRIVATE_FIELD_RE.match(line.strip())
        if m:
            existing_fields.add(m.group(1))

    additions = []
    for attr in attributes:
        if attr in existing_fields:
            continue
        additions.append(
            f'    @XmlAttribute(name="{attr}")\n'
            f'    private String {attr};\n'
        )

    if not additions:
        return dto_code

    insert_at = dto_code.rfind("}")
    return dto_code[:insert_at] + "\n" + "\n".join(additions) + "\n}"
