def generate_api_validator(api_name: str, rules: list) -> str:
    lines = [
        "package com.npci.upi.validation;",
        "",
        f"import com.npci.upi.dto.Req{api_name};",
        "",
        f"public class Req{api_name}Validator {{",
        "",
        f"    public static String validate(Req{api_name} req) {{"
    ]

    grouped = {}
    for r in rules:
        grouped.setdefault(r["parent"], []).append(r)

    for parent, fields in grouped.items():
        parent_getter = f"get{parent}"

        lines.append(
            f"""        if (req.{parent_getter}() == null) {{
            return "{parent.upper()}_MISSING";
        }}"""
        )

        for f in fields:
            field_getter = f"get{f['field'].capitalize()}"
            lines.append(
                f"""        if (req.{parent_getter}().{field_getter}() == null) {{
            return "{f['field'].upper()}_MISSING";
        }}"""
            )

    lines.extend([
        "        return null;",
        "    }",
        "}"
    ])

    return "\n".join(lines)
