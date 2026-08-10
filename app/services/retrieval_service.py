from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.db.qdrant_client_embedder import vector_store


def retrieve_context(
    query: str,
    user_id: int,
    repo_url: str | None = None,
):
    conditions = [
        FieldCondition(
            key="metadata.user_id",
            match=MatchValue(value=user_id),
        )
    ]

    if repo_url:
        conditions.append(
            FieldCondition(
                key="metadata.repo_url",
                match=MatchValue(value=repo_url),
            )
        )

    search_filter = Filter(must=conditions)

    docs = vector_store.similarity_search(
        query=query,
        k=10,
        filter=search_filter,
    )

    return docs
