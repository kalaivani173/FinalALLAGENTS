import os
from pathlib import Path

# Load .env first so OPENAI_API_KEY etc. are set before any os.environ reads
_config_dir = Path(__file__).resolve().parent
_env_file = _config_dir / ".env"

def _ensure_env_loaded():
    """Load .env so OPENAI_API_KEY is in os.environ (safe to call multiple times)."""
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file, override=True)
    except ImportError:
        pass

_ensure_env_loaded()

def get_openai_api_key() -> str:
    """
    Return OPENAI_API_KEY from environment. Ensures .env is loaded first.
    Use this whenever creating OpenAI/LLM/embeddings clients so the key is always used.
    """
    _ensure_env_loaded()
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    # Remove optional surrounding quotes from .env (e.g. OPENAI_API_KEY="sk-...")
    if len(key) >= 2 and key[0] == key[-1] and key[0] in ('"', "'"):
        key = key[1:-1].strip()
    return key

# Beneficiary Bank agent: artifacts here; Java repo default <project_root>/javacoderepo/BeneficiaryBank (override with BENEFICIARY_REPO or JAVACODEREPO_ROOT)
_root = Path(__file__).resolve().parent
_project_root = _root.parent
_javacoderepo_root = Path(os.environ.get("JAVACODEREPO_ROOT", str(_project_root / "javacoderepo")))
_default_repo = _javacoderepo_root / "BeneficiaryBank"
REPO_PATH = Path(os.environ.get("BENEFICIARY_REPO", str(_default_repo)))
ARTIFACTS_PATH = _root / "artifacts"
ARTIFACTS_PATH.mkdir(exist_ok=True)

# Agent identity (API responses and orchestrator A2A)
AGENT_NAME = "BENEFICIARY_BANK"
AGENT_ORCHESTRATOR_NAME = "Beneficiary"
PATCH_FILENAME = "beneficiary.patch"

NPCI_PUBLIC_KEY = os.environ.get("NPCI_PUBLIC_KEY", "npci_public.pem")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = get_openai_api_key()
SKIP_SIGNATURE_VERIFY = os.environ.get("SKIP_SIGNATURE_VERIFY", "").lower() in ("1", "true", "yes")

# Beneficiary-agent backend port (override with BENEFICIARY_AGENT_PORT if needed)
PORT = int(os.environ.get("BENEFICIARY_AGENT_PORT", "9002"))

ORCHESTRATOR_URL = os.environ.get("ORCHESTRATOR_URL", "http://localhost:8000").rstrip("/")
