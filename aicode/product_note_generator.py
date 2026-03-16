"""
Generate product note document for UPI change manifests.

Used during manifest creation (Option A) when no product note file exists.
Incorporates: description, payload (changeType, impactedPaths, fieldAdditions),
XSD content, and sample dumps.
"""
import json
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)


def generate_product_note(
    change_id: str,
    payload: dict,
    xsd_content: str | None = None,
    samples: str | None = None,
) -> str:
    """
    Generate a product note Markdown document for a UPI change.

    Incorporates:
    - Description / change rationale
    - Change type, API name, impacted paths, field additions
    - XSD schema (when available)
    - Sample request/response dumps (when available)

    Output sections: Change Summary, Business Rationale, PSP/Bank Implementation Requirements,
    Schema Changes, Sample Payloads (if any), Go-Live Notes.
    """
    api_name = payload.get("apiName") or payload.get("api_name") or "API"
    description = payload.get("description") or ""
    change_type = payload.get("changeType") or payload.get("change_type") or ""

    payload_json = json.dumps(payload, indent=2, default=str)
    xsd_section = f"\n\nXSD SCHEMA:\n```xml\n{xsd_content}\n```\n" if xsd_content else "\n\n(No XSD provided)\n"
    samples_section = f"\n\nSAMPLE REQUEST/RESPONSE DUMP:\n```xml\n{samples}\n```\n" if samples else "\n\n(No sample dumps provided)\n"

    prompt = f"""You are an NPCI UPI product documentation expert.

Create a product note document in Markdown format for the following UPI change.

==================================================
CHANGE ID: {change_id}
API NAME: {api_name}
CHANGE TYPE: {change_type}
DESCRIPTION: {description}
==================================================
PAYLOAD (change details, impacted paths, field additions):
{payload_json}
{xsd_section}
{samples_section}
==================================================

Output a Markdown document with these sections (use ## for section headers):

1. **Change Summary** - One paragraph overview of the change
2. **Business Rationale** - Why this change was made (regulatory, product need, etc.)
3. **PSP/Bank Implementation Requirements** - What PSPs and banks must implement (derive from impactedPaths, fieldAdditions)
4. **Schema Changes** - Summary of XSD changes (elements/attributes added or modified)
5. **Sample Payloads** - If samples were provided, include a brief example or reference
6. **Go-Live Notes** - Important dates, migration steps, or rollout considerations

RULES:
- Use clear, professional language for product owners and PSP/Bank implementation teams
- Be concise but complete
- Output ONLY the Markdown document, no preamble or explanation
- Start with a title line: # Product Note: {api_name} ({change_id})
"""

    response = llm.invoke(prompt)
    content = response.content.strip()
    # Remove any accidental markdown code fences around the whole output
    if content.startswith("```") and content.endswith("```"):
        content = content.strip("`").strip()
        if content.startswith("markdown"):
            content = content[8:].strip()
    return content
