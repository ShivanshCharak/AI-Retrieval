from collections import defaultdict
import json


def reciprocal_rank_fusion(documents, k: int = 60):
    scores = defaultdict(float)
    doc_lookup = {}
    print("documents", documents, type(documents))
    content = ""

    for rank, doc in enumerate(documents):
        if "id" in doc:
            content = doc.get("id")
        else:
            content = doc.get("content")

        if isinstance(content, dict):
            key = json.dumps(content, sort_keys=True)
            print(key)
        else:
            key = content

        scores[key] += 1 / (k + rank + 1)

        # Keep the original document
        doc_lookup[key] = doc

    fused_docs = []

    for key, score in scores.items():
        fused_doc = doc_lookup[key].copy()
        fused_doc["score"] = score
        fused_docs.append(fused_doc)

    fused_docs.sort(key=lambda x: x["score"], reverse=True)

    return fused_docs
