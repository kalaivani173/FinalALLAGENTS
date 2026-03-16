# Setting the OpenAI API key (for LLM calls)

The app uses LangChain’s `ChatOpenAI`, which reads **`OPENAI_API_KEY`** from the **environment** when an LLM call runs. The key is never hardcoded in source code.

## Option 1: Use a `.env` file (recommended for local dev)

1. In the project root (`aicode`), create a file named **`.env`** (same folder as `main.py`).
2. Add one line (replace with your real key):
   ```env
   OPENAI_API_KEY=sk-your-openai-api-key-here
   ```
3. The app already calls `load_dotenv()` in `main.py` and `rag.py`, so on startup it loads `.env` into the process environment. All LLM calls then use this key.

**Template:** Copy `.env.example` to `.env` and fill in the key:
```bash
copy .env.example .env
# Then edit .env and set OPENAI_API_KEY=sk-...
```

**Important:** Add `.env` to `.gitignore` so the real key is never committed. Example line for `.gitignore`:
```
.env
```

## Option 2: Set in the terminal (current session only)

**PowerShell (Windows):**
```powershell
$env:OPENAI_API_KEY = "sk-your-openai-api-key-here"
python -m uvicorn main:app --reload --port 8000
```

**Cmd:**
```cmd
set OPENAI_API_KEY=sk-your-openai-api-key-here
python -m uvicorn main:app --reload --port 8000
```

**Bash / Linux / macOS:**
```bash
export OPENAI_API_KEY=sk-your-openai-api-key-here
python -m uvicorn main:app --reload --port 8000
```

## Option 3: System environment variable (Windows)

1. Search “Environment variables” in Windows.
2. Open “Edit the system environment variables” → “Environment Variables”.
3. Under “User variables” (or “System variables”), click “New”.
4. Variable name: `OPENAI_API_KEY`  
   Variable value: `sk-your-openai-api-key-here`
5. OK and restart the terminal/IDE, then run the app.

---

## Is this approach good?

**Yes.** Using the environment (and `.env` with `load_dotenv()`) is the standard way to handle API keys:

| Benefit | Why it matters |
|--------|-----------------|
| **Key not in code** | No risk of committing the key to git or sharing it in screenshots. |
| **Different keys per environment** | Use one key locally (`.env`), another in production (e.g. server env vars). |
| **No code change to switch keys** | Change `.env` or env vars; no edits to Python files. |
| **LangChain default** | `ChatOpenAI` is designed to use `OPENAI_API_KEY` from the environment. |

**Do not:** Put the key in source code (e.g. `api_key="sk-..."`). That is insecure and easy to leak.

**Do:** Use `.env` for local dev (and add `.env` to `.gitignore`), and use environment variables in production (e.g. set in your host/CI).
