from collections import defaultdict


def reciprocal_rank_fusion(documents, k: int = 60):
    scores = defaultdict(float)
    doc_lookup = {}

    for rank, doc in enumerate(documents):
        # LangChain Document
        if hasattr(doc, "metadata"):
            doc_id = doc.metadata.get("id")

            # Fallback if metadata id doesn't exist
            if not doc_id:
                doc_id = doc.page_content

        # Dictionary support, if you ever have dicts
        elif isinstance(doc, dict):
            doc_id = doc.get("id") or doc.get("content")

        else:
            continue

        scores[doc_id] += 1 / (k + rank + 1)

        # Keep original Document
        doc_lookup[doc_id] = doc

    fused_docs = []

    for doc_id, score in scores.items():
        doc = doc_lookup[doc_id]

        # Don't mutate the original Document
        if hasattr(doc, "metadata"):
            fused_doc = doc.model_copy(deep=True)
            fused_doc.metadata["rrf_score"] = score
        else:
            fused_doc = doc.copy()
            fused_doc["score"] = score

        fused_docs.append(fused_doc)

    fused_docs.sort(
        key=lambda doc: (
            doc.metadata.get("rrf_score", 0)
            if hasattr(doc, "metadata")
            else doc.get("score", 0)
        ),
        reverse=True,
    )

    return fused_docs
