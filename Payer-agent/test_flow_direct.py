"""
Test manifest flow by calling process_manifest directly (no HTTP).
Run: python test_flow_direct.py
Requires: .env with OPENAI_API_KEY
"""
import asyncio
import json
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from agent.payer_agent import process_manifest

MANIFEST = {
    "changeId": "test-direct-001",
    "issuer": "NPCI_UPI_SWITCH",
    "changeType": "ADD_VALIDATION",
    "apiName": "ReqPay",
    "summary": "Add allowed purpose codes",
    "impactedPaths": [
        {
            "xmlPath": "ReqPay/Txn",
            "change": "ADD_VALIDATION",
            "attribute": {
                "name": "purpose",
                "datatype": "string",
                "mandatory": True,
                "allowedValues": ["00", "20", "31"],
            },
        }
    ],
}


def main():
    if not os.environ.get("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY in .env and run again.")
        return
    print("Calling process_manifest (RAG + LLM + patch apply)...")
    result = asyncio.run(process_manifest(MANIFEST))
    print("Result:", json.dumps(result, indent=2))
    print("\nDone.")


if __name__ == "__main__":
    main()
