# services/ingestion/ingestion_service.py

from app.db.qdrant_client_embedder import vector_store
from .loader import document_loader
import time

from app.services.ingestion.chunker import split_documents
from app.services.ingestion.metadata_extraction import generate_collection_metadata
from app.db.metadata_store import store_collection_metadata

from langchain_qdrant import QdrantVectorStore
from app.db.qdrant_client_embedder import embedder, client

from app.services.ingestion.graph_builder import create_document_nodes


def ingest_document(path: str, userId: str):
    start = time.perf_counter()
    docs = document_loader(path)
    print(f"Loading document: {time.perf_counter() - start:.2f}s")

    start = time.perf_counter()
    metadata = generate_collection_metadata(docs)
    print(f"Metadata generation: {time.perf_counter() - start:.2f}s")

    start = time.perf_counter()
    store_collection_metadata(metadata, userId)
    print(f"Store metadata: {time.perf_counter() - start:.2f}s")

    start = time.perf_counter()
    chunks = split_documents(docs)
    print(f"Chunking: {time.perf_counter() - start:.2f}s")

    for chunk in chunks:
        chunk.metadata["user_id"] = userId

    start = time.perf_counter()
    store_chunks(chunks)
    print(f"Embedding + upload: {time.perf_counter() - start:.2f}s")

    start = time.perf_counter()
    create_document_nodes(chunks)
    print(f"Graph building: {time.perf_counter() - start:.2f}s")
    print(len(docs))
    print(len(chunks))

    return {"documents": len(docs), "chunks": len(chunks)}


def store_chunks(chunks):
    texts = [chunk.page_content for chunk in chunks]

    start = time.perf_counter()
    vector_store.add_documents(chunks)
    print(f"Embedding only: {time.perf_counter() - start:.2f}s")
