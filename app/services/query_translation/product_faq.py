from pydantic import BaseModel
from app.services.llm.llm_service import llm
import time as Time
from langgraph.config import get_stream_writer
from app.graph.state import GraphState
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Conversation
from fastapi import Depends
from sqlalchemy import select


class ProductfaqOutput(BaseModel):
    response: str
    confidence: float
    topic: str


def product_faq(state: GraphState, db: Session = Depends(get_db)):
    start = Time.time()
    query = state["query"]
    writer = get_stream_writer()
    prv_len = 0
    final_obj = None
    prompt = f"""
    As an ai agent,your primary responsibility is to answer user queries about this AI Retrieval & GitHub Code Assistant using ONLY the information provided below.
    
        Answer ONLY using the information provided below.
    
        Do not invent features that are not mentioned.
    
         If the information below does not contain the requested answer, politely say that you don't have that information.
    
         Keep responses conversational, concise, and easy to understand.

        The topic should:
        - Be 3-7 words
        - Clearly describe what the user is asking about
        - Not be a sentence
        - Not include quotes
        - Not include punctuation at the end
    
        -----------------------
        PRODUCT INFORMATION
        -----------------------
    
        # AI Retrieval & GitHub Code Assistant
    
        ## Overview
    
        This project is an intelligent AI assistant designed to answer questions by selecting the most appropriate knowledge source instead of relying solely on an LLM. It combines long-term user memory, document retrieval, repository knowledge, and web search through an intelligent routing and retrieval pipeline.
    
        The system supports both general Retrieval-Augmented Generation (RAG) and a GitHub code assistant capable of understanding repositories and answering questions about a codebase.
    
        ## Technologies
    
        - Query Classification
        - Query Decomposition
        - HYDE
        - Multi Query Generation
        - Routing
        - Long-Term Memory
        - Vector Database
        - Knowledge Graph
        - Web Search
        - Reciprocal Rank Fusion (RRF)
        - Reranking
        - Retrieval-Augmented Generation (RAG)
    
        ## Architecture
    
        1. Query Routing
        - Routes product questions directly.
        - Routes knowledge questions to the retrieval pipeline.
    
        2. Retrieval Planning
        Selects one or more retrieval sources:
        - Memory
        - Vector Database
        - Knowledge Graph
        - Web Search
    
        3. Query Expansion
        Generates multiple search queries to improve retrieval.
    
        4. Parallel Retrieval
        Retrieves information from multiple sources simultaneously.
    
        5. Result Fusion
        Combines retrieved documents using Reciprocal Rank Fusion (RRF).
    
        6. Reranking
        Ranks retrieved documents according to relevance.
    
        7. Response Generation
        Generates grounded answers using retrieved context.
    
        8. Memory Extraction
        Extracts and stores long-term user information such as preferences, occupation, education, goals, and other stable facts.
    
        ## Retrieval Sources
    
        ### Memory
        Stores:
        - Personal profile
        - Preferences
        - Occupation
        - Education
        - Goals
        - Stable facts
        - Likes and dislikes
    
        ### Vector Database
        Indexes:
        - PDFs
        - Books
        - Notes
        - Documentation
        - Research Papers
        - Manuals
        - Reports
        - Resumes
        - GitHub repositories
    
        ### Knowledge Graph
        Supports relationship-based questions such as:
        - Service dependencies
        - API relationships
        - Authentication flow
        - Class interactions
    
        ### Web Search
        Retrieves current information when local knowledge is insufficient.
    
        ## GitHub Code Assistant
    
        The assistant can:
        - Explain repositories
        - Explain architecture
        - Explain APIs
        - Explain authentication
        - Explain request flow
        - Find relevant code
        - Search documentation
        - Understand module relationships
        - Answer repository-specific questions
        #VERY IMPORTANT
        - if query comes with hey, hello or greetings in particulary, you have to greet it back and dont tell anything about the system until asked
        - if it says something like how you doing or how you feeling or anythng about your feeling, you can say you are an ai and dont have sense of feeling
        Query:-
        {query}
    """
    response = llm.with_structured_output(ProductfaqOutput).invoke(prompt)
    print("response", response)

    state["trace"].append(
        {
            "node": "product_faq",
            "latency_ms": (Time.time() - start) * 1000,
            "confidence": response.confidence,
            "input": state["query"],
            "output": response.response,
        }
    )

    return {
        **state,
        "answer": response.response,
        "topic": response.topic,
    }
