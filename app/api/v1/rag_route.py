from sqlalchemy import select

from app.db.models import Conversation
from app.services.llm.llm_service import llm
from app.guardrails.output_validation import validate_output
from app.graph.nodes.memory import save_memory
from pydantic import BaseModel
from app.api.v1.sse_utils import sse_event
from app.api.v1.rag_context import format_docs_for_prompt
from app.api.v1.rag_prompt import build_rag_prompt

CHUNK_SIZE = 20


class AnswerWithTitle(BaseModel):
    answer: str
    topic: str


async def handle_rag_route(final_state, user_id, message, conversation_id, db):
    # Look the conversation up FIRST. The original code only checked this
    # after already paying for the LLM call, so a bad conversation_id
    # silently wasted a full generation before erroring out.
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )

    if not conversation:
        yield sse_event("error", message="Conversation not found")
        return

    docs = final_state.get("reranked_docs", [])
    formatted = format_docs_for_prompt(docs)

    prompt = build_rag_prompt(message, formatted.context_str)

    structured_llm = llm.with_structured_output(AnswerWithTitle)
    print(structured_llm)
    response = await structured_llm.ainvoke(prompt)

    conversation.title = response.topic
    conversation.sources = formatted.sources
    db.commit()

    full_answer = response.answer
    title = response.topic

    guard_result = validate_output(full_answer)

    if not guard_result["is_safe"]:
        yield sse_event(
            "guardrail",
            blocked=True,
            message="Response blocked by guardrail",
        )
        return

    for i in range(0, len(full_answer), CHUNK_SIZE):
        yield sse_event("token", content=full_answer[i : i + CHUNK_SIZE])

    save_memory(userId=user_id, message=message, db=db)

    trace = final_state.get("trace", [])
    confidence = trace[-1].get("confidence") if trace else None
    latency_ms = trace[-1].get("latency_ms") if trace else None

    yield sse_event(
        "complete",
        confidence=confidence,
        title=title,
        latency_ms=latency_ms,
        trace=trace,
        sources=formatted.sources,
        output_guard={"is_safe": True},
    )
