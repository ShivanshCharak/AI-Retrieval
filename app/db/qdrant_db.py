from qdrant_client.models import (
    VectorParams,
    Distance,
    SparseVectorParams,
)
from qdrant_client import QdrantClient

client = QdrantClient("http://localhost:6333")

client.create_collection(
    collection_name="documents",
    vectors_config={
        "dense": VectorParams(
            size=768,
            distance=Distance.COSINE,
        )
    },
    sparse_vectors_config={"sparse": SparseVectorParams()},
)
