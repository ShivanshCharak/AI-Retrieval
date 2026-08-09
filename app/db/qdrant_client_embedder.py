from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_ollama import OllamaEmbeddings

embedder = OllamaEmbeddings(model="nomic-embed-text")


client = QdrantClient(url="http://localhost:6333")


vector_store = QdrantVectorStore(
    client=client, collection_name="documents", vector_name="dense", embedding=embedder
)
