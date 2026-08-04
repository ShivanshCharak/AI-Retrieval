from pydantic import BaseModel
from app.services.llm.llm_service import llm
from app.db.metadata_store import get_collection_metadata


class ClassificationOutput(BaseModel):
    query_type: str
    confidence: float


def classify_query(query: str):
    metadata = get_collection_metadata()

    structured = llm.with_structured_output(ClassificationOutput)
    prompt = f"""
    Classify the user query into EXACTLY ONE category:

    - intro: Any greeting, small talk, pleasantry, or social question (e.g., "hello", "hi", "how are you doing today?", "good morning", "what's up").
    - simple: A clear, standalone technical question that can be answered directly without domain docs (e.g., "What is Docker?", "What is JSON?").
    - conceptual: Theoretical questions, reasoning ("how/why"), or queries directly related to the collection metadata topics (e.g., PostgreSQL, hybrid search, RAG).
    - sparse: Incomplete or vague TECHNICAL queries that lack context and need keyword/semantic expansion (e.g., "slow query", "auth error", "memory leak", "postgres"). 

    CRITICAL RULE:
    - If a query is a general human greeting or pleasantry, it MUST be 'intro', EVEN IF it asks a question like "how are you?".
    - 'sparse' is ONLY for vague TECHNICAL queries, not social small talk.
    - Only assign conceptual to those queries , which are closesly related to the metadata if not assign them with sparse

    COLLECTION METADATA:
    {metadata}

    Query:
    {query}
    """

    response = structured.invoke(prompt)
    print(response)

    return response.query_type
