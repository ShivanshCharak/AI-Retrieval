from app.db.qdrant_client_embedder import vector_store


def retrieve_context(query: str):
    docs = vector_store.similarity_search(query=query, k=5)
    return docs
