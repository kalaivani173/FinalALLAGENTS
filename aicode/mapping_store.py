import json
import os

STORE_PATH = "mapping_memory.json"


def _load():
    if not os.path.exists(STORE_PATH):
        return {}
    with open(STORE_PATH, "r") as f:
        return json.load(f)


def _save(data):
    with open(STORE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_mapped_class(xml_path: str):
    return _load().get(xml_path)


def save_mapping(xml_path: str, class_name: str):
    data = _load()
    data[xml_path] = class_name
    _save(data)
