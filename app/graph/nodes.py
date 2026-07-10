from app.services.query_translation.translation_service import generate_queries
from sqlalchemy.orm import Session
from typing import Any
from fastapi import Depends
from app.db.qdrant_client_embedder import embedder, client
from qdrant_client.models import PointStruct

import json
from app.services.retrieval.vector_search import vector_search

# from app.services.retrieval.graph_search import graph_search
# from app.services.retrieval.bm25_search import bm25_search
from app.services.retrieval.memory_search import memory_search
from app.services.retrieval.github_search import github_search
from app.db.models import Memory
from typing import Literal
from app.services.intro import intro
from app.db.database import get_db
from pathlib import Path


from app.services.fusion.rrf import reciprocal_rank_fusion
from pydantic import BaseModel, Field
from app.services.reranking.rerank import rerank_documents

from app.services.llm.llm_service import llm


def generated_queries(state):
    return {"generated_queries": generate_queries(state["query"])}


class RetrievalDecision(BaseModel):
    use_memory: bool
    use_vector: bool
    use_graph: bool
    use_repo: bool
    use_bm25: bool


def retrieval_node(state):

    metadata = ""
    userId = state["userId"]
    with open(f"app/db/metadata/collection_metadata_{userId}.json", "r") as f:
        metadata = json.load(f)

    prompt = f"""
    You are a retrieval planner.

Your task is to decide which retrieval sources should be used to answer the user's question.

Available retrieval sources:

1. MEMORY
If answering the user's question requires recalling previously stored
information about the user, ALWAYS set use_memory=True.
This things include, but not limited to this
- About user
- what do i like
- about user interests
- about user likes and dislikes
- where he is from
- origin
- background
- occupation
- age
-sex

- Who am I?
- Tell me about myself.
- Describe me.
- What do you know about me?
- Summarize my profile.
- Summarize my qualifications.
- Summarize my experience.
- Generate a bio about me.
- Write an introduction about me.
- I am applying somewhere. Can you summarize what I do?

If the user is asking to generate thngs which need thier info then also you have to set use_memory=True
If the user's message is introducing themselves, sharing new personal information, or chatting casually without asking a question, do NOT retrieve anything.

Examples:
- Hi, I'm Shivansh.
- I am a software engineer.
- I like football.
- My favorite language is Go.
- I live in Pune.

Return:

{{
  "use_memory": False,
  "use_vector": False,
  "use_graph": False,
   "use_repo": False
}}

The assistant should simply respond naturally and the new information will be extracted and stored by the memory extraction step after the response.

VECTOR DATABASE

The user has uploaded documents with the following metadata:

{metadata}

Set use_vector = True if the user's question could be answered using information from any uploaded document, regardless of its type.

This includes:
- books
- notes
- resumes
- PDFs
- documentation
- research papers
- manuals
- reports
- or any topic mentioned in the metadata.

If the question is unrelated to the uploaded documents or metadata, set use_vector = False.

3. KNOWLEDGE GRAPH
Use GRAPH when answering requires understanding relationships between entities, dependencies, or connected concepts from the uploaded documents and the metadata about those document is present in {metadata} if it is not related to these topics then keep use_graph=False.

Examples:
"Which services depend on Redis?"
"Show relationships between classes."
"How are these APIs connected?"

Rules:
- More than one retrieval source may be required.
- If unsure, enable VECTOR.
- Only enable MEMORY if personal information is required.
- Only enable GRAPH if relationships are important.

Return only JSON.
More than one retrieval source may be required.
one query can have use_vector to true and use_memory to true or all three as true if required
Example:

{{
    "use_memory": True,
    "use_vector": False,
    "use_graph": False
    "use_repo": False
}}
4. Repository
 Use repository whent he user is asking about the source code
 Example:
 Explain this function
 Where is auth implemented
 which file contain RBAC
 Show me where redis is used
 How this code take care of streaming data
 How jwt validated
 which endpoint calls this function
 Set use_repo=True


    """
    structured_llm = llm.with_structured_output(RetrievalDecision)
    plan = structured_llm.invoke(
        [
            ("system", prompt),
            ("human", state["query"]),
        ]
    )
    print("planed", plan)
    docs = []
    queries = state.get("generated_queries")
    if not queries:
        queries = [state["query"]]
    for q in queries:
        userId = state["userId"]
        if plan.use_memory:
            docs.extend(memory_search(q, userId))
            # print("going to use memeory")
        if plan.use_vector:
            docs.extend(vector_search(q, userId=userId))
        # if plan.use_repo:
        #     docs.extend(github_search(q, userId=userId))
        if not plan.use_vector and not plan.use_memory and not plan.use_graph:
            docs.extend(intro(q))

        # if plan.use_graph:
        # docs.extend(graph_search(q))
        # docs.extend(bm25_search(q))
    return {"documents": docs}


def fusion_node(state):
    return {"documents": reciprocal_rank_fusion(state["documents"])}


def rerank_nodes(state):
    return {"reranked_docs": rerank_documents(state["query"], state["documents"])}


class RouteDecision(BaseModel):
    route: Literal["rag", "product"]


def graph_router_node(state):
    structured_llm = llm.with_structured_output(RouteDecision)

    decision = structured_llm.invoke(
        [
            (
                "system",
                """
            You are a routing agent.

            Your job is to classify the user's query into exactly one category.

            Return ONLY one of:
            - rag
            - product


            PRODUCT:
            Use product ONLY when the user is asking about this Ai Assisytant which is the github code assistant:
            if it is a link assign it as rag right away not product
            this includes
            - if user is asking abiut you always return product
            - greeting if it is standalone
            - asking who you are
            - asking what you do
            - asking about its architecture
            - asking about its working
            - asking about what it needs to start working
            - asking about this product

            Examples:
            "hi" -> product
            "hello" -> product
            "how do you work?" -> product
            "what can you do?" -> product
            "explain your architecture" -> product
            "what you can do" -> Product
            "how do you work" -> Product
            "how are you" -> Product
            "how capable are you" -> Product

            RAG:
            Use rag when user is asking questions where you need a context i.r you need to do vector search memory search or graph search or user is asking about himself:
            - if user is asking about themselves always return rag
            - programming questions
            - technical questions
            - AI/ML questions
            - coding questions
            - framework questions
            - repository questions
            - document questions
            - PDF questions
            - uploaded file questions
            - general knowledge questions
            HIGHEST PRIORITY RULE:

            If the user is asking about themselves, their preferences, memories,
            history, possessions, profile, likes, dislikes, goals, or anything that
            requires retrieving personal information, ALWAYS return "rag".

            Examples:
            "What do I like?" -> rag
            "What food do I like?" -> rag
            "What is my favorite color?" -> rag
            "What car do I own?" -> rag
            "What have I told you about myself?" -> rag
            "What do you remember about me?" -> rag

            Examples:
            "what is llm?" -> rag
            "what is fastapi?" -> rag
            "what is a database?" -> rag
            "explain transformers" -> rag
            "what is langgraph?" -> rag
            "how does redis work?" -> rag
            "who am i" -> Rag
            "tell me about myself" -> Rag

            If unsure, ALWAYS return rag
            Important rules
            - Do not classify as product only if the query contains the word "you"
            - "You refers to the product only if user asking about assistant itself"

            Example:
            "Can you explain FastAPI?" -> rag
            "Can you help me debug this?" -> rag
            "Can you summarize my PDF?" -> rag

            3. Standalone greetings are product.
            If a greeting is followed by another question, classify using the main question.

            Example:
            "Hi" -> product
            "Hello" -> product
            "Hi, explain FastAPI." -> rag
            """,
            ),
            ("human", state["query"]),
        ]
    )

    print("QUERY:", state["query"])
    print("ROUTE:", decision.route)

    return {"route": decision.route}


def simple_answers(state):
    print("simple answer")
    return {"answer": intro(state["query"])}


class MemoryDecision(BaseModel):
    store: bool
    memory: dict[str, Any]


def save_memory(userId: int, message: str, db: Session):
    print("into save memory")
    memory_prompt = f"""
    You are a memory extraction agent.
    always in the emssage "I" is user who is writing and "you" is the code assistant or product
    Determine whether the user's latest message contains information worth storing as long-term memory.

    Store only:
    - Personal preferences
    - Personal profile
    - Long-term goals
    - Stable facts
    - Likes/dislikes
    - Occupation
    - Education
    - Important personal information

    Do NOT store:
    - Questions
    - Greetings
    - Temporary requests
    - General knowledge requests
    - One-time conversations

    User message:
    {message}

    Return JSON only.
    the memory object should reuturn the object, in the format 
    for example if the memory is about the user loving vegetable or owning a mercedes
    it should be{ {
        "loves":"vegetable",
        "owns": "mercedes"
    }
}
   {{
        "store": True,
        "memory": {{}}
    }}

If the message contains NO new long-term information:

{{
  "store": False,
  "memory": {{}}
}}

    """
    print("Before structured output")

    structured = llm.with_structured_output(MemoryDecision)

    print("Structured object created")

    decision = structured.invoke(memory_prompt)

    print("Decision received")
    memory = ""
    print("saving", decision)

    if decision.store:
        memory = Memory(user_id=userId, text=decision.memory)
        db.add(memory)
        db.commit()
        db.refresh(memory)
        memory_text = json.dumps(decision.memory, sort_keys=True)
        vector = embedder.embed_query(memory_text)
        client.upsert(
            collection_name="documents",
            points=[PointStruct(id=memory.id, vector=vector, payload={"user_id": userId, "text": decision.memory})],
        )

    return memory
