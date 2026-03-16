import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredPDFLoader
)

load_dotenv()  # Loads .env into os.environ (e.g. OPENAI_API_KEY=sk-...)

# ChatOpenAI does NOT take api_key in code. It reads OPENAI_API_KEY from the
# process environment (os.environ). So the key must be set by: .env (via
# load_dotenv above), or system env vars, or the shell. Without it, llm.invoke()
# would fail with an auth error from OpenAI.
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def load_attachments(change_id: str):
    documents = []
    base_dir = "artifacts"

    for folder in ["xsd", "samples", "specs"]:
        folder_path = os.path.join(base_dir, folder, change_id)
        if not os.path.exists(folder_path):
            continue

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if not os.path.isfile(file_path):
                continue

            try:
                loader = (
                    UnstructuredPDFLoader(file_path)
                    if file_name.lower().endswith(".pdf")
                    else TextLoader(file_path)
                )
                documents.extend(loader.load())
            except Exception:
                continue

    return documents


def validate_with_attachments(change_id: str, description: str):
    docs = load_attachments(change_id)

    if not docs:
        return {"notes": ["No attachments provided"], "warnings": []}

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
You are an NPCI UPI specification reviewer.

CHANGE DESCRIPTION:
{description}

ATTACHMENTS:
{context}

ONLY return JSON:
{{
  "notes": [],
  "warnings": []
}}
"""

    response = llm.invoke(prompt)
    return json.loads(response.content)
