"""
Product Kit Generator — FastAPI Router
Generates complete product documentation kits for UPI payment features.
Includes: Circular, Product Note, Tech Specs, Test Cases, XSD, Sample Payloads.
"""

import uuid
import json
import sqlite3
import os
import re
import zipfile
import io
import traceback
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from pathlib import Path

# PDF generator (NPCI-template compliant)
try:
    from pdf_generator import (
        generate_circular_pdf, generate_product_note_pdf,
        generate_tech_specs_pdf, generate_test_cases_pdf,
        generate_xsd_pdf, generate_payloads_pdf,
    )
    _PDF_OK = True
except Exception as _pdf_err:
    _PDF_OK = False
    print(f"[WARN] PDF generator unavailable: {_pdf_err}")

# ─────────────────────────────────────────────────────────────
# Database setup (SQLite, file-backed for persistence)
# ─────────────────────────────────────────────────────────────
_DB_PATH = str(Path(__file__).resolve().parent / "artifacts" / "product_kits.db")
os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)


def _conn():
    c = sqlite3.connect(_DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def _init_db():
    with _conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS product_kits (
            id               TEXT PRIMARY KEY,
            change_request_id TEXT,
            feature_name     TEXT NOT NULL,
            version          TEXT NOT NULL DEFAULT '1.0',
            input_payload    TEXT NOT NULL,
            product_kit      TEXT,
            uploaded_files   TEXT,
            critic_report    TEXT,
            status           TEXT NOT NULL DEFAULT 'draft',
            created_at       TEXT NOT NULL,
            updated_at       TEXT NOT NULL
        )
        """)
        # Migration: add columns if they don't exist (idempotent)
        for col, definition in [
            ("change_request_id", "TEXT"),
            ("uploaded_files",    "TEXT"),
        ]:
            try:
                c.execute(f"ALTER TABLE product_kits ADD COLUMN {col} {definition}")
            except Exception:
                pass
        c.commit()


_init_db()

# ─────────────────────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────────────────────
class ProductKitInput(BaseModel):
    feature_name: str
    version: str = "1.0"
    description: str
    actors: List[str] = []
    constraints: List[str] = []
    impacted_flows: List[str] = []
    regulatory_notes: str = ""
    change_request_id: Optional[str] = None   # Link to existing CR


class RefineRequest(BaseModel):
    section: Optional[str] = None
    feedback: str


class StatusUpdate(BaseModel):
    status: str   # "draft" | "approved"


# Sections that can be uploaded by user
UPLOADABLE_SECTIONS = {
    "circular":                  "circular",
    "product_note":              "product_note",
    "technical_specifications":  "technical_specifications",
    "test_cases":                "test_cases",
    "xsd":                       "xsd",
    "sample_payloads":           "sample_payloads",
}


# ─────────────────────────────────────────────────────────────
# LLM helper (OpenAI via langchain; falls back to deterministic)
# ─────────────────────────────────────────────────────────────
try:
    from langchain_openai import ChatOpenAI
    _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4, max_tokens=4000)
    _LLM_OK = True
except Exception:
    _llm = None
    _LLM_OK = False


def _llm_call(prompt: str, fallback_fn, *args) -> str:
    """Call LLM; on any failure invoke fallback_fn(*args)."""
    if _LLM_OK and _llm:
        try:
            from langchain_core.messages import HumanMessage
            result = _llm.invoke([HumanMessage(content=prompt)])
            return result.content.strip()
        except Exception:
            pass
    return fallback_fn(*args)


# ─────────────────────────────────────────────────────────────
# Prompt builder
# ─────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are a senior payments standards expert for NPCI (National Payments Corporation of India) specialising in UPI.
You generate complete, production-quality Product Kits for new UPI features.
STRICT RULES:
1. Never use "TBD", "placeholder", or example values from templates.
2. All values must be derived from the feature input provided.
3. API schemas in Technical Specs, XSD, and Sample Payloads MUST be consistent.
4. Test cases must align with business rules stated in the Circular and Product Note.
5. Return ONLY valid JSON — no markdown fences, no commentary outside JSON.
"""

_KIT_PROMPT_TEMPLATE = """
{system}

INPUT FEATURE:
Feature Name: {feature_name}
Version: {version}
Description: {description}
Actors: {actors}
Constraints: {constraints}
Impacted Flows: {impacted_flows}
Regulatory Notes: {regulatory_notes}

REQUIRED OUTPUT — return a single JSON object with exactly these keys:

{{
  "circular": "<full NPCI circular text with sections: Circular No, Date, Subject, Background, Objective, Scope, Applicability, Implementation Guidelines, Compliance, Effective Date>",
  "product_note": "<full product note text with sections: Executive Summary, Business Objective, Key Benefits, Actors & Roles, Business Flow, Constraints & Limitations, Regulatory Compliance>",
  "technical_specifications": {{
    "api_name": "string",
    "version": "string",
    "base_url": "string",
    "endpoints": [
      {{
        "method": "POST|GET",
        "path": "string",
        "description": "string",
        "request": {{
          "headers": {{}},
          "body": {{}}
        }},
        "response": {{
          "success": {{}},
          "error": {{}}
        }},
        "error_codes": [
          {{ "code": "string", "message": "string", "http_status": 400 }}
        ]
      }}
    ],
    "field_definitions": [
      {{ "field": "string", "type": "string", "mandatory": true, "description": "string", "validation": "string" }}
    ],
    "flow_description": "string"
  }},
  "test_cases": [
    {{
      "tc_id": "TC-001",
      "category": "Positive|Negative|Edge",
      "title": "string",
      "preconditions": "string",
      "input": {{}},
      "expected_output": {{}},
      "validation_points": ["string"]
    }}
  ],
  "xsd": "<?xml version='1.0' encoding='UTF-8'?><xs:schema ...>...</xs:schema>",
  "sample_payloads": {{
    "success_request": {{}},
    "success_response": {{}},
    "error_request": {{}},
    "error_response": {{}}
  }}
}}

Generate at least 3 endpoints, 8+ field definitions, 6+ test cases (mix of Positive/Negative/Edge), and a complete XSD.
"""

_REVIEW_PROMPT_TEMPLATE = """
{system}

You are reviewing a generated Product Kit for quality, consistency, and completeness.

PRODUCT KIT:
{kit_json}

Return a JSON critic report:
{{
  "overall_score": 85,
  "issues": [
    {{ "section": "string", "severity": "critical|warning|info", "description": "string", "suggestion": "string" }}
  ],
  "consistency_checks": {{
    "xsd_matches_payloads": true,
    "test_cases_match_api": true,
    "circular_aligns_product_note": true
  }},
  "summary": "string"
}}
"""

_REFINE_PROMPT_TEMPLATE = """
{system}

Refine the following section of a Product Kit based on feedback.

CURRENT CONTENT:
{current_content}

FEEDBACK:
{feedback}

Return ONLY the refined content for the section — same format/structure as the original.
"""


def _build_kit_prompt(inp: ProductKitInput) -> str:
    return _KIT_PROMPT_TEMPLATE.format(
        system=_SYSTEM_PROMPT,
        feature_name=inp.feature_name,
        version=inp.version,
        description=inp.description,
        actors=", ".join(inp.actors) if inp.actors else "PSP, Payer, Payee, Bank",
        constraints="; ".join(inp.constraints) if inp.constraints else "None specified",
        impacted_flows=", ".join(inp.impacted_flows) if inp.impacted_flows else "Payment, Refund",
        regulatory_notes=inp.regulatory_notes or "Standard UPI regulatory framework applies",
    )


# ─────────────────────────────────────────────────────────────
# Deterministic fallback kit builder
# ─────────────────────────────────────────────────────────────
def _deterministic_kit(inp: ProductKitInput) -> dict:
    """Build a well-structured Product Kit without LLM."""
    fn = inp.feature_name
    ver = inp.version
    today = datetime.now().strftime("%d %B %Y")
    yr = datetime.now().year
    actors = inp.actors or ["PSP", "Payer", "Payee", "Acquiring Bank", "Issuing Bank"]
    flows = inp.impacted_flows or ["Payment Initiation", "Authorization", "Settlement"]
    constraints = inp.constraints or ["Transaction limit per day", "Supported UPI ID formats"]

    # ── Circular ──────────────────────────────────────────────
    circular = f"""NATIONAL PAYMENTS CORPORATION OF INDIA
NPCI CIRCULAR
Circular No.: NPCI/UPI/{yr}/{str(uuid.uuid4().int)[:4]}
Date: {today}
Subject: Introduction of {fn} (Version {ver}) in Unified Payments Interface (UPI)

1. BACKGROUND
The National Payments Corporation of India (NPCI) has been continuously enhancing the UPI ecosystem to support evolving payment requirements. This circular introduces the {fn} feature to further strengthen UPI's capabilities in line with regulatory guidelines.

2. OBJECTIVE
The objective of this circular is to:
a) Define the technical and operational framework for {fn}
b) Specify compliance requirements for all UPI participants
c) Establish implementation timelines and certification criteria

3. SCOPE
This circular is applicable to all UPI-enabled entities including:
{chr(10).join(f'- {a}' for a in actors)}

4. FEATURE DESCRIPTION
{inp.description}

5. IMPACTED FLOWS
{chr(10).join(f'- {f}' for f in flows)}

6. IMPLEMENTATION GUIDELINES
a) All member banks and PSPs must implement {fn} by the effective date
b) Certification testing must be completed as per the test case matrix
c) Integration with NPCI switch must follow the updated XSD and API specifications
d) Any issues during implementation must be reported to NPCI technical helpdesk

7. COMPLIANCE
{inp.regulatory_notes or 'All participating entities must comply with applicable RBI regulations and NPCI operating guidelines.'}

Constraints to be adhered to:
{chr(10).join(f'- {c}' for c in constraints)}

8. EFFECTIVE DATE
This circular comes into effect 90 days from the date of issuance. Member banks and PSPs must complete User Acceptance Testing (UAT) within 60 days.

9. CONTACT
For queries, contact NPCI Technical Support at upi.support@npci.org.in

For and on behalf of
National Payments Corporation of India
(Chief Operating Officer – UPI)"""

    # ── Product Note ──────────────────────────────────────────
    product_note = f"""PRODUCT NOTE
Feature: {fn}
Version: {ver}
Date: {today}
Classification: Internal — UPI Product Team

1. EXECUTIVE SUMMARY
{fn} is a new capability introduced in UPI {ver} to {inp.description.lower()[:200]}. This feature enhances the UPI ecosystem by providing a structured, standards-compliant mechanism for participating entities.

2. BUSINESS OBJECTIVE
- Enable seamless {fn.lower()} for UPI participants
- Reduce manual intervention and processing time
- Improve transparency and auditability of transactions
- Comply with regulatory requirements

3. KEY BENEFITS
- Faster processing with standardized API contracts
- Reduced operational overhead for member banks
- Enhanced user experience for payers and payees
- Real-time status updates and notifications
- Comprehensive audit trail for dispute resolution

4. ACTORS & ROLES
{chr(10).join(f'- {a}: Participates in {fn} as per defined role in the UPI ecosystem' for a in actors)}

5. BUSINESS FLOW
Step 1: {actors[0] if actors else 'Initiator'} initiates {fn} request
Step 2: Request validated at PSP layer against business rules
Step 3: NPCI switch processes and routes request
Step 4: {actors[-1] if len(actors) > 1 else 'Recipient'} acknowledges and responds
Step 5: Settlement/confirmation sent back through the chain
Step 6: Audit log updated across all participants

6. CONSTRAINTS & LIMITATIONS
{chr(10).join(f'- {c}' for c in constraints)}

7. REGULATORY COMPLIANCE
{inp.regulatory_notes or 'This feature complies with RBI Payment System Guidelines, NPCI UPI Operating Circulars, and applicable data protection regulations.'}

8. ROLLOUT PLAN
- Phase 1 (Weeks 1-4): Technical integration and internal testing
- Phase 2 (Weeks 5-8): UAT with pilot PSPs
- Phase 3 (Weeks 9-12): Production rollout to all participants"""

    # ── Technical Specs ───────────────────────────────────────
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', fn).lower()
    tech_specs = {
        "api_name": f"UPI {fn} API",
        "version": ver,
        "base_url": f"/api/v{ver.split('.')[0]}/upi/{safe_name}",
        "endpoints": [
            {
                "method": "POST",
                "path": f"/api/v{ver.split('.')[0]}/upi/{safe_name}/initiate",
                "description": f"Initiate a new {fn} request",
                "request": {
                    "headers": {"Content-Type": "application/json", "X-API-Key": "string", "X-Request-ID": "UUID"},
                    "body": {
                        "reqId": "string (UUID, mandatory)",
                        "timestamp": "string (ISO-8601, mandatory)",
                        "version": ver,
                        "payerId": "string (VPA, mandatory)",
                        "payeeId": "string (VPA, mandatory)",
                        "amount": "number (decimal, mandatory)",
                        "currency": "INR",
                        "purpose": f"string — {fn} purpose code",
                        "additionalInfo": {}
                    }
                },
                "response": {
                    "success": {
                        "status": "SUCCESS",
                        "reqId": "string",
                        "txnId": "string (NPCI Transaction ID)",
                        "timestamp": "string",
                        "message": "Request accepted"
                    },
                    "error": {
                        "status": "FAILURE",
                        "reqId": "string",
                        "errorCode": "string",
                        "errorMessage": "string"
                    }
                },
                "error_codes": [
                    {"code": "E001", "message": "Invalid VPA format", "http_status": 400},
                    {"code": "E002", "message": "Amount exceeds daily limit", "http_status": 422},
                    {"code": "E003", "message": "Payer account insufficient balance", "http_status": 422},
                    {"code": "E004", "message": "Duplicate request ID", "http_status": 409},
                    {"code": "E005", "message": "Service temporarily unavailable", "http_status": 503}
                ]
            },
            {
                "method": "GET",
                "path": f"/api/v{ver.split('.')[0]}/upi/{safe_name}/status/{{reqId}}",
                "description": f"Query status of a {fn} request",
                "request": {
                    "headers": {"X-API-Key": "string", "X-Request-ID": "UUID"},
                    "path_params": {"reqId": "UUID of original request"}
                },
                "response": {
                    "success": {
                        "reqId": "string",
                        "txnId": "string",
                        "status": "PENDING|SUCCESS|FAILED|EXPIRED",
                        "timestamp": "string",
                        "details": {}
                    },
                    "error": {
                        "status": "FAILURE",
                        "errorCode": "E404",
                        "errorMessage": "Request not found"
                    }
                },
                "error_codes": [
                    {"code": "E404", "message": "Request not found", "http_status": 404},
                    {"code": "E401", "message": "Unauthorized", "http_status": 401}
                ]
            },
            {
                "method": "POST",
                "path": f"/api/v{ver.split('.')[0]}/upi/{safe_name}/callback",
                "description": f"Callback notification for {fn} completion",
                "request": {
                    "headers": {"X-Signature": "HMAC-SHA256", "Content-Type": "application/json"},
                    "body": {
                        "reqId": "string",
                        "txnId": "string",
                        "status": "SUCCESS|FAILED",
                        "timestamp": "string",
                        "details": {}
                    }
                },
                "response": {
                    "success": {"acknowledged": True},
                    "error": {"acknowledged": False, "reason": "string"}
                },
                "error_codes": [
                    {"code": "E400", "message": "Invalid signature", "http_status": 400}
                ]
            }
        ],
        "field_definitions": [
            {"field": "reqId", "type": "string (UUID v4)", "mandatory": True, "description": "Unique request identifier generated by initiating PSP", "validation": "Must be a valid UUID v4, unique per transaction"},
            {"field": "timestamp", "type": "string (ISO-8601)", "mandatory": True, "description": "Request creation timestamp in UTC", "validation": "Must be within ±5 minutes of server time"},
            {"field": "version", "type": "string", "mandatory": True, "description": "API version", "validation": f"Must be '{ver}'"},
            {"field": "payerId", "type": "string (VPA)", "mandatory": True, "description": "Virtual Payment Address of the payer", "validation": "Format: user@bank, max 255 chars"},
            {"field": "payeeId", "type": "string (VPA)", "mandatory": True, "description": "Virtual Payment Address of the payee", "validation": "Format: user@bank, max 255 chars"},
            {"field": "amount", "type": "number", "mandatory": True, "description": "Transaction amount in INR", "validation": "Min: 0.01, Max: 100000.00, 2 decimal places"},
            {"field": "currency", "type": "string", "mandatory": True, "description": "ISO 4217 currency code", "validation": "Must be 'INR'"},
            {"field": "purpose", "type": "string", "mandatory": True, "description": f"Purpose of {fn}", "validation": "Max 50 chars, alphanumeric"},
            {"field": "txnId", "type": "string", "mandatory": False, "description": "NPCI-assigned transaction ID (in response)", "validation": "Read-only, assigned by switch"}
        ],
        "flow_description": f"1. PSP constructs {fn} request with reqId and submits to NPCI switch\n2. Switch validates fields, checks duplicate reqId\n3. Switch routes to destination based on payeeId VPA resolution\n4. Destination PSP/bank processes and acknowledges\n5. Switch sends callback to originating PSP with final status\n6. Both parties update their records and notify end users"
    }

    # ── Test Cases ────────────────────────────────────────────
    test_cases = [
        {
            "tc_id": "TC-001",
            "category": "Positive",
            "title": f"Successful {fn} — Happy Path",
            "preconditions": "Valid payer VPA, sufficient balance, valid payee VPA",
            "input": {"reqId": "550e8400-e29b-41d4-a716-446655440001", "payerId": "alice@oksbi", "payeeId": "merchant@ybl", "amount": 500.00, "currency": "INR", "purpose": "Test payment"},
            "expected_output": {"status": "SUCCESS", "txnId": "NPCI20240001", "http_status": 200},
            "validation_points": ["Response contains valid txnId", "Status is SUCCESS", "Callback received within 30s"]
        },
        {
            "tc_id": "TC-002",
            "category": "Positive",
            "title": f"{fn} with minimum allowed amount",
            "preconditions": "Valid accounts, amount = ₹0.01",
            "input": {"reqId": "550e8400-e29b-41d4-a716-446655440002", "payerId": "user@oksbi", "payeeId": "test@ybl", "amount": 0.01, "currency": "INR", "purpose": "Min amount test"},
            "expected_output": {"status": "SUCCESS", "http_status": 200},
            "validation_points": ["Minimum amount processed successfully", "No rounding errors in amount"]
        },
        {
            "tc_id": "TC-003",
            "category": "Negative",
            "title": "Invalid payer VPA format",
            "preconditions": "None",
            "input": {"reqId": "550e8400-e29b-41d4-a716-446655440003", "payerId": "invalid-vpa-format", "payeeId": "merchant@ybl", "amount": 100.00, "currency": "INR", "purpose": "Test"},
            "expected_output": {"status": "FAILURE", "errorCode": "E001", "http_status": 400},
            "validation_points": ["Error code E001 returned", "Descriptive error message present", "No transaction created"]
        },
        {
            "tc_id": "TC-004",
            "category": "Negative",
            "title": "Amount exceeds daily limit",
            "preconditions": "Payer has reached daily transaction limit",
            "input": {"reqId": "550e8400-e29b-41d4-a716-446655440004", "payerId": "user@oksbi", "payeeId": "merchant@ybl", "amount": 200000.00, "currency": "INR", "purpose": "Over limit"},
            "expected_output": {"status": "FAILURE", "errorCode": "E002", "http_status": 422},
            "validation_points": ["Error code E002 returned", "No debit from payer account"]
        },
        {
            "tc_id": "TC-005",
            "category": "Negative",
            "title": "Duplicate request ID",
            "preconditions": "reqId already used in a previous successful transaction",
            "input": {"reqId": "550e8400-e29b-41d4-a716-446655440001", "payerId": "alice@oksbi", "payeeId": "merchant@ybl", "amount": 500.00, "currency": "INR", "purpose": "Duplicate"},
            "expected_output": {"status": "FAILURE", "errorCode": "E004", "http_status": 409},
            "validation_points": ["Idempotency enforced", "Original transaction not affected", "Error E004 returned"]
        },
        {
            "tc_id": "TC-006",
            "category": "Edge",
            "title": "Boundary amount — exactly ₹1,00,000",
            "preconditions": "Valid accounts, amount at maximum limit",
            "input": {"reqId": "550e8400-e29b-41d4-a716-446655440006", "payerId": "user@oksbi", "payeeId": "merchant@ybl", "amount": 100000.00, "currency": "INR", "purpose": "Max limit"},
            "expected_output": {"status": "SUCCESS", "http_status": 200},
            "validation_points": ["Maximum boundary amount accepted", "Amount processed without truncation"]
        },
        {
            "tc_id": "TC-007",
            "category": "Edge",
            "title": "Timestamp skew — request 4 minutes old",
            "preconditions": "Request created 4 minutes before submission (within ±5 min tolerance)",
            "input": {"reqId": "550e8400-e29b-41d4-a716-446655440007", "timestamp": "<4 minutes ago>", "payerId": "user@oksbi", "payeeId": "merchant@ybl", "amount": 100.00, "currency": "INR", "purpose": "Skew test"},
            "expected_output": {"status": "SUCCESS", "http_status": 200},
            "validation_points": ["Request within tolerance window accepted", "Timestamp stored accurately"]
        },
        {
            "tc_id": "TC-008",
            "category": "Edge",
            "title": "Timestamp skew — request 6 minutes old (rejected)",
            "preconditions": "Request created 6 minutes before submission (outside ±5 min tolerance)",
            "input": {"reqId": "550e8400-e29b-41d4-a716-446655440008", "timestamp": "<6 minutes ago>", "payerId": "user@oksbi", "payeeId": "merchant@ybl", "amount": 100.00, "currency": "INR", "purpose": "Stale test"},
            "expected_output": {"status": "FAILURE", "errorCode": "E_STALE_REQUEST", "http_status": 400},
            "validation_points": ["Stale request rejected", "Security policy enforced"]
        }
    ]

    # ── XSD ───────────────────────────────────────────────────
    xsd = f"""<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://npci.org/upi/{safe_name}/v{ver.replace('.', '_')}"
           xmlns:tns="http://npci.org/upi/{safe_name}/v{ver.replace('.', '_')}"
           elementFormDefault="qualified" attributeFormDefault="unqualified"
           version="{ver}">

  <!-- ═══ {fn} Request ═══ -->
  <xs:element name="{safe_name}Req" type="tns:{safe_name}ReqType"/>
  <xs:complexType name="{safe_name}ReqType">
    <xs:sequence>
      <xs:element name="Head" type="tns:HeadType"/>
      <xs:element name="Txn" type="tns:TxnType"/>
      <xs:element name="Payer" type="tns:PayerType"/>
      <xs:element name="Payee" type="tns:PayeeType"/>
      <xs:element name="AdditionalInfo" type="tns:AdditionalInfoType" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>

  <!-- ═══ {fn} Response ═══ -->
  <xs:element name="{safe_name}Resp" type="tns:{safe_name}RespType"/>
  <xs:complexType name="{safe_name}RespType">
    <xs:sequence>
      <xs:element name="Head" type="tns:HeadType"/>
      <xs:element name="Txn" type="tns:TxnType"/>
      <xs:element name="Result" type="tns:ResultType"/>
    </xs:sequence>
  </xs:complexType>

  <!-- ═══ Header ═══ -->
  <xs:complexType name="HeadType">
    <xs:attribute name="ver" type="xs:string" use="required"/>
    <xs:attribute name="ts" type="xs:dateTime" use="required"/>
    <xs:attribute name="orgId" type="xs:string" use="required"/>
    <xs:attribute name="msgId" type="xs:string" use="required"/>
  </xs:complexType>

  <!-- ═══ Transaction ═══ -->
  <xs:complexType name="TxnType">
    <xs:attribute name="id" type="xs:string" use="required"/>
    <xs:attribute name="refId" type="xs:string" use="optional"/>
    <xs:attribute name="ts" type="xs:dateTime" use="required"/>
    <xs:attribute name="type" type="tns:TxnTypeEnum" use="required"/>
    <xs:attribute name="note" type="xs:string" use="optional"/>
    <xs:attribute name="purpose" type="xs:string" use="optional"/>
    <xs:attribute name="initMode" type="xs:string" use="optional"/>
  </xs:complexType>
  <xs:simpleType name="TxnTypeEnum">
    <xs:restriction base="xs:string">
      <xs:enumeration value="PAY"/>
      <xs:enumeration value="COLLECT"/>
      <xs:enumeration value="REFUND"/>
    </xs:restriction>
  </xs:simpleType>

  <!-- ═══ Payer ═══ -->
  <xs:complexType name="PayerType">
    <xs:sequence>
      <xs:element name="Ac" type="tns:AccountType"/>
      <xs:element name="Creds" type="tns:CredsType"/>
    </xs:sequence>
    <xs:attribute name="name" type="xs:string" use="optional"/>
    <xs:attribute name="type" type="xs:string" use="required"/>
    <xs:attribute name="addr" type="xs:string" use="required"/>
  </xs:complexType>

  <!-- ═══ Payee ═══ -->
  <xs:complexType name="PayeeType">
    <xs:sequence>
      <xs:element name="Ac" type="tns:AccountType" minOccurs="0"/>
    </xs:sequence>
    <xs:attribute name="name" type="xs:string" use="optional"/>
    <xs:attribute name="type" type="xs:string" use="required"/>
    <xs:attribute name="addr" type="xs:string" use="required"/>
    <xs:attribute name="merchantCatCode" type="xs:string" use="optional"/>
  </xs:complexType>

  <!-- ═══ Account ═══ -->
  <xs:complexType name="AccountType">
    <xs:attribute name="addrType" type="xs:string" use="required"/>
    <xs:attribute name="mmid" type="xs:string" use="optional"/>
    <xs:attribute name="mobile" type="xs:string" use="optional"/>
    <xs:attribute name="accType" type="xs:string" use="optional"/>
    <xs:attribute name="ifsc" type="xs:string" use="optional"/>
    <xs:attribute name="acNum" type="xs:string" use="optional"/>
  </xs:complexType>

  <!-- ═══ Credentials ═══ -->
  <xs:complexType name="CredsType">
    <xs:sequence>
      <xs:element name="Cred" maxOccurs="unbounded">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="Data">
              <xs:complexType>
                <xs:attribute name="code" type="xs:string" use="required"/>
                <xs:attribute name="ki" type="xs:string" use="optional"/>
                <xs:attribute name="encryptedBase64" type="xs:base64Binary" use="required"/>
              </xs:complexType>
            </xs:element>
          </xs:sequence>
          <xs:attribute name="type" type="xs:string" use="required"/>
          <xs:attribute name="subType" type="xs:string" use="optional"/>
        </xs:complexType>
      </xs:element>
    </xs:sequence>
  </xs:complexType>

  <!-- ═══ Result ═══ -->
  <xs:complexType name="ResultType">
    <xs:attribute name="errCode" type="xs:string" use="optional"/>
    <xs:attribute name="errMsg" type="xs:string" use="optional"/>
    <xs:attribute name="info" type="xs:string" use="optional"/>
    <xs:attribute name="status" type="tns:StatusEnum" use="required"/>
    <xs:attribute name="txnId" type="xs:string" use="optional"/>
    <xs:attribute name="ts" type="xs:dateTime" use="optional"/>
  </xs:complexType>
  <xs:simpleType name="StatusEnum">
    <xs:restriction base="xs:string">
      <xs:enumeration value="SUCCESS"/>
      <xs:enumeration value="FAILURE"/>
      <xs:enumeration value="PENDING"/>
    </xs:restriction>
  </xs:simpleType>

  <!-- ═══ Additional Info ═══ -->
  <xs:complexType name="AdditionalInfoType">
    <xs:sequence>
      <xs:element name="Tag" minOccurs="0" maxOccurs="unbounded">
        <xs:complexType>
          <xs:attribute name="name" type="xs:string" use="required"/>
          <xs:attribute name="value" type="xs:string" use="required"/>
        </xs:complexType>
      </xs:element>
    </xs:sequence>
  </xs:complexType>

</xs:schema>"""

    # ── Sample Payloads ───────────────────────────────────────
    req_id_ok = "550e8400-e29b-41d4-a716-446655440099"
    txn_id = "NPCI202400010099"
    now_ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000+00:00")

    sample_payloads = {
        "success_request": {
            "reqId": req_id_ok,
            "timestamp": now_ts,
            "version": ver,
            "payerId": "alice@oksbi",
            "payeeId": "merchant@ybl",
            "amount": 250.00,
            "currency": "INR",
            "purpose": fn[:30],
            "additionalInfo": {"feature": fn, "channel": "UPI"}
        },
        "success_response": {
            "status": "SUCCESS",
            "reqId": req_id_ok,
            "txnId": txn_id,
            "timestamp": now_ts,
            "message": f"{fn} processed successfully",
            "details": {"approvalCode": "AUTH001", "rrn": "123456789012"}
        },
        "error_request": {
            "reqId": "550e8400-e29b-41d4-a716-446655440098",
            "timestamp": now_ts,
            "version": ver,
            "payerId": "invalid-vpa",
            "payeeId": "merchant@ybl",
            "amount": 100.00,
            "currency": "INR",
            "purpose": fn[:30]
        },
        "error_response": {
            "status": "FAILURE",
            "reqId": "550e8400-e29b-41d4-a716-446655440098",
            "errorCode": "E001",
            "errorMessage": "Invalid VPA format for payerId",
            "timestamp": now_ts
        }
    }

    return {
        "circular": circular,
        "product_note": product_note,
        "technical_specifications": tech_specs,
        "test_cases": test_cases,
        "xsd": xsd,
        "sample_payloads": sample_payloads
    }


def _deterministic_review(kit: dict) -> dict:
    """Generate a basic quality review without LLM."""
    issues = []
    tc_count = len(kit.get("test_cases", []))
    ep_count = len((kit.get("technical_specifications") or {}).get("endpoints", []))

    if tc_count < 6:
        issues.append({"section": "test_cases", "severity": "warning", "description": f"Only {tc_count} test cases found", "suggestion": "Add at least 6 test cases covering Positive, Negative, and Edge scenarios"})
    if ep_count < 2:
        issues.append({"section": "technical_specifications", "severity": "warning", "description": f"Only {ep_count} endpoint(s) defined", "suggestion": "Define initiate, status query, and callback endpoints at minimum"})
    if not kit.get("xsd", "").startswith("<?xml"):
        issues.append({"section": "xsd", "severity": "critical", "description": "XSD does not start with XML declaration", "suggestion": "Ensure XSD is valid XML with proper namespace declarations"})

    return {
        "overall_score": max(60, 100 - len(issues) * 10),
        "issues": issues,
        "consistency_checks": {
            "xsd_matches_payloads": True,
            "test_cases_match_api": tc_count >= 6,
            "circular_aligns_product_note": True
        },
        "summary": f"Product Kit has {tc_count} test cases and {ep_count} endpoints. {'Looks good overall.' if not issues else 'Some improvements recommended.'}"
    }


# ─────────────────────────────────────────────────────────────
# DB helpers
# ─────────────────────────────────────────────────────────────
def _row_to_dict(row) -> dict:
    if row is None:
        return None
    d = dict(row)
    for key in ("input_payload", "product_kit", "critic_report"):
        if d.get(key):
            try:
                d[key] = json.loads(d[key])
            except Exception:
                pass
    return d


def _get_kit(kit_id: str) -> dict:
    with _conn() as c:
        row = c.execute("SELECT * FROM product_kits WHERE id = ?", (kit_id,)).fetchone()
    return _row_to_dict(row)


# ─────────────────────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────────────────────
router = APIRouter(prefix="/product-kit", tags=["Product Kit Generator"])


@router.post("/generate")
def generate_product_kit(inp: ProductKitInput):
    """Generate a complete Product Kit from feature input."""
    kit_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    # Build prompt and call LLM
    prompt = _build_kit_prompt(inp)

    def _fallback(_inp):
        return json.dumps(_deterministic_kit(_inp))

    raw = _llm_call(prompt, _fallback, inp)

    # Parse JSON response
    kit_data = None
    try:
        # Strip markdown fences if present
        clean = re.sub(r'^```(?:json)?\s*', '', raw.strip(), flags=re.MULTILINE)
        clean = re.sub(r'```\s*$', '', clean.strip(), flags=re.MULTILINE)
        kit_data = json.loads(clean)
    except Exception:
        # Last resort: use deterministic
        kit_data = _deterministic_kit(inp)

    # Persist
    cr_id = inp.change_request_id or ""
    with _conn() as c:
        c.execute(
            """INSERT INTO product_kits
               (id, change_request_id, feature_name, version, input_payload, product_kit,
                uploaded_files, status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (kit_id, cr_id, inp.feature_name, inp.version,
             json.dumps(inp.model_dump()), json.dumps(kit_data),
             json.dumps({}), "draft", now, now)
        )
        c.commit()

    return {"id": kit_id, "change_request_id": cr_id, "feature_name": inp.feature_name,
            "version": inp.version, "status": "draft",
            "product_kit": kit_data, "created_at": now}


@router.post("/{kit_id}/review")
def review_product_kit(kit_id: str):
    """Run an AI critic review on a generated Product Kit."""
    kit_record = _get_kit(kit_id)
    if not kit_record:
        raise HTTPException(status_code=404, detail="Product kit not found")

    kit_data = kit_record.get("product_kit") or {}
    prompt = _REVIEW_PROMPT_TEMPLATE.format(
        system=_SYSTEM_PROMPT,
        kit_json=json.dumps(kit_data, indent=2)[:8000]
    )

    def _fb(kd):
        return json.dumps(_deterministic_review(kd))

    raw = _llm_call(prompt, _fb, kit_data)

    critic = None
    try:
        clean = re.sub(r'^```(?:json)?\s*', '', raw.strip(), flags=re.MULTILINE)
        clean = re.sub(r'```\s*$', '', clean.strip(), flags=re.MULTILINE)
        critic = json.loads(clean)
    except Exception:
        critic = _deterministic_review(kit_data)

    now = datetime.utcnow().isoformat()
    with _conn() as c:
        c.execute(
            "UPDATE product_kits SET critic_report = ?, updated_at = ? WHERE id = ?",
            (json.dumps(critic), now, kit_id)
        )
        c.commit()

    return {"id": kit_id, "critic_report": critic, "updated_at": now}


@router.post("/{kit_id}/refine")
def refine_product_kit(kit_id: str, body: RefineRequest):
    """Refine a specific section (or whole kit) based on feedback."""
    kit_record = _get_kit(kit_id)
    if not kit_record:
        raise HTTPException(status_code=404, detail="Product kit not found")

    kit_data = kit_record.get("product_kit") or {}
    section = body.section

    if section and section in kit_data:
        current_content = json.dumps(kit_data[section]) if isinstance(kit_data[section], (dict, list)) else kit_data[section]
        prompt = _REFINE_PROMPT_TEMPLATE.format(
            system=_SYSTEM_PROMPT,
            current_content=current_content[:5000],
            feedback=body.feedback
        )
        raw = _llm_call(prompt, lambda: current_content)
        try:
            clean = re.sub(r'^```(?:json)?\s*', '', raw.strip(), flags=re.MULTILINE)
            clean = re.sub(r'```\s*$', '', clean.strip(), flags=re.MULTILINE)
            kit_data[section] = json.loads(clean)
        except Exception:
            kit_data[section] = raw
    else:
        # Refine full kit: regenerate with feedback added to description
        inp_data = kit_record.get("input_payload") or {}
        if isinstance(inp_data, dict):
            inp_data["description"] = (inp_data.get("description", "") + f"\n\nRefinement feedback: {body.feedback}")
            try:
                inp_obj = ProductKitInput(**inp_data)
                kit_data = _deterministic_kit(inp_obj)
            except Exception:
                pass

    now = datetime.utcnow().isoformat()
    with _conn() as c:
        c.execute(
            "UPDATE product_kits SET product_kit = ?, updated_at = ? WHERE id = ?",
            (json.dumps(kit_data), now, kit_id)
        )
        c.commit()

    return {"id": kit_id, "product_kit": kit_data, "updated_at": now}


@router.get("/{kit_id}")
def get_product_kit(kit_id: str):
    """Retrieve a product kit by ID."""
    record = _get_kit(kit_id)
    if not record:
        raise HTTPException(status_code=404, detail="Product kit not found")
    return record


@router.get("/")
def list_product_kits():
    """List all product kits (summary view)."""
    with _conn() as c:
        rows = c.execute(
            "SELECT id, feature_name, version, status, created_at, updated_at FROM product_kits ORDER BY created_at DESC"
        ).fetchall()
    return {"data": [dict(r) for r in rows]}


@router.patch("/{kit_id}/status")
def update_kit_status(kit_id: str, body: StatusUpdate):
    """Update kit status (draft → approved)."""
    record = _get_kit(kit_id)
    if not record:
        raise HTTPException(status_code=404, detail="Product kit not found")
    if body.status not in ("draft", "approved"):
        raise HTTPException(status_code=400, detail="Status must be 'draft' or 'approved'")
    now = datetime.utcnow().isoformat()
    with _conn() as c:
        c.execute("UPDATE product_kits SET status = ?, updated_at = ? WHERE id = ?", (body.status, now, kit_id))
        c.commit()
    return {"id": kit_id, "status": body.status, "updated_at": now}


# ─────────────────────────────────────────────────────────────
# Section Upload — user provides their own file for a section
# ─────────────────────────────────────────────────────────────
@router.post("/{kit_id}/upload-section")
async def upload_section(
    kit_id: str,
    section: str = Form(...),       # e.g. "circular", "product_note", "xsd"
    file: UploadFile = File(...),
):
    """Upload a user-provided file for a specific Product Kit section.
    Stores the raw bytes as base64 in uploaded_files JSON and marks
    that section as user-supplied (not AI-generated).
    Accepts: PDF, DOCX, TXT, XML, JSON files.
    """
    record = _get_kit(kit_id)
    if not record:
        raise HTTPException(status_code=404, detail="Product kit not found")
    if section not in UPLOADABLE_SECTIONS:
        raise HTTPException(status_code=400,
                            detail=f"Unknown section '{section}'. Valid: {list(UPLOADABLE_SECTIONS)}")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:   # 10 MB guard
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")

    import base64
    uploaded = {}
    raw_up = record.get("uploaded_files")
    if isinstance(raw_up, dict):
        uploaded = raw_up
    elif isinstance(raw_up, str):
        try:
            uploaded = json.loads(raw_up)
        except Exception:
            uploaded = {}

    uploaded[section] = {
        "filename": file.filename,
        "content_type": file.content_type or "application/octet-stream",
        "data_b64": base64.b64encode(content).decode("utf-8"),
        "size": len(content),
        "uploaded_at": datetime.utcnow().isoformat(),
        "source": "user_upload",
    }

    now = datetime.utcnow().isoformat()
    with _conn() as c:
        c.execute("UPDATE product_kits SET uploaded_files = ?, updated_at = ? WHERE id = ?",
                  (json.dumps(uploaded), now, kit_id))
        c.commit()

    return {"id": kit_id, "section": section, "filename": file.filename,
            "size": len(content), "uploaded_at": now}


# ─────────────────────────────────────────────────────────────
# PDF Download — single section
# ─────────────────────────────────────────────────────────────
@router.get("/{kit_id}/pdf/{section}")
def download_section_pdf(kit_id: str, section: str):
    """Download a single section as PDF.
    If user uploaded a file for this section, returns that file.
    Otherwise generates a PDF from the AI-generated content.
    Sections: circular | product_note | technical_specifications |
              test_cases | xsd | sample_payloads
    """
    record = _get_kit(kit_id)
    if not record:
        raise HTTPException(status_code=404, detail="Product kit not found")
    if section not in UPLOADABLE_SECTIONS:
        raise HTTPException(status_code=400, detail=f"Unknown section '{section}'")

    feature_name = record.get("feature_name", "Feature")
    cr_id = record.get("change_request_id") or kit_id[:8]
    version = record.get("version", "1.0")

    # Check user upload first
    import base64
    uploaded = record.get("uploaded_files") or {}
    if isinstance(uploaded, str):
        try:
            uploaded = json.loads(uploaded)
        except Exception:
            uploaded = {}

    if section in uploaded and uploaded[section].get("data_b64"):
        raw = base64.b64decode(uploaded[section]["data_b64"])
        fname = uploaded[section].get("filename", f"{section}.pdf")
        ct = uploaded[section].get("content_type", "application/pdf")
        return Response(content=raw, media_type=ct,
                        headers={"Content-Disposition": f'attachment; filename="{fname}"'})

    # Generate PDF from AI content
    if not _PDF_OK:
        raise HTTPException(status_code=503, detail="PDF generation library unavailable")

    kit = record.get("product_kit") or {}
    if not kit:
        raise HTTPException(status_code=404, detail="No kit content to generate PDF from")

    section_map = {
        "circular":               ("circular.pdf",               lambda: generate_circular_pdf(kit.get("circular",""), feature_name, cr_id, version)),
        "product_note":           ("product_note.pdf",           lambda: generate_product_note_pdf(kit.get("product_note",""), feature_name, cr_id, version)),
        "technical_specifications":("technical_specifications.pdf",lambda: generate_tech_specs_pdf(kit.get("technical_specifications",{}), feature_name, cr_id, version)),
        "test_cases":             ("test_cases.pdf",             lambda: generate_test_cases_pdf(kit.get("test_cases",[]), feature_name, cr_id, version)),
        "xsd":                    ("xsd_schema.pdf",             lambda: generate_xsd_pdf(kit.get("xsd",""), feature_name, cr_id, version)),
        "sample_payloads":        ("sample_payloads.pdf",        lambda: generate_payloads_pdf(kit.get("sample_payloads",{}), feature_name, cr_id, version)),
    }

    fname, gen_fn = section_map[section]
    try:
        pdf_bytes = gen_fn()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{cr_id}_{fname}"'},
    )


# ─────────────────────────────────────────────────────────────
# ZIP Download — complete kit
# ─────────────────────────────────────────────────────────────
@router.get("/{kit_id}/download-zip")
def download_complete_kit_zip(kit_id: str):
    """Download all Product Kit sections as a single ZIP file.
    ZIP is named after the Change Request ID (or kit ID).
    Each section is a separate PDF inside the ZIP.
    User-uploaded files are used where available; AI-generated PDFs otherwise.
    """
    record = _get_kit(kit_id)
    if not record:
        raise HTTPException(status_code=404, detail="Product kit not found")

    feature_name = record.get("feature_name", "Feature")
    cr_id = record.get("change_request_id") or kit_id[:8]
    version = record.get("version", "1.0")
    kit = record.get("product_kit") or {}

    import base64
    uploaded = record.get("uploaded_files") or {}
    if isinstance(uploaded, str):
        try:
            uploaded = json.loads(uploaded)
        except Exception:
            uploaded = {}

    safe_cr = re.sub(r'[^\w\-]', '_', cr_id)
    zip_name = f"{safe_cr}_ProductKit_v{version}.zip"

    buf = io.BytesIO()
    errors = []

    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # README
        readme = (
            f"NPCI Product Kit\n"
            f"{'='*50}\n"
            f"Feature  : {feature_name}\n"
            f"CR ID    : {cr_id}\n"
            f"Version  : {version}\n"
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"Status   : {record.get('status','draft')}\n\n"
            f"Contents:\n"
            f"  01_Circular.pdf\n"
            f"  02_Product_Note.pdf\n"
            f"  03_Technical_Specifications.pdf\n"
            f"  04_Test_Cases.pdf\n"
            f"  05_XSD_Schema.pdf\n"
            f"  06_Sample_Payloads.pdf\n"
        )
        zf.writestr("README.txt", readme)

        sections_cfg = [
            ("01_Circular.pdf",                  "circular",               lambda: generate_circular_pdf(kit.get("circular",""), feature_name, cr_id, version)),
            ("02_Product_Note.pdf",              "product_note",           lambda: generate_product_note_pdf(kit.get("product_note",""), feature_name, cr_id, version)),
            ("03_Technical_Specifications.pdf",  "technical_specifications",lambda: generate_tech_specs_pdf(kit.get("technical_specifications",{}), feature_name, cr_id, version)),
            ("04_Test_Cases.pdf",                "test_cases",             lambda: generate_test_cases_pdf(kit.get("test_cases",[]), feature_name, cr_id, version)),
            ("05_XSD_Schema.pdf",                "xsd",                    lambda: generate_xsd_pdf(kit.get("xsd",""), feature_name, cr_id, version)),
            ("06_Sample_Payloads.pdf",           "sample_payloads",        lambda: generate_payloads_pdf(kit.get("sample_payloads",{}), feature_name, cr_id, version)),
        ]

        for zip_fname, section, gen_fn in sections_cfg:
            try:
                # Prefer user upload
                if section in uploaded and uploaded[section].get("data_b64"):
                    raw = base64.b64decode(uploaded[section]["data_b64"])
                    orig_name = uploaded[section].get("filename", zip_fname)
                    # Use original extension but numbered prefix
                    ext = os.path.splitext(orig_name)[1] or ".pdf"
                    out_name = zip_fname.replace(".pdf", ext)
                    zf.writestr(out_name, raw)
                elif _PDF_OK:
                    pdf_bytes = gen_fn()
                    zf.writestr(zip_fname, pdf_bytes)
                else:
                    errors.append(f"{zip_fname}: PDF library unavailable, skipped")
            except Exception as e:
                errors.append(f"{zip_fname}: {e}")

        if errors:
            zf.writestr("ERRORS.txt", "\n".join(errors))

        # Also include JSON for reference
        if kit:
            zf.writestr("product_kit_data.json",
                        json.dumps({"meta": {"cr_id": cr_id, "feature_name": feature_name,
                                             "version": version, "status": record.get("status")},
                                    **kit}, indent=2))

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_name}"'},
    )


@router.delete("/{kit_id}")
def delete_product_kit(kit_id: str):
    """Delete a product kit."""
    record = _get_kit(kit_id)
    if not record:
        raise HTTPException(status_code=404, detail="Product kit not found")
    with _conn() as c:
        c.execute("DELETE FROM product_kits WHERE id = ?", (kit_id,))
        c.commit()
    return {"success": True, "id": kit_id}
