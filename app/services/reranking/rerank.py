def rerank_documents(query: str, documents: list):
    return sorted(documents, key=lambda x: x.metadata.get("rrf_score", 0), reverse=True)
