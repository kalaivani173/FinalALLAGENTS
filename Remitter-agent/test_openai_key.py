"""
Test that OPENAI_API_KEY is loaded and usable.

Run from Payer-agent directory:
  python test_openai_key.py

Checks:
  1. Key is loaded from .env via config.get_openai_api_key()
  2. Key is non-empty and looks like an OpenAI key (sk-...)
  3. Optional: call OpenAI API (tiny embedding) to confirm the key works
"""

import sys

def main():
    print("Checking if OPENAI_API_KEY is loaded for use...")
    print()

    # 1. Load key via config (same path used by LLM and embeddings)
    try:
        from config import get_openai_api_key
        key = get_openai_api_key()
    except Exception as e:
        print(f"FAIL: Could not load config / key: {e}")
        return 1

    if not key:
        print("FAIL: OPENAI_API_KEY is empty.")
        print("  Set it in .env (Payer-agent/.env) or as environment variable OPENAI_API_KEY.")
        return 1

    # 2. Show key is present (masked)
    if key.startswith("sk-"):
        masked = f"{key[:7]}...{key[-4:]}" if len(key) > 11 else "***"
    else:
        masked = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
    print(f"OK: Key is loaded (masked: {masked})")
    print()

    # 3. Optional: verify key works with a minimal API call
    print("Verifying key with OpenAI API (tiny embedding)...")
    try:
        from langchain_openai import OpenAIEmbeddings
        from config import get_openai_api_key
        emb = OpenAIEmbeddings(api_key=get_openai_api_key())
        # Single short string to minimize cost
        result = emb.embed_query("test")
        if result and len(result) > 0:
            print(f"OK: Embedding API call succeeded (vector length: {len(result)})")
        else:
            print("WARN: API responded but embedding was empty.")
    except Exception as e:
        print(f"FAIL: OpenAI API call failed: {e}")
        return 1

    print()
    print("All checks passed. OPENAI_API_KEY is loaded and will be used for LLM/embeddings.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
