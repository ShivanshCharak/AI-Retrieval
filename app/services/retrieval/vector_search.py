from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

from langchain_qdrant import QdrantVectorStore

from app.db.qdrant_client_embedder import embedder

client = QdrantClient(url="http://localhost:6333")


vector_store = QdrantVectorStore(client=client, collection_name="documents", embedding=embedder)


def vector_search(query: str, userId: str, k: int = 5):

    results = vector_store.similarity_search_with_score(
        query=query, k=k, filter=Filter(must=[FieldCondition(key="metadata.user_id", match=MatchValue(value=userId))])
    )

    docs = []

    for doc, score in results:

        docs.append({"content": doc.page_content, "metadata": doc.metadata, "score": float(score), "source": "qdrant"})

    return docs
