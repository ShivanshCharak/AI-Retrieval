from langgraph.graph import StateGraph, END
from app.graph.state import GraphState

from app.graph.nodes import (
    generated_queries,
    retrieval_node,
    fusion_node,
    rerank_nodes,
    graph_router_node,
    simple_answers,
)

workflow = StateGraph(GraphState)


def route_decision(state):
    if state["route"] == "rag" and state["deep_search"]:
        return "deep"
    elif state["route"] == "rag":
        return "quick"
    else:
        return "product"


def route_web_search(state):
    if state["web_search"]:
        return state["web_search"]
    return "document_search"


workflow.add_node("query_generation", generated_queries)
workflow.add_node("router", graph_router_node)

workflow.add_node("retrieval", retrieval_node)

workflow.add_node("fusion", fusion_node)

workflow.add_node("rerank", rerank_nodes)


workflow.add_node("simple_answers", simple_answers)
workflow.set_entry_point("router")

workflow.add_edge("query_generation", "retrieval")

workflow.add_edge("retrieval", "fusion")

workflow.add_edge("fusion", "rerank")

workflow.add_edge("rerank", END)

workflow.add_conditional_edges(
    "router", route_decision, {"deep": "query_generation", "product": "simple_answers", "quick": "retrieval"}
)


graph = workflow.compile()
