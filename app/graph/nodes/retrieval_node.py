import re
import time
import asyncio

from pydantic import BaseModel
from app.services.retrieval.vector_search import vector_search
from app.services.retrieval.memory_search import memory_search
from app.services.retrieval.github_search import github_parser
from app.services.retrieval_service import retrieve_context


class RetrievalDecision(BaseModel):
    use_memory: bool
    use_vector: bool
    use_graph: bool
    use_repo: bool
    use_bm25: bool
    confidence: float


# ============================================================
# DETERMINISTIC SOURCE DETECTION
# ============================================================


def contains_github_url(query: str) -> bool:
    return bool(
        re.search(
            r"https?://(?:www\.)?github\.com/[^\s]+",
            query,
            re.IGNORECASE,
        )
    )


def contains_repository_reference(query: str) -> bool:
    q = query.lower()

    repository_patterns = [
        "my repository",
        "my repo",
        "github repository",
        "github repo",
        "uploaded repository",
        "uploaded repo",
        "the repository",
        "the repo",
        "this repository",
        "this repo",
        "source code",
        "my codebase",
        "the codebase",
        "this codebase",
        "uploaded project",
        "project files",
        "from my code",
        "from the code",
        "from my repository",
        "from my repo",
        "from the github repo",
        "from the github repository",
        "in my repository",
        "in my repo",
        "in the repository",
        "in the repo",
    ]

    return any(pattern in q for pattern in repository_patterns)


def contains_document_reference(query: str) -> bool:
    q = query.lower()

    document_patterns = [
        "uploaded document",
        "the uploaded document",
        "my uploaded document",
        "uploaded pdf",
        "the uploaded pdf",
        "my uploaded pdf",
        "from the document",
        "from my document",
        "from the uploaded document",
        "from the pdf",
        "from my pdf",
        "from the uploaded pdf",
        "from the notes",
        "from my notes",
        "from the uploaded notes",
        "uploaded files",
        "from the uploaded files",
        "indexed document",
        "indexed documents",
        "uploaded book",
        "from the book",
    ]

    return any(pattern in q for pattern in document_patterns)


def contains_memory_reference(query: str) -> bool:
    q = query.lower()

    memory_patterns = [
        "what do you remember about me",
        "what do you know about me",
        "what are my interests",
        "what are my preferences",
        "what are my likes",
        "what are my dislikes",
        "what do i like",
        "what do i dislike",
        "tell me about myself",
        "tell me about me",
        "describe me",
        "my profile",
        "my background",
        "my experience",
        "my qualifications",
        "my history",
        "what did i ask you",
        "what did i tell you",
        "my saved",
        "my memories",
        "my goals",
    ]

    return any(pattern in q for pattern in memory_patterns)


def deterministic_retrieval_plan(query: str):
    """
    Returns:
        (RetrievalDecision, str)

    Always returns a concrete plan. There is no LLM fallback —
    if no explicit source is detected, a default general-purpose
    plan is used instead.
    """

    # ========================================================
    # 1. GITHUB URL
    # HIGHEST PRIORITY
    # ========================================================

    if contains_github_url(query):
        return (
            RetrievalDecision(
                use_memory=False,
                use_vector=False,
                use_graph=False,
                use_repo=True,
                use_bm25=True,
                confidence=1.0,
            ),
            "GitHub URL detected → repository retrieval",
        )

    repo_requested = contains_repository_reference(query)

    document_requested = contains_document_reference(query)

    memory_requested = contains_memory_reference(query)

    # User explicitly wants repository + document
    if repo_requested and document_requested:
        return (
            RetrievalDecision(
                use_memory=False,
                use_vector=True,
                use_graph=False,
                use_repo=True,
                use_bm25=True,
                confidence=1.0,
            ),
            "Explicit repository + document request",
        )

    # User explicitly wants repository + memory
    if repo_requested and memory_requested:
        return (
            RetrievalDecision(
                use_memory=True,
                use_vector=False,
                use_graph=False,
                use_repo=True,
                use_bm25=True,
                confidence=1.0,
            ),
            "Explicit repository + memory request",
        )

    # User explicitly wants document + memory
    if document_requested and memory_requested:
        return (
            RetrievalDecision(
                use_memory=True,
                use_vector=True,
                use_graph=False,
                use_repo=False,
                use_bm25=True,
                confidence=1.0,
            ),
            "Explicit document + memory request",
        )

    if repo_requested:
        return (
            RetrievalDecision(
                use_memory=False,
                use_vector=False,
                use_graph=False,
                use_repo=True,
                use_bm25=True,
                confidence=1.0,
            ),
            "Explicit repository/source-code request",
        )

    if document_requested:
        return (
            RetrievalDecision(
                use_memory=False,
                use_vector=True,
                use_graph=False,
                use_repo=False,
                use_bm25=True,
                confidence=1.0,
            ),
            "Explicit document request",
        )

    if memory_requested:
        return (
            RetrievalDecision(
                use_memory=True,
                use_vector=False,
                use_graph=False,
                use_repo=False,
                use_bm25=False,
                confidence=1.0,
            ),
            "Explicit memory request",
        )

    # ========================================================
    # 7. NO EXPLICIT SOURCE — DEFAULT PLAN
    #
    # No LLM fallback. Default to vector + bm25 retrieval,
    # which covers the general case of answering from
    # indexed/uploaded content with lexical backup.
    # ========================================================

    return (
        RetrievalDecision(
            use_memory=False,
            use_vector=True,
            use_graph=False,
            use_repo=False,
            use_bm25=True,
            confidence=0.5,
        ),
        "No explicit source detected → default vector + BM25 retrieval",
    )


# ============================================================
# RETRIEVAL NODE
# ============================================================


async def retrieval_node(state):
    start = time.time()

    query = state["query"]
    userId = state["userId"]

    # ========================================================
    # STEP 1 — DETERMINISTIC ROUTING (always deterministic now)
    # ========================================================

    plan, explanation = deterministic_retrieval_plan(query)

    latency = (time.time() - start) * 1000

    print("DETERMINISTIC RETRIEVAL PLAN")
    print("PLAN:", plan)
    print("CONFIDENCE:", plan.confidence)
    print("EXPLANATION:", explanation)

    state["trace"].append(
        {
            "node": "retrieval router",
            "latency_ms": latency,
            "confidence": plan.confidence,
            "input": query,
            "output": plan,
            "routing_type": "deterministic",
            "explanation": explanation,
        }
    )

    # ========================================================
    # STEP 2 — RETRIEVAL
    # ========================================================

    docs = []

    queries = state.get("generated_queries")

    if not queries:
        queries = [query]

    for q in queries:

        if plan.use_memory:
            docs.extend(
                memory_search(
                    q,
                    userId,
                )
            )

        if plan.use_vector:
            docs.extend(await retrieve_context(query, userId))

        if plan.use_repo:
            repo_docs = await github_parser(state)

            if repo_docs:
                docs.extend(repo_docs)

        # Add this later when implemented:
        #
        # if plan.use_graph:
        #     docs.extend(graph_search(q))
        #
        # if plan.use_bm25:
        #     docs.extend(bm25_search(q))

    print("docs", docs)

    return {
        **state,
        "documents": docs,
    }
