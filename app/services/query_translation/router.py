ROUTING_MAP = {
    "simple": ["multi_query"],
    "sparse": ["multi_query", "hyde"],
    "conceptual": ["multi_query", "step_back"],
}


def route_query(query_type: str):
    return ROUTING_MAP.get(query_type, ["multi_query"])
