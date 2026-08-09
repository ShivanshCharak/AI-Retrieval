import json
from pydantic import BaseModel
from app.services.llm.llm_service import llm
from app.services.retrieval.vector_search import vector_search

import time

from app.services.retrieval.memory_search import memory_search
from app.services.retrieval.github_search import github_search


class RetrievalDecision(BaseModel):
    explanation: str
    use_memory: bool
    use_vector: bool
    use_graph: bool
    use_repo: bool
    use_bm25: bool
    confidence: float


def retrieval_node(state):
    start = time.time()

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
         CONFIDENCE:
            Return a number between 0.0 and 1.0 representing how confident
            you are in the selected route.

    """
    structured_llm = llm.with_structured_output(RetrievalDecision)
    plan = structured_llm.invoke(
        [
            ("system", prompt),
            ("human", state["query"]),
        ]
    )
    state["trace"].append(
        {
            "node": "retrieval router",
            "latency": (time.time() - start) * 1000,
            "confidence": plan.confidence,
            "explaination": plan.explaination,
            "input": state["query"],
            "output": plan,
        }
    )
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
        if plan.use_repo:
            docs.extend(github_search(q, userId=userId))
        # if not plan.use_vector and not plan.use_memory and not plan.use_graph:
        #     docs.extend(intro(q))

        # if plan.use_graph:
        # docs.extend(graph_search(q))
        # docs.extend(bm25_search(q))
    return {**state, "documents": docs}
