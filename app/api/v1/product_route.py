from app.api.v1.sse_utils import sse_event
from app.graph.nodes.memory import save_memory


async def handle_product_route(final_state, user_id, message, db):
    """Stream the answer for the 'product' route and persist memory."""
    answer = final_state.get("answer", "")
    topic = final_state.get("topic", "")

    if answer:
        yield sse_event("token", title=topic, content=answer)

    yield sse_event(
        "complete",
        title=topic,
        trace=final_state.get("trace", []),
    )

    save_memory(userId=user_id, message=message, db=db)
