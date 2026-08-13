# input_validation.py
from .llm_guard import guard
from app.graph.state import GraphState
from app.db.metadata_store import get_collection_metadata


def validate_input(state: GraphState):

    prompt = f"""
    You are a safety classifier.

    Classify the following user message as exactly one of:

    safe
    unsafe

    Questions asking the assistant to explain, summarize, analyze,
    retrieve, or reason about documents/code/database architecture
    provided by the user are SAFE.
    - User can upload a doc and ask question to that or he can add a link and ask questions from the githubrepo he is adding these queries are safe
    Do not classify a request as unsafe merely because it mentions:
    - databases
    - source code
    - codebases
    - uploaded files
    - credentials as a topic
    - system architecture


    User message:
    {state["query"]}
    """

    response = guard.invoke(prompt)

    lines = response.content.strip().lower().splitlines()
    verdict = lines[0]
    category = lines[1] if len(lines) > 1 else None
    if verdict == "unsafe" and category == "s8":
        is_safe = True
    else:
        is_safe = verdict == "safe"

    return {
        "input_guard_result": {
            "is_safe": is_safe,
            "raw": response.content,
            "category": category,
        },
        "blocked": not is_safe,
    }
