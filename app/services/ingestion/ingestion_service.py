import time
import uuid
import asyncio

from qdrant_client.models import PointStruct, SparseVector

from app.db.qdrant_client_embedder import client, embedder
from app.db.qdrant_sparse import sparse_model
from app.db.metadata_store import store_collection_metadata

from .loader import document_loader
from .metadata_extraction import generate_collection_metadata

from app.services.ingestion.ingestion_helper.chunker import split_documents
from app.services.ingestion.ingestion_helper.text_cleaner import (
    clean_documents,
    merge_document,
)
from app.services.ingestion.ingestion_helper.chunk_quality import filter_chunks
from app.services.ingestion.graph_builder import create_document_nodes


async def ingest_document(
    path: str,
    userId: str,
):
    """Asynchronously ingest a document into the vector store."""
    total_start = time.perf_counter()

    start = time.perf_counter()
    docs = await asyncio.to_thread(document_loader, path)
    loaded_pages = len(docs)

    print(f"Loading: {time.perf_counter() - start:.2f}s")
    print(f"Loaded pages: {loaded_pages}")

    start = time.perf_counter()
    docs = await asyncio.to_thread(clean_documents, docs)
    merged_doc = await asyncio.to_thread(merge_document, docs)

    print(f"Cleaning + merging: {time.perf_counter() - start:.2f}s")
    print(f"Merged text: {len(merged_doc.page_content):,} chars")

    start = time.perf_counter()
    metadata = await asyncio.to_thread(generate_collection_metadata, merged_doc)

    print(f"Metadata generation: {time.perf_counter() - start:.2f}s")

    start = time.perf_counter()
    await store_collection_metadata(metadata, userId)

    print(f"Store metadata: {time.perf_counter() - start:.2f}s")

    start = time.perf_counter()
    chunks = await asyncio.to_thread(split_documents, [merged_doc])
    print(chunks)

    print(f"Chunking: {time.perf_counter() - start:.2f}s")
    print(f"Generated chunks: {len(chunks)}")

    start = time.perf_counter()
    valid_chunks, rejected_chunks = await asyncio.to_thread(filter_chunks, chunks)

    print(f"Quality filtering: {time.perf_counter() - start:.2f}s")
    print(f"Valid chunks: {len(valid_chunks)}")
    print(f"Rejected chunks: {len(rejected_chunks)}")

    for chunk in valid_chunks:
        chunk.metadata["user_id"] = userId
        chunk.metadata["ingestion_version"] = "v2"

    start = time.perf_counter()
    await store_chunks_async(valid_chunks)

    print(f"Embedding + upload: {time.perf_counter() - start:.2f}s")

    start = time.perf_counter()
    await asyncio.to_thread(create_document_nodes, valid_chunks)

    print(f"Graph building: {time.perf_counter() - start:.2f}s")

    total_time = time.perf_counter() - total_start

    print("\n" + "=" * 60)
    print(f"Total ingestion: {total_time:.2f}s")
    print(f"Pages loaded: {loaded_pages}")
    print(f"Chunks created: {len(chunks)}")
    print(f"Chunks stored: {len(valid_chunks)}")
    print(f"Chunks rejected: {len(rejected_chunks)}")
    print("=" * 60)

    return {
        "documents": loaded_pages,
        "chunks_created": len(chunks),
        "chunks_stored": len(valid_chunks),
        "chunks_rejected": len(rejected_chunks),
    }


async def store_chunks_async(chunks):
    """Asynchronously store chunks in vector database."""
    if not chunks:
        return

    # Run blocking embedding operations in thread pool
    texts = [chunk.page_content for chunk in chunks]

    # Dense embeddings
    dense_embeddings = await asyncio.to_thread(embedder.embed_documents, texts)

    # Sparse BM25 embeddings
    sparse_embeddings = await asyncio.to_thread(lambda: list(sparse_model.embed(texts)))

    points = []

    for i, chunk in enumerate(chunks):
        sparse = sparse_embeddings[i]

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

    # Upsert to Qdrant (blocking but necessary)
    await asyncio.to_thread(
        client.upsert,
        collection_name="documents",
        points=points,
    )


if __name__ == "__main__":
    # For direct execution, run with asyncio
    asyncio.run(
        ingest_document(
            "/home/shivansh/Downloads/database-internals-9781492040347.pdf",
            "4",
        )
    )
