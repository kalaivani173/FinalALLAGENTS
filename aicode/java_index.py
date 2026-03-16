import os
import re

JAVA_EXT = ".java"

ROOT_RE = re.compile(r'@XmlRootElement\s*\(\s*name\s*=\s*"([^"]+)"')
ELEMENT_RE = re.compile(r'@XmlElement\s*\(\s*name\s*=\s*"([^"]+)"')
ATTR_RE = re.compile(r'@XmlAttribute\s*\(\s*name\s*=\s*"([^"]+)"')
FIELD_RE = re.compile(r'private\s+(\w+)\s+(\w+);')


def index_java_codebase(java_root: str):
    """
    Builds a semantic index of Java DTOs:
    - class name
    - XML root
    - XML elements
    - XML attributes
    - field → type mapping
    Returns empty list if java_root does not exist.
    """
    index = []
    if not java_root or not os.path.isdir(java_root):
        return index

    for root, _, files in os.walk(java_root):
        for file in files:
            if not file.endswith(JAVA_EXT):
                continue

            path = os.path.join(root, file)

            try:
                code = open(path, encoding="utf-8").read()
            except Exception:
                continue

            class_match = re.search(r'class\s+(\w+)', code)
            if not class_match:
                continue

            class_name = class_match.group(1)

            fields = {
                name: ftype
                for ftype, name in FIELD_RE.findall(code)
            }

            index.append({
                "className": class_name,
                "path": path,
                "code": code,
                "xmlRoot": ROOT_RE.findall(code),          # e.g. ReqPay
                "xmlElements": ELEMENT_RE.findall(code),  # e.g. Head
                "xmlAttributes": ATTR_RE.findall(code),   # e.g. ver, ts
                "fields": fields                          # e.g. head -> Head
            })

    return index
