from qdrant_client import QdrantClient
from langchain_ollama import OllamaEmbeddings

client = QdrantClient(url="http://localhost:6333")

embedder = OllamaEmbeddings(model="nomic-embed-text")
