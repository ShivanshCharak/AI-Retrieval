from app.db.neo4j_client import driver


def graph_search(
    query: str,
    limit: int = 5
):

    with driver.session() as session:

        result = session.run(
            """
            MATCH (d:Document)
            WHERE d.content CONTAINS $query
            RETURN d.content AS content
            LIMIT $limit
            """,
            query=query,
            limit=limit
        )

        docs = []

        for row in result:

            docs.append(
                {
                    "content": row["content"],
                    "score": 0.5,
                    "source": "neo4j"
                }
            )

        return docs