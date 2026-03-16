import os

JAVA_EXT = ".java"


def build_java_vector_store(java_root: str):
    """
    Hackathon-safe Java retriever.
    No FAISS. No embeddings. No vector DB.
    """
    return java_root


def retrieve_java_file(java_root: str, query: str):
    """
    Deterministically selects the most relevant Java file.

    Strategy:
    - Prefer DTO / Model classes
    - Prefer Req / Txn / Pay naming
    - Use filename heuristics only (SAFE)
    """

    candidates = []
    q = query.lower()

    for root, _, files in os.walk(java_root):
        for file in files:
            if not file.endswith(JAVA_EXT):
                continue

            score = 0
            name = file.lower()

            # Strong signals
            if "dto" in name or "model" in name:
                score += 5

            if "req" in q and "req" in name:
                score += 3

            if "txn" in q and "txn" in name:
                score += 3

            if "pay" in q and "pay" in name:
                score += 2

            candidates.append((score, os.path.join(root, file)))

    if not candidates:
        raise ValueError("No Java files found")

    # Pick highest score
    candidates.sort(key=lambda x: x[0], reverse=True)
    best_path = candidates[0][1]

    with open(best_path, "r", encoding="utf-8") as f:
        code = f.read()

    return {
        "path": best_path,
        "code": code
    }
