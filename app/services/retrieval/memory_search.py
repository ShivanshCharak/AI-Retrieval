from app.db.qdrant_client_embedder import embedder, client
from qdrant_client.models import Filter, FieldCondition, MatchValue


def memory_search(query: str, user_id: int, top_k: int = 5):
    query_vector = embedder.embed_query(query)
    results = client.query_points(
        collection_name="documents",
        query=query_vector,
        limit=top_k,
        query_filter=Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]),
    )
    memories = []
    for point in results.points:
        text = point.payload.get("text")
        if not text:
            print("no memeory found")
            continue
        memories.append(
            {
                "content": point.payload["text"],
                "score": point.score,
                "source": "memory",
            }
        )
    print("memories", memories)
    return memories
