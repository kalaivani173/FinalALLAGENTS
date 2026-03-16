def retrieve(vector_store, manifest: dict, k: int = 6):
    impacted = manifest.get("impactedPaths") or []
    parts = [
        f"API: {manifest.get('apiName', '')}",
        f"ChangeType: {manifest.get('changeType', '')}",
    ]
    if impacted and impacted[0].get("xmlPath"):
        parts.append(f"XML Path: {impacted[0]['xmlPath']}")
    field_name = (
        (impacted and impacted[0].get("attribute", {}).get("name"))
        or (impacted and impacted[0].get("fieldName"))
    )
    if field_name:
        parts.append(f"Field: {field_name}")
    query = "\n".join(parts)
    return vector_store.similarity_search(query, k=k)
