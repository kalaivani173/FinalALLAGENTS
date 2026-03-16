from pathlib import Path

TARGETS = ["dto", "request", "response", "validator", "controller", "service"]

def scan_repo(repo_path: Path):
    docs = []

    for f in repo_path.rglob("*.java"):
        if any(t in f.as_posix().lower() for t in TARGETS):
            docs.append({
                "path": str(f),
                "content": f.read_text(encoding="utf-8")
            })

    for f in repo_path.rglob("*.xsd"):
        docs.append({
            "path": str(f),
            "content": f.read_text(encoding="utf-8")
        })

    return docs
