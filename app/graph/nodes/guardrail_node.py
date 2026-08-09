# app/graph/nodes/guardrail_nodes.py
from app.guardrails.input_validation import validate_input

# from app.guardrails.llm_guard import check_llm_safety
from app.guardrails.output_validation import validate_output
from app.graph.state import GraphState


def input_guard_node(state: GraphState):
    result = validate_input(state)
    if not result["input_guard_result"]["is_safe"]:

        # short-circuit: set a flag the router / downstream can check
        return {
            **state,
            "blocked": True,
            "block_reason": result["input_guard_result"]["raw"],
        }
    return {**state, "blocked": False}


def output_guard_node(state: GraphState):
    result = validate_output(state)
    if not result["output_guard_result"]["is_safe"]:
        return {**state, "answer": "I can't provide that response.", "blocked": True}
    return state
