from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.services.query_translation.product_faq import product_faq


from app.graph.nodes.graph_router import graph_router_node
from app.graph.nodes_med import generated_queries, fusion_node, rerank_nodes
from app.graph.nodes.retrieval_node import retrieval_node

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


# workflow.add_node("simple_answers", simple_answers)
workflow.add_node("product_faq", product_faq)
workflow.set_entry_point("router")

# workflow.add_edge("simple_answers", "product_faq")

workflow.add_edge("query_generation", "retrieval")

workflow.add_edge("retrieval", "fusion")

workflow.add_edge("fusion", "rerank")

workflow.add_edge("rerank", END)

workflow.add_conditional_edges(
    "router",
    route_decision,
    {"deep": "query_generation", "product": "product_faq", "quick": "retrieval"},
)


graph = workflow.compile()
