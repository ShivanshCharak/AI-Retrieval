
from app.db.neo4j_client import (
    driver
)


def create_document_nodes(chunks):

    with driver.session() as session:

        for idx, chunk in enumerate(chunks):

            session.run(
                """
                CREATE (d:Document {
                    id:$id,
                    content:$content
                })
                """,
                id=idx,
                content=chunk.page_content
            )