import asyncio
from qdrant_client import QdrantClient
from app.services.reranking.rerank import rerank_documents

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
    SparseVector,
    Prefetch,
    FusionQuery,
    Fusion,
)

from langchain_core.documents import Document
from app.services.fusion.rrf import reciprocal_rank_fusion
from langchain_ollama import OllamaEmbeddings

from app.db.qdrant_sparse import sparse_model

EMBEDDING_MODEL = "nomic-embed-text"

embedder = OllamaEmbeddings(model=EMBEDDING_MODEL)

client = QdrantClient(url="http://localhost:6333")


async def retrieve_context(
    query: str,
    user_id: str,
    k: int = 20,
    repo_url: str | None = None,
):
    """Asynchronously retrieve context from vector database."""
    print("hey")
    conditions = [
        FieldCondition(
            key="metadata.user_id",
            match=MatchValue(value=user_id),
        )
    ]

    if repo_url:
        conditions.append(
            FieldCondition(
                key="repo_url",
                match=MatchValue(value=repo_url),
            )
        )

    search_filter = Filter(must=conditions)

    # Run blocking Qdrant operations in thread pool
    collection_info = await asyncio.to_thread(client.get_collection, "documents")
    print(collection_info)

    count_result = await asyncio.to_thread(
        client.count, collection_name="documents", exact=True
    )
    print(count_result)

    scroll_result = await asyncio.to_thread(
        client.scroll,
        collection_name="documents",
        limit=1,
        with_payload=True,
    )
    print(scroll_result)

    # Embedding operations (blocking I/O to LLM)
    dense_vector = await asyncio.to_thread(embedder.embed_query, query)

    # Sparse embedding
    sparse_embedding = await asyncio.to_thread(
        lambda: list(sparse_model.embed([query]))[0]
    )
    sparse_vector = SparseVector(
        indices=sparse_embedding.indices.tolist(),
        values=sparse_embedding.values.tolist(),
    )

    # Query points (blocking I/O)
    dense_results = await asyncio.to_thread(
        client.query_points,
        collection_name="documents",
        query=dense_vector,
        using="dense",
        query_filter=search_filter,
        limit=10,
        with_payload=True,
        with_vectors=False,
    )

    sparse_results = await asyncio.to_thread(
        client.query_points,
        collection_name="documents",
        query=sparse_vector,
        using="sparse",
        query_filter=search_filter,
        limit=10,
        with_payload=True,
        with_vectors=False,
    )

    # ==================================================
    # DENSE RESULTS
    # ==================================================

    print("\n" + "=" * 100)
    print("DENSE FIRST:", dense_results.points[:2])
    print("DENSE VECTOR SEARCH")
    print("=" * 100)

    print("QUERY:", query)
    print("RESULTS:", len(dense_results.points))

    for rank, result in enumerate(dense_results.points, start=1):

        payload = result.payload or {}

        content = (
            payload.get("text")
            or payload.get("page_content")
            or payload.get("content")
            or ""
        )

        print("\n" + "-" * 100)
        print("DENSE RANK:", rank)
        print("DENSE SCORE:", result.score)
        print("ID:", result.id)

        print("\nCONTENT:")
        print(content[:1500])

    # ==================================================
    # SPARSE RESULTS
    # ==================================================

    print("\n" + "=" * 100)
    print("SPARSE VECTOR SEARCH")
    print("=" * 100)

    print("QUERY:", query)
    print("RESULTS:", len(sparse_results.points))

    for rank, result in enumerate(sparse_results.points, start=1):

        payload = result.payload or {}

        content = (
            payload.get("text")
            or payload.get("page_content")
            or payload.get("content")
            or ""
        )

        print("\n" + "-" * 100)
        print("SPARSE RANK:", rank)
        print("SPARSE SCORE:", result.score)
        print("ID:", result.id)

        print("\nCONTENT:")
        print(content[:1500])

    # Fusion (CPU bound, wrap in thread)
    fused_results = await asyncio.to_thread(
        reciprocal_rank_fusion, dense_results.points, sparse_results.points
    )

    print("RRF RESULTS:", len(fused_results))

    for rank, point in enumerate(fused_results[:10], 1):
        print(rank, point.id, point.payload["text"][:150])

    # Reranking (blocking)
    reranked_results = await asyncio.to_thread(
        rerank_documents,
        query=query,
        documents=fused_results,
        top_k=20,
    )

    print("\nRERANKED RESULTS:")

    for i, doc in enumerate(reranked_results, 1):
        print(i, doc.id, doc.payload["text"])

    return reranked_results
