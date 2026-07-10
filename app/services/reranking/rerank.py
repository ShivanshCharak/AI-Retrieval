def rerank_documents(
    query: str,
    documents: list
):

    return sorted(
        documents,
        key=lambda x: x.get(
            "score",
            0
        ),
        reverse=True
    )