import re
import time as Time
from typing import Literal

import json
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage

from app.services.llm.llm_service import llm
from app.db.metadata_store import get_collection_metadata
from app.services.retrieval.github_search import _scope_key


class RouteDecision(BaseModel):
    explanation: str = Field(
        description=(
            "One sentence explaining why the query is routed as " "rag or product."
        )
    )
    route: Literal["rag", "product"]
    confidence: float


# ============================================================
# DETERMINISTIC ROUTING HELPERS
# ============================================================

GITHUB_URL_PATTERN = re.compile(
    r"https?://(?:www\.)?github\.com/[^\s]+",
    re.IGNORECASE,
)


DOCUMENT_REFERENCE_PATTERNS = (
    "uploaded document",
    "uploaded pdf",
    "uploaded file",
    "uploaded files",
    "the uploaded document",
    "the uploaded pdf",
    "the uploaded file",
    "this document",
    "this pdf",
    "this file",
    "the document",
    "the pdf",
    "from the document",
    "from the pdf",
    "from the file",
    "from my document",
    "from my pdf",
    "from my file",
    "based on the document",
    "based on the pdf",
    "based on the file",
    "according to the document",
    "according to the pdf",
    "according to the file",
)


def contains_github_url(query: str) -> bool:
    return bool(GITHUB_URL_PATTERN.search(query))


def contains_document_reference(query: str) -> bool:
    query = query.lower()

    return any(phrase in query for phrase in DOCUMENT_REFERENCE_PATTERNS)


def deterministic_route(query: str):
    """
    Return (route, explanation) when the query can be
    safely classified without an LLM.

    Return None when semantic classification is required.
    """

    if contains_github_url(query):
        return (
            "rag",
            "The query contains a GitHub URL, so it must use repository retrieval.",
        )

    if contains_document_reference(query):
        return (
            "rag",
            "The query explicitly asks for information from an uploaded document or file.",
        )

    return None


# ============================================================
# GRAPH ROUTER
# ============================================================


def graph_router_node(state):
    start = Time.time()

    query = state["query"]

    # --------------------------------------------------------
    # 1. DETERMINISTIC ROUTING
    # --------------------------------------------------------

    deterministic = deterministic_route(query)

    if deterministic is not None:
        route, explanation = deterministic

        latency = (Time.time() - start) * 1000

        print("DETERMINISTIC ROUTE:", route)
        print("CONFIDENCE:", 1.0)
        print("EXPLANATION:", explanation)

        state["trace"].append(
            {
                "node": "router",
                "latency_ms": latency,
                "confidence": 1.0,
                "explanation": explanation,
                "input": query,
                "output": route,
                "routing_type": "deterministic",
            }
        )

        return {
            **state,
            "route": route,
            "confidence": 1.0,
        }

    # --------------------------------------------------------
    # 2. LLM ROUTING
    # --------------------------------------------------------

    structured_llm = llm.with_structured_output(RouteDecision)

    metadata = get_collection_metadata()

    with open(f"scope_cache/{_scope_key(state['userId'])}.json") as f:
        repo_metadata = json.load(f)

    static_instruction = f"""
You are a routing agent.

Your job is to classify the user's query into exactly ONE category:

- PRODUCT
- RAG

Apply these rules:

1. USER DATA

If the user asks about their own:
- data
- preferences
- memories
- history
- saved information
- profile
- goals

classify as RAG.

2. KNOWLEDGE BASE

If the user explicitly asks for information from:
- connected knowledge base
- indexed documents
- saved memories
- repositories
- project files

classify as RAG.

3. ENTITY

If the user asks about a specific person, project,
repository, document, subject, or entity that exists
in the connected knowledge base, classify as RAG.

4. ASSISTANT

"you", "your", or "yourself" refers to the AI assistant.

"me", "my", or "myself" refers to the user.

Questions about the AI assistant itself are PRODUCT.

Examples:

"How do you work?" -> PRODUCT
"What model are you running?" -> PRODUCT
"What are your capabilities?" -> PRODUCT
"Explain your architecture" -> PRODUCT

5. PRODUCT

General questions about the assistant or its capabilities
that do not request information from the connected
knowledge base are PRODUCT.

Metadata:

{metadata}

Repository metadata:

{repo_metadata}
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

    print("LLM ROUTE:", decision.route)
    print("CONFIDENCE:", decision.confidence)
    print("EXPLANATION:", decision.explanation)

    state["trace"].append(
        {
            "node": "router",
            "latency_ms": latency,
            "confidence": decision.confidence,
            "explanation": decision.explanation,
            "input": query,
            "output": decision.route,
            "routing_type": "llm",
        }
    )

    return {
        **state,
        "route": decision.route,
        "confidence": decision.confidence,
    }
