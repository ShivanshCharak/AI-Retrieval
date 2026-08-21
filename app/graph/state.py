from typing import TypedDict, List


class GraphState(TypedDict, total=False):
    query: str
    userId: int

    web_search: bool
    deep_search: bool
    topic: str

    route: str

    generated_queries: list
    documents: list
    reranked_docs: list

    answer: str

    trace: list

    # Guardrails
    blocked: bool
    block_reason: str
