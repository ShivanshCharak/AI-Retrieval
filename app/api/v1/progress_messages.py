PROGRESS_MESSAGES = {
    "input_guard": {
        "title": "Checking your request",
        "description": "Validating the request before processing.",
    },
    "router": {
        "title": "Understanding your question",
        "description": "Determining the best way to answer.",
    },
    "query_generation": {
        "title": "Generating search queries",
        "description": "Creating optimized search terms.",
    },
    "retrieval": {
        "title": "Searching documents",
        "description": "Looking through your uploaded files and knowledge.",
    },
    "fusion": {
        "title": "Combining search results",
        "description": "Merging results from multiple searches.",
    },
    "rerank": {
        "title": "Ranking results",
        "description": "Keeping only the most relevant information.",
    },
    "product_faq": {
        "title": "Preparing response",
        "description": "Generating a response from the product knowledge.",
    },
    "output_guard": {
        "title": "Checking response",
        "description": "Validating the generated response.",
    },
}


def get_progress_message(node: str) -> dict:
    return PROGRESS_MESSAGES.get(
        node,
        {"title": node.replace("_", " ").title(), "description": ""},
    )
