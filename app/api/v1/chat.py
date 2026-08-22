from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Request,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.v1.security import get_current_user_id
from app.db.database import get_db
from app.api.v1.ingestion import ingest
from app.graph.graph import graph
from app.graph.state import GraphState
from app.api.v1.sse_utils import sse_event
from app.api.v1.progress_messages import get_progress_message
from app.api.v1.product_route import handle_product_route
from app.api.v1.rag_route import handle_rag_route

router = APIRouter()


@router.post("/chat")
async def query(
    request: Request,
    message: str = Form(...),
    model: str = Form(...),
    web_search: bool = Form(False),
    conversation_id: int = Form(...),
    file: UploadFile | None = File(None),
    deep_search: bool = Form(False),
    db: Session = Depends(get_db),
):
    user_id = get_current_user_id(request)

    if file and file.size > 0:
        await ingest(file, user_id)

    async def generate():
        try:
            final_state = None

            initial_state: GraphState = {
                "query": message,
                "userId": user_id,
                "trace": [],
                "deep_search": deep_search,
                "web_search": web_search,
            }

            async for mode, data in graph.astream(
                initial_state,
                stream_mode=["updates", "values"],
            ):
                if mode == "updates":
                    if not data:
                        continue

                    node = next(iter(data))
                    node_state = data[node]

                    if node == "input_guard" and node_state.get("blocked", False):
                        yield sse_event(
                            "guardrail",
                            blocked=True,
                            message="Request blocked by guardrail",
                        )
                        # Graph is already terminating — don't wait for final_state.
                        return

                    progress = get_progress_message(node)
                    yield sse_event(
                        "progress",
                        stage=node,
                        title=progress["title"],
                        description=progress["description"],
                    )

                elif mode == "values":
                    final_state = data

            if final_state is None:
                yield sse_event("error", message="Graph execution failed")
                return

            route = final_state.get("route")

            if not route:
                yield sse_event("error", message="No route was produced by the graph.")
                return

            if route == "product":
                async for event in handle_product_route(
                    final_state, user_id, message, db
                ):
                    yield event

            elif route == "rag":
                async for event in handle_rag_route(
                    final_state, user_id, message, conversation_id, db
                ):
                    yield event

            else:
                yield sse_event("error", message=f"Unknown route: {route}")

        except Exception as exc:
            print("GRAPH ERROR:", repr(exc))
            yield sse_event(
                "error",
                message="An error occurred while processing the request.",
            )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
