from qdrant_client import QdrantClient

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
from langchain_ollama import OllamaEmbeddings

from app.db.qdrant_sparse import sparse_model

EMBEDDING_MODEL = "nomic-embed-text"

embedder = OllamaEmbeddings(model=EMBEDDING_MODEL)

client = QdrantClient(url="http://localhost:6333")


def retrieve_context(
    query: str,
    user_id: int,
    k: int = 20,
    repo_url: str | None = None,
):

    # ==================================================
    # 1. Build filter
    # ==================================================

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

    # ==================================================
    # 2. Dense query embedding
    # ==================================================

    dense_vector = embedder.embed_query(query)

    # ==================================================
    # 3. Sparse BM25 query embedding
    # ==================================================

    sparse_embedding = list(sparse_model.embed([query]))[0]

    sparse_vector = SparseVector(
        indices=sparse_embedding.indices.tolist(),
        values=sparse_embedding.values.tolist(),
    )

    # ==================================================
    # 4. Hybrid retrieval + RRF
    # ==================================================

    results = client.query_points(
        collection_name="documents",
        prefetch=[
            # ------------------------------------------
            # Dense retrieval
            # ------------------------------------------
            Prefetch(
                query=dense_vector,
                using="dense",
                filter=search_filter,
                limit=40,
            ),
            # ------------------------------------------
            # Sparse BM25 retrieval
            # ------------------------------------------
            Prefetch(
                query=sparse_vector,
                using="sparse",
                filter=search_filter,
                limit=40,
            ),
        ],
        # ----------------------------------------------
        # Reciprocal Rank Fusion
        # ----------------------------------------------
        query=FusionQuery(fusion=Fusion.RRF),
        limit=k,
        with_payload=True,
        with_vectors=False,
    )

    # ==================================================
    # 5. Debug retrieved results
    # ==================================================

    print("\n" + "=" * 100)
    print("HYBRID RETRIEVAL")
    print("QUERY:", query)
    print("RESULTS:", len(results.points))

    for rank, result in enumerate(
        results.points,
        start=1,
    ):

        payload = result.payload or {}

        content = (
            payload.get("text")
            or payload.get("page_content")
            or payload.get("content")
            or ""
        )

        print("\n" + "-" * 100)

        print("RANK:", rank)
        print("RRF SCORE:", result.score)
        print("ID:", result.id)

        print("\nCONTENT:")
        print(content[:1500])

    # ==================================================
    # 6. Convert Qdrant results -> LangChain Documents
    # ==================================================

    documents = []

    for result in results.points:

        payload = result.payload or {}

        content = (
            payload.get("text")
            or payload.get("page_content")
            or payload.get("content")
            or ""
        )

        # ----------------------------------------------
        # Preserve stored metadata
        # ----------------------------------------------

        metadata = payload.get("metadata", {}).copy()

        # ----------------------------------------------
        # Add retrieval information
        # ----------------------------------------------

        metadata["score"] = result.score
        metadata["qdrant_id"] = result.id

        # ----------------------------------------------
        # Create LangChain Document
        # ----------------------------------------------

        documents.append(
            Document(
                page_content=content,
                metadata=metadata,
            )
        )

    # ==================================================
    # 7. Debug final Documents
    # ==================================================

    print("\n" + "=" * 100)
    print("FINAL LANGCHAIN DOCUMENTS")
    print("DOCUMENT COUNT:", len(documents))

    for rank, doc in enumerate(
        documents,
        start=1,
    ):

        print("\n" + "-" * 100)

        print("DOCUMENT:", rank)
        print("CONTENT LENGTH:", len(doc.page_content))
        print("CONTENT:")
        print(doc.page_content[:1000])

        print("\nMETADATA:")
        print(doc.metadata)

    # ==================================================
    # 8. Return LangChain Documents
    # ==================================================

    return documents
