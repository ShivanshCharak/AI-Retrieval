from app.services.query_translation.query_classifier import classify_query
from app.services.query_translation.router import route_query

from app.services.query_translation.multi_query import generate_multi_queries
from app.services.query_translation.hyde import generate_hyde
from app.db.metadata_store import get_collection_metadata

from app.services.query_translation.step_back_decomposition import decompose_query


def generate_queries(query: str):
    query_type = classify_query(query)
    techniques = route_query(query_type)
    metadata = get_collection_metadata()

    return execute_techniques(query, techniques, metadata)


def execute_techniques(query: str, techniques: list[str], metadata):
    results = []
    if "multi_query" in techniques:
        results.extend(generate_multi_queries(query, metadata))
    if "decomposition" or "step_back" in techniques:
        results.extend(decompose_query(query))
    if "hyde" in techniques:
        results.append(generate_hyde(query))
    print("results", results)
    return results
