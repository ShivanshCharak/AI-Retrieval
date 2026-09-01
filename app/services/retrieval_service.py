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


def retrieve_context(
    query: str,
    user_id: str,
    k: int = 20,
    repo_url: str | None = None,
):
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
    print(client.get_collection("documents"))

    print(client.count(collection_name="documents", exact=True))

    print(
        client.scroll(
            collection_name="documents",
            limit=1,
            with_payload=True,
        )
    )

    dense_vector = embedder.embed_query(query)

    sparse_embedding = list(sparse_model.embed([query]))[0]
    sparse_vector = SparseVector(
        indices=sparse_embedding.indices.tolist(),
        values=sparse_embedding.values.tolist(),
    )

    dense_results = client.query_points(
        collection_name="documents",
        query=dense_vector,
        using="dense",
        query_filter=search_filter,
        limit=10,
        with_payload=True,
        with_vectors=False,
    )

    sparse_results = client.query_points(
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
    fused_results = reciprocal_rank_fusion(dense_results.points, sparse_results.points)

    print("RRF RESULTS:", len(fused_results))

    for rank, point in enumerate(fused_results[:10], 1):
        print(rank, point.id, point.payload["text"][:150])
    reranked_results = rerank_documents(
        query=query,
        documents=fused_results,
        top_k=20,
    )

    print("\nRERANKED RESULTS:")

    for i, doc in enumerate(reranked_results, 1):
        print(i, doc.id, doc.payload["text"])


if __name__ == "__main__":
    print("hey")

    retrieve_context(
        "In a Bw-Tree, how do delta node update chains interact with garbage collection, and why does this create a different consistency challenge than the one WiscKey faces when reclaiming space in its vLog during compaction?",
        "4",
        5,
    )
