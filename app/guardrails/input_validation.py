# input_validation.py
from .llm_guard import guard
from app.graph.state import GraphState


def validate_input(state: GraphState):
    print("validating inpuy")
    prompt = f"""
    You are a safety classifier.

    Classify the following user message as exactly one of:

    safe
    unsafe


    User message:
    {state["query"]}
    """

    response = guard.invoke(prompt)
    print("response", response)
    verdict = response.content.strip().lower()
    print("verdict", verdict)
    is_safe = verdict.startswith("safe")

    return {
        "input_guard_result": {
            "is_safe": is_safe,
            "raw": response.content,
        },
        "blocked": not is_safe,
    }
