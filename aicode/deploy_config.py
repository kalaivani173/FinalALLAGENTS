"""
Deploy and Git integration configuration.
Read from os.environ; load .env via load_dotenv() in main so env is set before deploy runs.
"""
import os
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent


def _bool_env(key: str, default: bool = False) -> bool:
    v = os.environ.get(key, "").strip().lower()
    return v in ("1", "true", "yes") if v else default


def _int_env(key: str, default: int) -> int:
    try:
        v = os.environ.get(key, "").strip()
        return int(v) if v else default
    except ValueError:
        return default


def _str_env(key: str, default: str = "") -> str:
    return os.environ.get(key, "").strip() or default


# ---- Deploy ----
def get_javacoderepo_root() -> str:
    """JAVACODEREPO_ROOT from env, or default: sibling of aicode named javacoderepo."""
    root = _str_env("JAVACODEREPO_ROOT")
    if root and os.path.isdir(root):
        return os.path.normpath(root)
    parent = _BASE_DIR.parent
    default = str(parent / "javacoderepo")
    return os.path.normpath(default)


DEPLOY_DRY_RUN = _bool_env("DEPLOY_DRY_RUN", False)

# ---- Git ----
DEPLOY_GIT_ENABLED = _bool_env("DEPLOY_GIT_ENABLED", True)
# Legacy: DEPLOY_PUSH_TO_GIT=1 also enables Git (same as DEPLOY_GIT_ENABLED)
if not DEPLOY_GIT_ENABLED and _bool_env("DEPLOY_PUSH_TO_GIT", False):
    DEPLOY_GIT_ENABLED = True

DEPLOY_GIT_COMMIT_ONLY = _bool_env("DEPLOY_GIT_COMMIT_ONLY", False)
DEPLOY_GIT_BRANCH = _str_env("DEPLOY_GIT_BRANCH")  # empty = use current branch
DEPLOY_GIT_REMOTE = _str_env("DEPLOY_GIT_REMOTE", "origin")
DEPLOY_GIT_COMMIT_MESSAGE_TEMPLATE = _str_env(
    "DEPLOY_GIT_COMMIT_MESSAGE_TEMPLATE",
    "Deploy field-addition: {changeId}",
)
DEPLOY_GIT_ALLOW_DIRTY_REPO = _bool_env("DEPLOY_GIT_ALLOW_DIRTY_REPO", True)

# ---- Timeouts (seconds) ----
DEPLOY_GIT_ADD_TIMEOUT = _int_env("DEPLOY_GIT_ADD_TIMEOUT", 30)
DEPLOY_GIT_COMMIT_TIMEOUT = _int_env("DEPLOY_GIT_COMMIT_TIMEOUT", 30)
DEPLOY_GIT_PUSH_TIMEOUT = _int_env("DEPLOY_GIT_PUSH_TIMEOUT", 60)

# ---- Retries ----
DEPLOY_GIT_PUSH_RETRIES = max(0, _int_env("DEPLOY_GIT_PUSH_RETRIES", 2))
