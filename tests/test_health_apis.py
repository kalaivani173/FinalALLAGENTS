"""
API health checks (no Selenium). Verifies each agent's /health and orchestrator root.
Skips when a service is not running.
"""
import pytest
import requests

from conftest import (
    ORCHESTRATOR_URL,
    PAYER_AGENT_URL,
    BENEFICIARY_AGENT_URL,
    REMITTER_AGENT_URL,
    PAYEE_AGENT_URL,
    skip_if_server_down,
)

TIMEOUT = 5


def _get(url: str, path: str = ""):
    return requests.get(f"{url}{path}", timeout=TIMEOUT)


@pytest.mark.parametrize("name,url,health_path", [
    ("payer", PAYER_AGENT_URL, "/health"),
    ("beneficiary", BENEFICIARY_AGENT_URL, "/health"),
    ("remitter", REMITTER_AGENT_URL, "/health"),
    ("payee", PAYEE_AGENT_URL, "/health"),
])
def test_agent_health(name, url, health_path):
    """Each agent exposes /health and returns 200 with status."""
    skip_if_server_down(url, name)
    r = _get(url, health_path)
    assert r.status_code == 200, f"{name} health: expected 200, got {r.status_code}"
    data = r.json()
    assert data.get("status") == "ok", f"{name} health: expected status ok, got {data}"


def test_orchestrator_root():
    """Orchestrator serves root (UI or redirect)."""
    skip_if_server_down(ORCHESTRATOR_URL, "orchestrator")
    r = _get(ORCHESTRATOR_URL, "/")
    assert r.status_code == 200, f"orchestrator /: expected 200, got {r.status_code}"


def test_orchestrator_partners_api():
    """Orchestrator exposes partners list."""
    skip_if_server_down(ORCHESTRATOR_URL, "orchestrator")
    r = _get(ORCHESTRATOR_URL, "/npciswitch/partners")
    assert r.status_code == 200, f"orchestrator partners: expected 200, got {r.status_code}"
    data = r.json()
    assert isinstance(data, dict), "partners should be a dict (partner id -> config)"
