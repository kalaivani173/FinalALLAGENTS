from datetime import datetime


def create_partner_manifest(payload: dict, xsd_path: str, openapi_path: str | None = None):
    manifest = {
        "changeId": payload["changeId"],
        "issuer": "NPCI_UPI_SWITCH",
        "changeType": payload["changeType"],
        "apiName": payload["apiName"],
        "summary": payload.get("description"),
        "impactedPaths": [
            {
                "xmlPath": payload.get("xmlPath"),
                "change": payload["changeType"],
                "attribute": {
                    "name": payload.get("attributeName"),
                    "datatype": payload.get("datatype"),
                    "mandatory": payload.get("mandatory", False),
                    "allowedValues": payload.get("allowedValues"),
                },
            }
        ],
        "xsd": {"path": xsd_path},
        "npciStatus": "READY_FOR_ADOPTION",
        "timestamp": datetime.utcnow().isoformat(),
    }
    if openapi_path:
        manifest["openapi"] = {"path": openapi_path}
    return manifest
