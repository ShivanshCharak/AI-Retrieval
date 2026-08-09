from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from app.graph.graph import GraphState
import time
from langchain_qdrant import QdrantVectorStore

from app.db.qdrant_client_embedder import embedder, vector_store


def vector_search(state: GraphState, query: str, userId: str, k: int = 5):
    start = time.time()

    results = vector_store.similarity_search_with_score(
        query=query,
        k=k,
        filter=Filter(
            must=[
                FieldCondition(key="metadata.user_id", match=MatchValue(value=userId))
            ]
        ),
    )

    docs = []
    state["trace"].append(
        {
            "node": "vector search",
            "latency_ms": (time.time() - start) * 1000,
        }
    )
    for doc, score in results:

        docs.append(
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score),
                "source": "qdrant",
            }
        )

    return docs
