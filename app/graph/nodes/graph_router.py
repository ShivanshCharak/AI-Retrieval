import time as Time
from app.services.llm.llm_service import llm
from pydantic import BaseModel
from typing import Literal
from app.db.metadata_store import get_collection_metadata
from langchain_core.messages import SystemMessage


class RouteDecision(BaseModel):
    route: Literal["rag", "product"]
    confidence: float


def graph_router_node(query):
    start = Time.time()

    structured_llm = llm.with_structured_output(RouteDecision)

    metadata = get_collection_metadata()

    static_instruction = f"""
    You are a routing agent.

    Your job is to classify the user's query into exactly one category.

    PRONOUN RULE:
    - "you", "your", or "yourself" refers to the AI assistant.
    - "me", "my", or "myself" refers to the user.

    Return exactly one route:

    PRODUCT:
    - Questions about the AI assistant itself
    - Architecture
    - System design
    - How the system works
    - Models
    - Capabilities
    - Greetings and conversational wishes

    Examples:
    - "how do you work" -> product
    - "what does this system use" -> product
    - "hello" -> product
    - "what model are you running" -> product

    RAG:
    - User's own data
    - Preferences
    - Likes/dislikes
    - Memories
    - History
    - Saved items
    - Goals
    - Profile
    - Metadata
    - Saved/stored GitHub links
    - Knowledge/information that should be retrieved from the connected knowledge base

    Examples:
    - "what are my saved preferences" -> rag
    - "what did I ask you yesterday" -> rag
    - "https://github.com/username" -> rag
    - "what is a B-tree index" -> rag

    CONFIDENCE:
    Return a number between 0.0 and 1.0 representing how confident
    you are in the selected route.

    Metadata:
    {metadata}
    """

    system_message = SystemMessage(
        content=[
            {
                "type": "text",
                "text": static_instruction,
                "cache_control": {"type": "ephemeral"},
            }
        ]
    )

    decision = structured_llm.invoke(
        [
            system_message,
            ("human", query),
        ]
    )

    latency = (Time.time() - start) * 1000

    print("ROUTE:", decision.route)
    print("CONFIDENCE:", decision.confidence)

    print("\nADDITIONAL KWARGS:")
    print(decision.additional_kwargs)

    return {
        "route": decision.route,
        "confidence": decision.confidence,
        "trace": {
            "node": "router",
            "latency_ms": latency,
            "confidence": decision.confidence,
            "input": query,
            "output": decision.route,
        },
    }
