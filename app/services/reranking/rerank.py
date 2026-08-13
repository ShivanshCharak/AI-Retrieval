# from sentence_transformers import CrossEncoder

# reranker = CrossEncoder(
#     "BAAI/bge-reranker-v2-m3",
#     max_length=1024,
# )


# def rerank_documents(
#     query: str,
#     documents: list,
#     top_k: int = 5,
# ):

#     pairs = []

#     for doc in documents:

#         if hasattr(doc, "page_content"):
#             content = doc.page_content
#         elif isinstance(doc, dict):
#             content = doc.get("content", "")
#         else:
#             content = ""

#         pairs.append((query, content))

#     # New relevance score for every query/document pair
#     scores = reranker.predict(
#         pairs,
#         batch_size=8,
#         show_progress_bar=False,
#     )

#     reranked = []

#     for doc, score in zip(documents, scores):

#         score = float(score)

#         if hasattr(doc, "metadata"):

#             doc.metadata["rerank_score"] = score

#         elif isinstance(doc, dict):

#             doc.setdefault("metadata", {})

#             doc["metadata"]["rerank_score"] = score

#         reranked.append((doc, score))

#     # Sort using the NEW reranker score
#     reranked.sort(
#         key=lambda x: x[1],
#         reverse=True,
#     )


#     return [doc for doc, score in reranked[:top_k]]
def rerank_documents(
    query,
    documents,
    top_k: int = 5,
):
    return sorted(
        documents,
        key=lambda doc: doc.metadata.get("rrf_score", 0),
        reverse=True,
    )
