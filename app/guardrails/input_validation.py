from .llm_guard import guard
from app.graph.graph import GraphState


def validate_input(state: GraphState):
    prompt = f"""
    Task: Check if there is unsafe content in the user message according to the safety policy.

    <BEGIN CONVERSATION>
    User:
    {state['query']}
    <END CONVERSATION>
"""
    response = guard.invoke(prompt)
    return {
        "content": response.content,
        "duration": response.response_metadata.total_duration,
    }
