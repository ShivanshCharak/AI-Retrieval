import time as Time
from app.services.llm.llm_service import llm
from pydantic import BaseModel, Field
from typing import Literal
from app.db.metadata_store import get_collection_metadata
from langchain_core.messages import SystemMessage


class RouteDecision(BaseModel):
    # Order matters for structured generation: reasoning must come
    # before route/confidence so the label is conditioned on the reasoning,
    # not the other way around (avoids post-hoc rationalization).
    explanation: str = Field(
        description=(
            "One sentence: identify whether the query refers to (a) the assistant itself, "
            "(b) the user's own data/history, or (c) a subject/entity described in the Metadata. "
            "State which one and why, before choosing a route."
        )
    )
    route: Literal["rag", "product"]
    confidence: float


def graph_router_node(state):
    start = Time.time()

    structured_llm = llm.with_structured_output(RouteDecision)

    metadata = get_collection_metadata()

    static_instruction = f"""
    You are a routing agent.

    Your job is to classify the user's query into exactly one category.

    PRONOUN RULE:
    - "you", "your", or "yourself" refers to the AI assistant.
    - "me", "my", or "myself" refers to the user.

    ENTITY RULE (check this before matching PRODUCT examples on surface wording):
    - If the query refers to a specific person, entity, or subject (by name or
      description) that is NOT the assistant and NOT the user, check whether that
      person/entity/subject is described in the Metadata below.
    - If yes, classify as RAG — the query is asking about content in the knowledge
      base assign it as rag examples.Metadata relevance takes priority over superficial similarity to PRODUCT examples.
    - if query has given you a github link either t has gave you a question with it or not assign it as rag
    - Example pattern: "what does [person mentioned in metadata] do" -> rag
      (because it asks about a subject described in Metadata, not about the assistant)
    

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
    - any attached document, pdf
    - Profile
    - Saved/stored GitHub links
    - Any subject, person, or topic described in the Metadata below
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
            ("human", state["query"]),
        ]
    )

    latency = (Time.time() - start) * 1000

    print("ROUTE:", decision.route)
    print("CONFIDENCE:", decision.confidence)
    print("EXPLANATION:", decision.explanation)  # <-- now you can see WHY

    state["trace"].append(
        {
            "node": "router",
            "latency_ms": latency,
            "confidence": decision.confidence,
            "explanation": decision.explanation,  # <-- log it for debugging
            "input": state["query"],
            "output": decision.route,
        }
    )

    return {"route": decision.route, "confidence": decision.confidence, **state}
