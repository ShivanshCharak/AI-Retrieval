import json
from fastapi import APIRouter, Depends, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import jwt
import json

from app.api.v1.ingestion import ingest
from app.db.database import get_db
from app.graph.graph import graph
from app.graph.nodes import save_memory
from app.services.llm.llm_service import llm

router = APIRouter()

SECRET_KEY = "4WfP4JbL6lLQ5zQZ_8K4YxW5RkM8bM7T9dN2L8xR1cA"

PROGRESS_MESSAGES = {
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
    "simple_answers": {
        "title": "Preparing response",
        "description": "Generating a direct answer.",
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
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload["user_id"]

    if file and file.size > 0:
        await ingest(file, user_id)

    async def generate():
        final_state = None
        print("message", message)
        async for mode, data in graph.astream(
            {
                "query": message,
                "userId": user_id,
                "trace": [],
                "deep_search": deep_search,
            },
            stream_mode=["updates", "values"],
        ):
            if mode == "updates":
                node = list(data.keys())[0]

                progress = PROGRESS_MESSAGES.get(
                    node,
                    {"title": node.replace("_", " ").title(), "description": ""},
                )

                yield (f"data: {json.dumps({
                        'type': 'progress',
                        'stage': node,
                        'title': progress['title'],
                        'description': progress['description']
                    })}\n\n")

            elif mode == "values":
                final_state = data

        if final_state is None:
            yield f"data: {json.dumps({'type':'error','message':'Graph execution failed'})}\n\n"
            return

        # Product route
        if final_state["route"] == "product":
            yield f"data: {json.dumps({'type':'token','content': final_state['answer']})}\n\n"
            yield f"data: {json.dumps({'type':'complete'})}\n\n"
            save_memory(
                userId=user_id,
                message=message,
                db=db,
            )

            return

        # RAG route
        docs = final_state.get("reranked_docs", [])
        print("doc", docs)

        context = "\n\n".join(
            (
                json.dumps(doc["content"])
                if isinstance(doc["content"], dict)
                else str(doc["content"])
            )
            for doc in docs
        )
        print("context", context)

        prompt = f"""
        You are a Answer generator you have to answer the user on the basis of context provided
        Answer the question using ONLY the provided context.
        the words "I", "me", and "my" always refer to the USER, not you.

        If the context does not contain the answer, say you don't know.
        if the context say "User" change it to "you" but that doesnt mean if user asks "who am i" you reply with "i is you" thats wrong reply you simple say you dont have enoug context
        If user ask you about something which you dont have the context of you should simply say i dont know or provided context have no info about you


        Question:
        {message}

        Context:
        {context}
        """

        for chunk in llm.stream(prompt):
            if chunk.content:
                yield f"data: {json.dumps({'type':'token','content': chunk.content})}\n\n"

        save_memory(
            userId=user_id,
            message=message,
            db=db,
        )

        yield f"data: {json.dumps({'type':'complete'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )
