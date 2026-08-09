from app.services.query_translation.translation_service import generate_queries


from app.services.fusion.rrf import reciprocal_rank_fusion
from app.services.reranking.rerank import rerank_documents

from app.services.llm.llm_service import llm


def generated_queries(state):
    return {"generated_queries": generate_queries(state["query"])}


def fusion_node(state):
    return {"documents": reciprocal_rank_fusion(state["documents"])}


def rerank_nodes(state):
    return {"reranked_docs": rerank_documents(state["query"], state["documents"])}
