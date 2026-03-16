"""
Quick test for orchestrator endpoints. Run with backend up: python -m uvicorn main:app --port 8000
Usage: python test_orchestrator.py [base_url]
Default base_url: http://localhost:8000
"""
import json
import sys
try:
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib2 import urlopen, Request, HTTPError, URLError

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")
CHANGE_ID = "CHG-TEST-001"


def post_status(agent: str, status: str) -> dict:
    url = f"{BASE}/orchestrator/a2a/status"
    body = json.dumps({"changeId": CHANGE_ID, "agent": agent, "status": status}).encode("utf-8")
    req = Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
    with urlopen(req) as r:
        return json.loads(r.read().decode())


def get_change_status() -> dict:
    url = f"{BASE}/orchestrator/change/{CHANGE_ID}"
    with urlopen(url) as r:
        return json.loads(r.read().decode())


def main():
    print("Orchestrator test (base:", BASE, ")\n")
    # 1. Post statuses
    for agent, status in [("Payer", "RECEIVED"), ("Payee", "APPLIED"), ("Bank_A", "TESTED"), ("Bank_B", "READY")]:
        try:
            out = post_status(agent, status)
            print(f"  POST {agent} -> {status}: {out}")
        except HTTPError as e:
            print(f"  POST {agent} -> {status}: HTTP {e.code} - {e.read().decode()}")
            return
        except URLError as e:
            print(f"  Error: {e}. Is the backend running? (python -m uvicorn main:app --port 8000)")
            return
    # 2. Get status
    print()
    try:
        out = get_change_status()
        print("  GET change status:", json.dumps(out, indent=2))
    except Exception as e:
        print("  GET failed:", e)
        return
    print("\nDone. Check artifacts/orchestrator_state.json for persisted state.")


if __name__ == "__main__":
    main()
