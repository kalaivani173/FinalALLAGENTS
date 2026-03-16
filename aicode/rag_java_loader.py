import os
from langchain_community.document_loaders import TextLoader

JAVA_EXTENSIONS = (".java",)


def load_java_codebase(base_dir: str) -> str:
    """
    Loads all Java files under base_dir for RAG.

    Returns:
    - Single string containing entire Java codebase
    """

    documents = []

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(JAVA_EXTENSIONS):
                path = os.path.join(root, file)
                try:
                    loader = TextLoader(path, encoding="utf-8")
                    documents.extend(loader.load())
                except Exception:
                    # Hackathon-safe: skip unreadable files
                    continue

    if not documents:
        raise ValueError("No Java files found for RAG")

    return "\n\n".join(doc.page_content for doc in documents)
