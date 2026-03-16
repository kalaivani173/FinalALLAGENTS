"""
Pytest fixtures for Selenium E2E tests.
Expects services to be running; use env vars to override ports.
"""
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# Base URLs (override via env for CI/different ports)
def _base_url(env_key: str, default_port: str) -> str:
    url = os.environ.get(env_key, "").strip()
    if url:
        return url.rstrip("/")
    return f"http://127.0.0.1:{default_port}"


ORCHESTRATOR_URL = _base_url("ORCHESTRATOR_E2E_URL", "8000")
PAYER_AGENT_URL = _base_url("PAYER_AGENT_E2E_URL", "9001")
BENEFICIARY_AGENT_URL = _base_url("BENEFICIARY_AGENT_E2E_URL", "9002")
REMITTER_AGENT_URL = _base_url("REMITTER_AGENT_E2E_URL", "9003")
PAYEE_AGENT_URL = _base_url("PAYEE_AGENT_E2E_URL", "9004")


def _server_reachable(url: str, path: str = "/", timeout: int = 2) -> bool:
    try:
        import requests
        r = requests.get(f"{url}{path}", timeout=timeout)
        return r.status_code in (200, 304)
    except Exception:
        return False


def skip_if_server_down(base_url: str, app_name: str):
    """Skip test if the app at base_url is not reachable."""
    if not _server_reachable(base_url):
        pytest.skip(f"{app_name} not running at {base_url} (start the service first)")


@pytest.fixture(scope="module")
def chrome_driver():
    """One Chrome WebDriver per test module (headless by default)."""
    opts = Options()
    if os.environ.get("E2E_HEADED", "").lower() not in ("1", "true", "yes"):
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    yield driver
    driver.quit()


@pytest.fixture
def driver(chrome_driver):
    """Per-test driver (same browser instance)."""
    yield chrome_driver
    chrome_driver.delete_all_cookies()


# App URLs for parametrized tests: (name, url, title_contains)
APP_URLS = [
    ("orchestrator", ORCHESTRATOR_URL, "NPCI"),
    ("payer", PAYER_AGENT_URL, "Payer"),
    ("beneficiary", BENEFICIARY_AGENT_URL, "Beneficiary"),
    ("remitter", REMITTER_AGENT_URL, "Remitter"),
    ("payee", PAYEE_AGENT_URL, "Payee"),
]
