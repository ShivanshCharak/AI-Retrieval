from pydantic import BaseModel

from app.services.llm.llm_service import llm


class CollectionMetadata(BaseModel):
    summary: str
    topics: list[str]


def generate_collection_metadata(docs):

    text = "\n".join(
        doc.page_content[:1000]
        for doc in docs[:5]
    )

    structured = llm.with_structured_output(
        CollectionMetadata
    )

    prompt = f"""
            Analyze this document collection.

            Generate:

            1. Short summary
            2. Top 10 topics

            Document:
            {text}
            """
    return structured.invoke(prompt)