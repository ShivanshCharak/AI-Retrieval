# import json

# import jwt
# from fastapi import (
#     APIRouter,
#     Depends,
#     File,
#     Form,
#     HTTPException,
#     Request,
#     UploadFile,
# )
# from fastapi.responses import StreamingResponse
# from sqlalchemy.orm import Session
# from sqlalchemy import select
# from app.db.models import Conversation
# from app.api.v1.ingestion import ingest
# from app.guardrails.output_validation import validate_output
# from app.db.database import get_db
# from app.graph.graph import graph
# from app.graph.nodes.memory import save_memory
# from app.graph.state import GraphState
# from app.services.llm.llm_service import llm
# from pydantic import BaseModel

# router = APIRouter()


# class AnswerWithTitle(BaseModel):
#     answer: str
#     topic: str


# SECRET_KEY = "4WfP4JbL6lLQ5zQZ_8K4YxW5RkM8bM7T9dN2L8xR1cA"


# PROGRESS_MESSAGES = {
#     "input_guard": {
#         "title": "Checking your request",
#         "description": "Validating the request before processing.",
#     },
#     "router": {
#         "title": "Understanding your question",
#         "description": "Determining the best way to answer.",
#     },
#     "query_generation": {
#         "title": "Generating search queries",
#         "description": "Creating optimized search terms.",
#     },
#     "retrieval": {
#         "title": "Searching documents",
#         "description": "Looking through your uploaded files and knowledge.",
#     },
#     "fusion": {
#         "title": "Combining search results",
#         "description": "Merging results from multiple searches.",
#     },
#     "rerank": {
#         "title": "Ranking results",
#         "description": "Keeping only the most relevant information.",
#     },
#     "product_faq": {
#         "title": "Preparing response",
#         "description": "Generating a response from the product knowledge.",
#     },
#     "output_guard": {
#         "title": "Checking response",
#         "description": "Validating the generated response.",
#     },
# }


# @router.post("/chat")
# async def query(
#     request: Request,
#     message: str = Form(...),
#     model: str = Form(...),
#     web_search: bool = Form(False),
#     conversation_id: int = Form(...),
#     file: UploadFile | None = File(None),
#     deep_search: bool = Form(False),
#     db: Session = Depends(get_db),
# ):
#     token = request.cookies.get("access_token")
#     print(conversation_id)

#     if not token:
#         raise HTTPException(
#             status_code=401,
#             detail="Not authenticated",
#         )

#     payload = jwt.decode(
#         token,
#         SECRET_KEY,
#         algorithms=["HS256"],
#     )

#     user_id = payload["user_id"]

#     if file and file.size > 0:
#         await ingest(file, user_id)

#     async def generate():

#         try:
#             final_state = None

#             initial_state: GraphState = {
#                 "query": message,
#                 "userId": user_id,
#                 "trace": [],
#                 "deep_search": deep_search,
#                 "web_search": web_search,
#             }

#             async for mode, data in graph.astream(
#                 initial_state,
#                 stream_mode=["updates", "values"],
#             ):

#                 # =========================================
#                 # NODE UPDATES
#                 # =========================================

#                 if mode == "updates":

#                     if not data:
#                         continue

#                     node = next(iter(data))
#                     node_state = data[node]

#                     print("NODE UPDATE:", node, node_state)

#                     # =====================================
#                     # INPUT GUARD
#                     # =====================================

#                     if node == "input_guard":

#                         if node_state.get("blocked", False):

#                             print("🚫 INPUT BLOCKED")
#                             print(
#                                 "REASON:",
#                                 node_state.get("block_reason"),
#                             )

#                             yield (f"data: {json.dumps({
#                                     'type': 'guardrail',
#                                     'blocked': True,
#                                     'message': 'Request blocked by guardrail',
#                                 })}\n\n")

#                             # IMPORTANT:
#                             # Do not wait for final_state.
#                             # The graph is already terminating.
#                             return

#                     # =====================================
#                     # NORMAL PROGRESS
#                     # =====================================

#                     progress = PROGRESS_MESSAGES.get(
#                         node,
#                         {
#                             "title": node.replace("_", " ").title(),
#                             "description": "",
#                         },
#                     )

#                     yield (f"data: {json.dumps({
#                             'type': 'progress',
#                             'stage': node,
#                             'title': progress['title'],
#                             'description': progress['description'],
#                         })}\n\n")

#                 # =========================================
#                 # COMPLETE GRAPH STATE
#                 # =========================================

#                 elif mode == "values":

#                     final_state = data

#             # =============================================
#             # NO FINAL STATE
#             # =============================================

#             if final_state is None:

#                 yield (f"data: {json.dumps({
#                         'type': 'error',
#                         'message': 'Graph execution failed',
#                     })}\n\n")

#                 return

#             print("FINAL STATE:", final_state)

#             # =============================================
#             # ROUTE
#             # =============================================

#             route = final_state.get("route")

#             if not route:

#                 yield (f"data: {json.dumps({
#                         'type': 'error',
#                         'message': 'No route was produced by the graph.',
#                     })}\n\n")

#                 return

#             # =============================================
#             # PRODUCT ROUTE
#             # =============================================

#             if route == "product":

#                 print("PRODUCT ROUTE")

#                 answer = final_state.get("answer", "")
#                 topic = final_state.get("topic", "")

#                 if answer:

#                     yield (f"data: {json.dumps({
#                             'type': 'token',
#                             "title": topic,
#                             'content': answer,
#                         })}\n\n")

#                 yield (f"data: {json.dumps({
#                         'type': 'complete',
#                         "title": topic,
#                         'trace': final_state.get("trace", []),
#                     })}\n\n")

#                 save_memory(
#                     userId=user_id,
#                     message=message,
#                     db=db,
#                 )

#                 return

#             elif route == "rag":

#                 print("RAG ROUTE")

#                 docs = final_state.get(
#                     "reranked_docs",
#                     [],
#                 )

#                 context = "\n\n".join(
#                     (
#                         doc.page_content
#                         if hasattr(doc, "page_content")
#                         else str(doc.get("content", ""))
#                     )
#                     for doc in docs
#                 )

#                 prompt = f"""

#             Use all relevant information present in the context.

#             You are answering a user's question using retrieved knowledge-base context.

#             Instructions:

#             1. Answer the user's question directly.
#             2. Do not summarize the retrieved documents unless the user explicitly asks for a summary.
#             3. Use the retrieved context as supporting evidence, not as the task itself.
#             4. If the question is broad, give the user a useful conceptual overview.
#             5. Organize the answer around the user's topic, not around the order of retrieved chunks.
#             6. Do not mention "the provided text", "the retrieved documents", or "the context".
#             7. If the retrieved context does not contain enough information, say so rather than inventing details.
#             Secondly this
#             Generate a short conversation topic for the user's question.

#             The topic should:
#             - Be 3-7 words
#             - Clearly describe what the user is asking about
#             - Not be a sentence
#             - Not include quotes
#             - Not include punctuation at the end
#              User question:
#             {message}

#             Retrieved context:
#             {context}
#             """

#                 # =========================================
#                 # GENERATE COMPLETE ANSWER
#                 # =========================================

#                 print("GENERATING ANSWER...")
#                 structured_llm = llm.with_structured_output(AnswerWithTitle)
#                 response = await structured_llm.ainvoke(prompt)
#                 conversation = db.scalar(
#                     select(Conversation).where(
#                         Conversation.id == conversation_id,
#                         Conversation.user_id == user_id,
#                     )
#                 )

#                 conversation.title = response.topic
#                 db.commit()
#                 if not conversation:
#                     yield f"data: {json.dumps({
#                         'type': 'error',
#                         'message': 'Conversation not found',
#                     })}\n\n"
#                     return
#                 full_answer = response.answer
#                 title = response.topic
#                 title = response.topic

#                 print("GENERATED ANSWER:")
#                 print(full_answer)

#                 print("GENERATED TITLE:")
#                 print(title)

#                 # =========================================
#                 # OUTPUT GUARD
#                 # =========================================

#                 print("RUNNING OUTPUT GUARD...")

#                 guard_result = validate_output(full_answer)

#                 if not guard_result["is_safe"]:

#                     print("🚫 OUTPUT BLOCKED")
#                     print("REASON:", guard_result["raw"])

#                     yield (f"data: {json.dumps({
#                             'type': 'guardrail',
#                             'blocked': True,
#                             'message': 'Response blocked by guardrail',
#                         })}\n\n")

#                     return

#                 print("✅ OUTPUT SAFE")

#                 # =========================================
#                 # STREAM SAFE ANSWER
#                 # =========================================

#                 # At this point the complete answer has already
#                 # passed the output guard.

#                 # We can now send it to the client in chunks.

#                 chunk_size = 20

#                 for i in range(0, len(full_answer), chunk_size):

#                     token = full_answer[i : i + chunk_size]

#                     yield (f"data: {json.dumps({
#                             'type': 'token',
#                             'content': token,
#                         })}\n\n")

#                 # =========================================
#                 # SAVE MEMORY
#                 # =========================================

#                 save_memory(
#                     userId=user_id,
#                     message=message,
#                     db=db,
#                 )

#                 # =========================================
#                 # TRACE
#                 # =========================================

#                 trace = final_state.get(
#                     "trace",
#                     [],
#                 )

#                 confidence = None
#                 latency_ms = None

#                 if trace:

#                     confidence = trace[-1].get("confidence")

#                     latency_ms = trace[-1].get("latency_ms")

#                 # =========================================
#                 # COMPLETE
#                 # =========================================

#                 yield (f"data: {json.dumps({
#                         'type': 'complete',
#                         'confidence': confidence,
#                         'title': title,
#                         'latency_ms': latency_ms,
#                         'trace': trace,
#                         'output_guard': {
#                             'is_safe': True,
#                         },
#                     }, default=str)}\n\n")

#                 return

#             # =============================================
#             # UNKNOWN ROUTE
#             # =============================================

#             else:

#                 yield (f"data: {json.dumps({
#                         'type': 'error',
#                         'message': f'Unknown route: {route}',
#                     })}\n\n")

#                 return
#         except Exception as exc:

#             print("GRAPH ERROR:", repr(exc))

#             yield (f"data: {json.dumps({
#                             'type': 'error',
#                             'message': 'An error occurred while processing the request.',
#                         })}\n\n")

#             return

#     return StreamingResponse(
#         generate(),
#         media_type="text/event-stream",
#         headers={
#             "Cache-Control": "no-cache",
#             "Connection": "keep-alive",
#             "X-Accel-Buffering": "no",
#         },
#     )
