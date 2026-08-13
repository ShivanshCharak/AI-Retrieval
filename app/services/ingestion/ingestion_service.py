import time

from app.db.qdrant_client_embedder import vector_store

from .loader import document_loader
from app.services.ingestion.ingestion_helper.chunker import split_documents
from app.services.ingestion.ingestion_helper.text_cleaner import clean_documents
from app.services.ingestion.ingestion_helper.chunk_quality import filter_chunks
from app.db.qdrant_client_embedder import embedder
from langchain_qdrant.sparse_embeddings import SparseVector
import uuid
from app.db.qdrant_client_embedder import client
from qdrant_client.models import PointStruct
from app.db.qdrant_sparse import sparse_model
from .metadata_extraction import (
    generate_collection_metadata,
)

from qdrant_client.models import (
    PointStruct,
    NamedVector,
    NamedSparseVector,
    SparseVector,
)
from app.db.metadata_store import (
    store_collection_metadata,
)

from app.services.ingestion.graph_builder import (
    create_document_nodes,
)


def ingest_document(
    path: str,
    userId: str,
):

    total_start = time.perf_counter()

    # =========================================================
    # 1. LOAD
    # =========================================================

    start = time.perf_counter()

    docs = document_loader(path)

    print(f"Loading document: " f"{time.perf_counter() - start:.2f}s")

    print(f"Loaded documents/pages: {len(docs)}")

    # =========================================================
    # 2. NORMALIZE / CLEAN
    # =========================================================

    start = time.perf_counter()

    docs = clean_documents(docs)

    print(f"Cleaning: " f"{time.perf_counter() - start:.2f}s")

    print(f"Documents after cleaning: {len(docs)}")

    # =========================================================
    # 3. GENERATE DOCUMENT METADATA
    # =========================================================

    start = time.perf_counter()

    metadata = generate_collection_metadata(docs)
    print(metadata)

    print(f"Metadata generation: " f"{time.perf_counter() - start:.2f}s")

    # =========================================================
    # 4. STORE COLLECTION METADATA
    # =========================================================

    start = time.perf_counter()

    store_collection_metadata(
        metadata,
        userId,
    )

    print(f"Store metadata: " f"{time.perf_counter() - start:.2f}s")

    # =========================================================
    # 5. CHUNK
    # =========================================================

    start = time.perf_counter()

    chunks = split_documents(docs)

    print(f"Chunking: " f"{time.perf_counter() - start:.2f}s")

    print(f"Generated chunks: {len(chunks)}")

    # =========================================================
    # 6. QUALITY FILTER
    # =========================================================

    start = time.perf_counter()

    valid_chunks, rejected_chunks = filter_chunks(chunks)
    valid_chunks, rejected_chunks = filter_chunks(chunks)

    print("\n" + "=" * 80)
    print("REJECTED CHUNKS")
    print("=" * 80)

    for i, chunk in enumerate(rejected_chunks[:20]):

        print(f"\nREJECTED #{i + 1}")

        print(chunk.page_content[:500])

        print(
            "METADATA:",
            chunk.metadata,
        )

    print("=" * 80)

    print(f"Quality filtering: " f"{time.perf_counter() - start:.2f}s")

    print(f"Valid chunks: {len(valid_chunks)}")

    print(f"Rejected chunks: {len(rejected_chunks)}")

    # =========================================================
    # 7. ADD METADATA
    # =========================================================

    for chunk in valid_chunks:
        print(chunk)

        chunk.metadata["user_id"] = userId

        chunk.metadata["ingestion_version"] = "v2"

    # =========================================================
    # 8. STORE IN QDRANT
    # =========================================================

    start = time.perf_counter()

    store_chunks(valid_chunks)

    print(f"Embedding + upload: " f"{time.perf_counter() - start:.2f}s")

    # =========================================================
    # 9. BUILD GRAPH
    # =========================================================

    start = time.perf_counter()

    create_document_nodes(valid_chunks)

    print(f"Graph building: " f"{time.perf_counter() - start:.2f}s")

    # =========================================================
    # 10. SUMMARY
    # =========================================================

    print("\n" + "=" * 80)

    print(f"Total ingestion time: " f"{time.perf_counter() - total_start:.2f}s")

    print(f"Pages/documents: {len(docs)}")

    print(f"Chunks created: {len(chunks)}")

    print(f"Chunks stored: {len(valid_chunks)}")

    print(f"Chunks rejected: {len(rejected_chunks)}")

    print("=" * 80)

    return {
        "documents": len(docs),
        "chunks_created": len(chunks),
        "chunks_stored": len(valid_chunks),
        "chunks_rejected": len(rejected_chunks),
    }


def store_chunks(chunks):
    print("before chunk")
    if not chunks:
        print("no chunks found")
        return

    texts = [chunk.page_content for chunk in chunks]

    # Dense embeddings
    print("embedding")
    dense_embeddings = embedder.embed_documents(texts)
    print("dense embeddes")

    # Sparse BM25 embeddings
    sparse_embeddings = list(sparse_model.embed(texts))
    print("Sparse embedded")

    points = []

    for i, chunk in enumerate(chunks):

        sparse = sparse_embeddings[i]

        sparse_vector = SparseVector(
            indices=sparse.indices.tolist(),
            values=sparse.values.tolist(),
        )

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector={
                    "dense": dense_embeddings[i],
                    "sparse": SparseVector(
                        indices=sparse.indices.tolist(),
                        values=sparse.values.tolist(),
                    ),
                },
                payload={
                    "text": chunk.page_content,
                    "metadata": chunk.metadata,
                },
            )
        )
    client.upsert(
        collection_name="documents",
        points=points,
    )
