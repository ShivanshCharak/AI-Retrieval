from app.db.qdrant_client_embedder import client

offset = None
while True:
    points, offset = client.scroll(
        collection_name="documents",
        limit=1000000,
        offset=offset,
        with_payload=True,
        with_vectors=False,
    )

    with open("./documents.txt", "w") as f:
        f.write(str(points))

    if offset is None:
        break
