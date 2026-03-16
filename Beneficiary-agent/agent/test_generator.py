"""Generate JUnit unit tests for generated code using LLM."""
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
                "OPENAI_API_KEY is not set. Set it in .env (Beneficiary-agent/.env) or as environment variable."
            )
        _llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0,
            api_key=api_key,
        )
    return _llm

PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a senior Java engineer writing JUnit 5 unit tests for a UPI Beneficiary Bank (credit/CBS integration) Spring Boot application. "
     "Output only valid Java source code: a single test class with package, imports, @SpringBootTest, and @Test methods. "
     "No markdown fences, no explanation. Use JUnit 5 (org.junit.jupiter.api.Test) and Spring Boot test support."),
    ("human",
     """
Manifest (NPCI change request):
{manifest_json}

Generated code change (unified diff):
{patch_content}

Generate a JUnit 5 test class that tests the behaviour implied by this change. Match the package and class names from the diff. Output only the Java file contents.
""")
])


def generate_unit_tests(manifest: dict, patch_content: str) -> str:
    """Use LLM to generate JUnit unit test code for the generated patch. Returns Java source."""
    if not (patch_content or "").strip():
        return "// No patch content; cannot generate tests."
    manifest_json = json.dumps(manifest, indent=2)
    return _get_llm().invoke(
        PROMPT.format_messages(
            manifest_json=manifest_json,
            patch_content=(patch_content or "").strip()
        )
    ).content
