import json
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def map_xml_to_java(xml_path: str, attribute: str, java_index: list):
    """
    Maps XML path like "ReqPay.Txn" or "ReqPay.Payer.Device" to the correct Java DTO.
    Walks the path segments via nested DTO fields so deeper elements (like Device)
    are resolved correctly instead of stopping at the first child.
    """

    parts = xml_path.split(".")
    if len(parts) < 2:
        return None

    root_xml = parts[0]

    # 1️⃣ Find root DTO (e.g., ReqPay)
    root_candidates = [j for j in java_index if root_xml in j.get("xmlRoot", "")]
    if not root_candidates:
        return None

    current_dto = root_candidates[0]

    # 2️⃣ Resolve nested DTOs via field types for each subsequent path segment
    for element in parts[1:]:
        field_type = current_dto["fields"].get(element.lower())
        if not field_type:
            # Can't go deeper – stop at the last successfully resolved DTO
            break

        next_dto = next((j for j in java_index if j["className"] == field_type), None)
        if not next_dto:
            break

        current_dto = next_dto

    # If we never moved past the root and no direct field matched, mapping failed
    if current_dto is root_candidates[0] and len(parts) > 1:
        # There was at least one non-root segment but we couldn't resolve any field
        field_type = current_dto["fields"].get(parts[1].lower())
        if not field_type:
            return None

    # 3️⃣ Deterministic mapping (NO hallucination)
    return {
        "className": current_dto["className"],
        "path": current_dto["path"],
        "reason": "Resolved via nested DTO field type walk"
    }
