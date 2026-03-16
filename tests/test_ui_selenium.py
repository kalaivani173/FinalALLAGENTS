"""
Selenium E2E tests: load each app's UI and verify page and key elements.
Skips when a service is not running. See tests/README.md for how to start them.
"""
import pytest
from conftest import APP_URLS, skip_if_server_down


@pytest.mark.parametrize("app_name,base_url,title_contains", APP_URLS)
def test_app_ui_loads(driver, app_name, base_url, title_contains):
    """Each app root URL loads and page title contains expected text."""
    skip_if_server_down(base_url, app_name)
    driver.get(f"{base_url}/")
    driver.implicitly_wait(5)
    assert title_contains.lower() in driver.title.lower(), (
        f"{app_name}: expected title to contain '{title_contains}', got '{driver.title}'"
    )


@pytest.mark.parametrize("app_name,base_url,title_contains", APP_URLS)
def test_app_has_main_content(driver, app_name, base_url, title_contains):
    """Each app has main content (root div or .app)."""
    skip_if_server_down(base_url, app_name)
    driver.get(f"{base_url}/")
    driver.implicitly_wait(5)
    # React root or static .app
    root = driver.find_elements("css selector", "#root, .app")
    assert len(root) >= 1, f"{app_name}: expected #root or .app on page"


@pytest.mark.parametrize("app_name,base_url,_", APP_URLS)
def test_app_no_console_errors(driver, app_name, base_url, _):
    """Basic check: page load does not yield severe JS errors (best-effort)."""
    skip_if_server_down(base_url, app_name)
    driver.get(f"{base_url}/")
    driver.implicitly_wait(3)
    try:
        logs = driver.get_log("browser")
    except Exception:
        pytest.skip("browser log not supported")
    severe = [e for e in logs if e.get("level") == "SEVERE"]
    # Allow some SEVERE in dev (e.g. source map 404); fail only if many
    assert len(severe) < 10, f"{app_name}: too many console SEVERE: {severe[:5]}"
