import os
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader

# ---------------------------
# LLM Configuration
# ---------------------------
# Used ONLY for NEW API XSD generation
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# ---------------------------
# Load sample XML / payloads
# ---------------------------
def load_samples(change_id: str) -> str:
    """
    Loads sample request/response XMLs uploaded by PM.

    Folder structure:
    artifacts/
        samples/
            <changeId>/
                sample1.xml
                sample2.xml
    """

    base_path = os.path.join("artifacts", "samples", change_id)

    if not os.path.exists(base_path):
        raise FileNotFoundError(
            f"No sample files found for changeId={change_id}"
        )

    documents = []

    for file_name in os.listdir(base_path):
        file_path = os.path.join(base_path, file_name)

        if not os.path.isfile(file_path):
            continue

        try:
            loader = TextLoader(file_path)
            documents.extend(loader.load())
        except Exception:
            # Ignore unreadable files (hackathon-safe)
            continue

    if not documents:
        raise ValueError("No readable sample content found")

    return "\n\n".join(doc.page_content for doc in documents)


# ---------------------------
# Generate XSD from samples
# ---------------------------
def generate_xsd_from_samples(
    api_name: str,
    samples: str
) -> str:
    """
    Generates a DRAFT XSD for a NEW UPI API using samples.

    IMPORTANT:
    - Used ONLY for ADD_NEW_API
    - Output shown to PM for approval
    """

    prompt = f"""
You are an NPCI UPI Specification expert.

You are generating a DRAFT XSD for a NEW UPI API.

==============================
RULES (VERY STRICT):
==============================
1. Use ONLY elements present in samples
2. Default datatype: xs:string
3. Mark fields optional unless clearly mandatory
4. Use proper xs:complexType and xs:sequence
5. Do NOT invent fields
6. Do NOT explain anything
7. Return ONLY valid XSD
8. Use targetNamespace with api name

==============================
API NAME:
==============================
{api_name}

==============================
SAMPLES:
==============================
{samples}
"""

    response = llm.invoke(prompt)

    return response.content.strip()
