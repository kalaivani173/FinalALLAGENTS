import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import LLM_MODEL, get_openai_api_key

_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        api_key = get_openai_api_key()
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Set it in .env (Payer-agent/.env) or as environment variable."
            )
        _llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0,
            api_key=api_key,
        )
    return _llm

PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a senior Java UPI PSP engineer. "
     "Use ONLY the provided code. "
     "Output unified git diff ONLY (no explanation)."),
    ("human",
     """
Manifest (NPCI change):
{manifest_json}

Existing Code:
{context}

Apply the change to the Java code. Output only a valid unified git diff.
""")
])

def generate_patch(manifest, docs):
    context = "\n\n".join(
        f"// FILE: {d.metadata['path']}\n{d.page_content}"
        for d in docs
    )
    manifest_json = json.dumps(manifest, indent=2)

    return _get_llm().invoke(
        PROMPT.format_messages(
            manifest_json=manifest_json,
            context=context
        )
    ).content
