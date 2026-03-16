"""
Shared web path constants for XSD hosting on the backend service.
Use these when building manifest xsd.path or linking to XSD from the same service.
"""
import os

# XSD hosting: GET {XSD_WEB_PATH_PREFIX}/{changeId}/{filename} serves the XSD file
XSD_WEB_PATH_PREFIX = "/npciswitch/xsd"

# Base URL for manifest XSD path (include host and port). Set via env XSD_BASE_URL.
XSD_BASE_URL = (os.environ.get("XSD_BASE_URL") or "http://localhost:8000").rstrip("/")

# OpenAPI/Swagger hosting: GET {OPENAPI_WEB_PATH_PREFIX}/{changeId}/{filename} serves the spec file
OPENAPI_WEB_PATH_PREFIX = "/npciswitch/openapi"

# Base URL for manifest OpenAPI path (include host and port). Set via env OPENAPI_BASE_URL.
# Defaults to XSD_BASE_URL so both are hosted on the same service.
OPENAPI_BASE_URL = (os.environ.get("OPENAPI_BASE_URL") or XSD_BASE_URL).rstrip("/")

# Product note hosting: GET {PRODUCT_NOTE_WEB_PATH_PREFIX}/{changeId}/{filename} serves the product note
PRODUCT_NOTE_WEB_PATH_PREFIX = "/npciswitch/product-note"
PRODUCT_NOTE_BASE_URL = (os.environ.get("PRODUCT_NOTE_BASE_URL") or XSD_BASE_URL).rstrip("/")


def xsd_web_path(change_id: str, filename: str) -> str:
    """Build the XSD web path (path only, no host).
    Example: xsd_web_path('CHG-624', 'ReqPay.xsd') -> '/npciswitch/xsd/CHG-624/ReqPay.xsd'
    """
    if not filename.endswith(".xsd"):
        filename = f"{filename}.xsd"
    return f"{XSD_WEB_PATH_PREFIX}/{change_id}/{filename}"


def xsd_web_url(change_id: str, filename: str) -> str:
    """Build the full XSD URL for manifest (includes localhost and port).
    Example: xsd_web_url('CHG-624', 'ReqPay.xsd') -> 'http://localhost:8000/npciswitch/xsd/CHG-624/ReqPay.xsd'
    """
    return f"{XSD_BASE_URL}{xsd_web_path(change_id, filename)}"


def openapi_web_path(change_id: str, filename: str) -> str:
    """Build the OpenAPI web path (path only, no host).
    Example: openapi_web_path('CHG-624', 'openapi.yaml') -> '/npciswitch/openapi/CHG-624/openapi.yaml'
    """
    return f"{OPENAPI_WEB_PATH_PREFIX}/{change_id}/{filename}"


def openapi_web_url(change_id: str, filename: str) -> str:
    """Build the full OpenAPI URL for manifest (includes host and port).
    Example: openapi_web_url('CHG-624', 'openapi.yaml') -> 'http://localhost:8000/npciswitch/openapi/CHG-624/openapi.yaml'
    """
    return f"{OPENAPI_BASE_URL}{openapi_web_path(change_id, filename)}"


OPENAPI_UI_PATH_PREFIX = "/npciswitch/openapi-ui"


def openapi_ui_url(change_id: str) -> str:
    """Build the full Swagger UI URL for manifest (human-readable, not raw JSON).
    Example: openapi_ui_url('CHG-624') -> 'http://localhost:8000/npciswitch/openapi-ui/CHG-624'
    """
    return f"{OPENAPI_BASE_URL}{OPENAPI_UI_PATH_PREFIX}/{change_id}"


def product_note_web_path(change_id: str, filename: str) -> str:
    """Build the product note web path (path only, no host).
    Example: product_note_web_path('CHG-624', 'product_note.pdf') -> '/npciswitch/product-note/CHG-624/product_note.pdf'
    """
    return f"{PRODUCT_NOTE_WEB_PATH_PREFIX}/{change_id}/{filename}"


def product_note_web_url(change_id: str, filename: str) -> str:
    """Build the full product note URL for manifest (includes host and port).
    Example: product_note_web_url('CHG-624', 'product_note.md') -> 'http://localhost:8000/npciswitch/product-note/CHG-624/product_note.md'
    """
    return f"{PRODUCT_NOTE_BASE_URL}{product_note_web_path(change_id, filename)}"
