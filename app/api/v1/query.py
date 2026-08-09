import json

import jwt
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.v1.ingestion import ingest
from app.db.database import get_db
from app.graph.graph import graph
from app.graph.nodes.memory import save_memory
from app.graph.state import GraphState
from app.services.llm.llm_service import llm

router = APIRouter()

SECRET_KEY = "4WfP4JbL6lLQ5zQZ_8K4YxW5RkM8bM7T9dN2L8xR1cA"


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


@router.post("/chat")
async def query(
    request: Request,
    message: str = Form(...),
    model: str = Form(...),
    web_search: bool = Form(False),
    file: UploadFile | None = File(None),
    deep_search: bool = Form(False),
    db: Session = Depends(get_db),
):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=["HS256"],
    )

    user_id = payload["user_id"]

    if file and file.size > 0:
        await ingest(file, user_id)

    async def generate():

        final_state = None

        initial_state: GraphState = {
            "query": message,
            "userId": user_id,
            "trace": [],
            "deep_search": deep_search,
            "web_search": web_search,
        }

        try:

            async for mode, data in graph.astream(
                initial_state,
                stream_mode=["updates", "values"],
            ):

                # =========================================
                # NODE UPDATES
                # =========================================

                if mode == "updates":

                    if not data:
                        continue

                    node = next(iter(data))
                    node_state = data[node]

                    print("NODE UPDATE:", node, node_state)

                    # =====================================
                    # INPUT GUARD
                    # =====================================

                    if node == "input_guard":

                        if node_state.get("blocked", False):

                            print("🚫 INPUT BLOCKED")
                            print(
                                "REASON:",
                                node_state.get("block_reason"),
                            )

                            yield (f"data: {json.dumps({
                                    'type': 'guardrail',
                                    'blocked': True,
                                    'message': 'Request blocked by guardrail',
                                })}\n\n")

                            # IMPORTANT:
                            # Do not wait for final_state.
                            # The graph is already terminating.
                            return

                    # =====================================
                    # NORMAL PROGRESS
                    # =====================================

                    progress = PROGRESS_MESSAGES.get(
                        node,
                        {
                            "title": node.replace("_", " ").title(),
                            "description": "",
                        },
                    )

                    yield (f"data: {json.dumps({
                            'type': 'progress',
                            'stage': node,
                            'title': progress['title'],
                            'description': progress['description'],
                        })}\n\n")

                # =========================================
                # COMPLETE GRAPH STATE
                # =========================================

                elif mode == "values":

                    final_state = data

        except Exception as exc:

            print("GRAPH ERROR:", repr(exc))

            yield (f"data: {json.dumps({
                    'type': 'error',
                    'message': 'An error occurred while processing the request.',
                })}\n\n")

            return

        # =============================================
        # NO FINAL STATE
        # =============================================

        if final_state is None:

            yield (f"data: {json.dumps({
                    'type': 'error',
                    'message': 'Graph execution failed',
                })}\n\n")

            return

        print("FINAL STATE:", final_state)

        # =============================================
        # ROUTE
        # =============================================

        route = final_state.get("route")

        if not route:

            yield (f"data: {json.dumps({
                    'type': 'error',
                    'message': 'No route was produced by the graph.',
                })}\n\n")

            return

        # =============================================
        # PRODUCT ROUTE
        # =============================================

        if route == "product":

            print("PRODUCT ROUTE")

            answer = final_state.get("answer", "")

            if answer:

                yield (f"data: {json.dumps({
                        'type': 'token',
                        'content': answer,
                    })}\n\n")

            yield (f"data: {json.dumps({
                    'type': 'complete',
                    'trace': final_state.get("trace", []),
                })}\n\n")

            save_memory(
                userId=user_id,
                message=message,
                db=db,
            )

            return

        # =============================================
        # RAG ROUTE
        # =============================================

        elif route == "rag":

            print("RAG ROUTE")

            docs = final_state.get(
                "reranked_docs",
                [],
            )

            context = "\n\n".join(
                (
                    json.dumps(doc["content"])
                    if isinstance(doc.get("content"), dict)
                    else str(doc.get("content", ""))
                )
                for doc in docs
            )

            prompt = f"""
You are an answer generator.

Answer the user's question using ONLY the provided context.

The words "I", "me", and "my" always refer to the USER, not you.

Use all relevant information present in the context.

If the context contains only part of the requested information,
answer using the information that IS present.

Do not refuse simply because some information is missing.

Only say "I don't know" when the requested information is
completely absent from the context.

Never invent or infer details that are not explicitly supported
by the context.

If the context says "User", change it to "you" when appropriate.

If the user asks "who am I?" and the context does not provide
enough information, say you don't have enough information.

Question:
{message}

Context:
{context}
"""

            # =========================================
            # STREAM RAG TOKENS
            # =========================================

            full_answer = ""

            async for chunk in llm.astream(prompt):

                if not chunk.content:
                    continue

                token = chunk.content

                full_answer += token

                yield (f"data: {json.dumps({
                        'type': 'token',
                        'content': token,
                    })}\n\n")

            # =========================================
            # SAVE MEMORY
            # =========================================

            save_memory(
                userId=user_id,
                message=message,
                db=db,
            )

            # =========================================
            # TRACE
            # =========================================

            trace = final_state.get(
                "trace",
                [],
            )

            confidence = None
            latency_ms = None

            if trace:

                confidence = trace[-1].get("confidence")

                latency_ms = trace[-1].get("latency_ms")

            # =========================================
            # COMPLETE
            # =========================================

            yield (f"data: {json.dumps({
                    'type': 'complete',
                    'confidence': confidence,
                    'latency_ms': latency_ms,
                    'trace': trace,
                })}\n\n")

            return

        # =============================================
        # UNKNOWN ROUTE
        # =============================================

        else:

            yield (f"data: {json.dumps({
                    'type': 'error',
                    'message': f'Unknown route: {route}',
                })}\n\n")

            return

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
