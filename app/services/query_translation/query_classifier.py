from pydantic import BaseModel
from app.services.llm.llm_service import llm


class ClassificationOutput(BaseModel):
    query_type: str
    confidence: float


def classify_query(query: str):
    structured = llm.with_structured_output(ClassificationOutput)

    prompt = f"""
    Classify query into ONE category:
    - intro: if user ask for hello, hi
    - simple: single fact question
    - complex: multi-part reasoning or multiple concepts
    - sparse: vague query needing semantic expansion
    - conceptual: theory or "why/how" reasoning

    Query:
    {query}
    """

    response = structured.invoke(prompt)
    print(response)

    return response.query_type
