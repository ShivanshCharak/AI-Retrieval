from sentence_transformers import CrossEncoder

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-2-v2",
    max_length=512,
    device="cpu",
)


def rerank_documents(
    query: str,
    documents: list,
    top_k: int = 5,
):
    pairs = []

    for doc in documents:

        # Qdrant ScoredPoint
        if hasattr(doc, "payload"):
            content = doc.payload.get("text", "")

        # LangChain Document
        elif hasattr(doc, "page_content"):
            content = doc.page_content

        # Dict
        elif isinstance(doc, dict):
            content = doc.get("content", "")

        else:
            content = ""

        pairs.append((query, content))

    scores = reranker.predict(
        pairs,
        batch_size=8,
        show_progress_bar=False,
    )

    reranked = list(zip(documents, scores))

    reranked.sort(
        key=lambda x: float(x[1]),
        reverse=True,
    )

    return [doc for doc, score in reranked[:top_k]]
