from typing import TypedDict, List


class GraphState(TypedDict):
    query: str
    query_type: str
    generated_queries: List[str]
    documents: List[dict]
    reranked_docs: List[dict]
    answer: str
    route: str
    web_search: bool
    userId: str
    deep_search: bool

    trace: List[dict]
