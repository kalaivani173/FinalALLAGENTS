"""
Test flow: send a manifest to Payer-agent and verify code change pipeline.
Run with: python test_manifest_flow.py
Requires: .env with OPENAI_API_KEY=sk-... in this folder.
Option A: Start server yourself: python app.py (runs on port 9001)
Option B: This script can start the server for you (set START_SERVER=1).
"""
import json
import os
import subprocess
import sys
import time

# Load .env so OPENAI_API_KEY is set (for server if we start it)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import requests

PORT = int(os.environ.get("PAYER_AGENT_PORT", "9001"))
BASE = f"http://127.0.0.1:{PORT}"

# Flat manifest (no signature) - ADD_VALIDATION for purpose code
MANIFEST = {
    "changeId": "test-purpose-001",
    "issuer": "NPCI_UPI_SWITCH",
    "changeType": "ADD_VALIDATION",
    "apiName": "ReqPay",
    "summary": "Add allowed purpose codes for Txn",
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
    # Optionally start server (so it inherits OPENAI_API_KEY from .env)
    start_server = os.environ.get("START_SERVER", "").strip().lower() in ("1", "true", "yes")
    proc = None
    if start_server:
        print(f"Starting server (port {PORT})...")
        proc = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        time.sleep(10)
        if proc.poll() is not None:
            out, _ = proc.communicate()
            print("Server exited. Output:", out.decode()[-1500:] if out else "none")
            sys.exit(1)

    print("1. Health check...")
    try:
        r = requests.get(f"{BASE}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        print("   Server not reachable. Start it with: python app.py (port 9001)")
        print("   Or run with START_SERVER=1 (and set OPENAI_API_KEY in .env)")
        if proc:
            try:
                out, _ = proc.communicate(timeout=2)
                if out:
                    print("   Server output:", out.decode()[-800:])
            except Exception:
                proc.terminate()
        sys.exit(1)
    r.raise_for_status()
    print("   ", r.json())

    print("\n2. POST /agent/manifest (sending manifest)...")
    r = requests.post(f"{BASE}/agent/manifest", json=MANIFEST, timeout=300)
    print("   Status:", r.status_code)
    if r.status_code != 200:
        print("   Response:", r.text[:500])
        return
    data = r.json()
    print("   changeId:", data.get("changeId"))
    print("   status:", data.get("status"))
    print("   artifacts keys:", list(data.get("artifacts", {}).keys()))

    cid = MANIFEST["changeId"]
    print("\n3. GET /agent/status (all changes)...")
    r = requests.get(f"{BASE}/agent/status", timeout=5)
    r.raise_for_status()
    changes = r.json().get("changes", [])
    for c in changes:
        print("   ", c.get("changeId"), "->", c.get("state"))

    print("\n4. GET /agent/status/" + cid + "...")
    r = requests.get(f"{BASE}/agent/status/{cid}", timeout=5)
    r.raise_for_status()
    d = r.json()
    print("   state:", d.get("state"))
    if d.get("artifacts"):
        print("   artifacts:", json.dumps(d["artifacts"], indent=2)[:400], "...")

    if proc:
        proc.terminate()
        print("\nServer stopped.")
    print("\nDone.")


if __name__ == "__main__":
    main()
