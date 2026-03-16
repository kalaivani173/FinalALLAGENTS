def decide_change(payload: dict) -> str:
    """
    NPCI Rule:
    Any schema change requires NPCI code update
    """
    if payload.get("changeType") in {
        "ADD_XML_ATTRIBUTE",
        "ADD_NEW_API"
    }:
        return "CODE_CHANGE_REQUIRED"

    return "NO_CODE_CHANGE_REQUIRED"
