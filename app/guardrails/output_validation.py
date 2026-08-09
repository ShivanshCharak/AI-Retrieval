# output_validation.py
from .llm_guard import guard
from app.graph.state import GraphState


def validate_output(state: GraphState):
    prompt = f"""
    Task: Check if there is unsafe content in the AI assistant's response according to the safety policy.

    <BEGIN CONVERSATION>
    Assistant:
    {state['answer']}
    <END CONVERSATION>
    """
    response = guard.invoke(prompt)
    verdict = response.content.strip().lower()
    is_safe = verdict.startswith("safe")

    return {
        "output_guard_result": {
            "is_safe": is_safe,
            "raw": response.content,
            "duration": response.response_metadata.total_duration,
        },
        "blocked": not is_safe,
        "answer": state["answer"] if is_safe else "I can't share that response.",
    }
