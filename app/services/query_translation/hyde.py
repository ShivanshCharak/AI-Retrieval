from pydantic import BaseModel
from app.services.llm.llm_service import llm

class HyDEOutput(BaseModel):
    hypothetical_answer: str

def generate_hyde(query: str):
    structured_output = llm.with_structured_output(
        HyDEOutput
    )
    prompt = f"""
        You are an expert technical documentation generator. 
        Your task is to write a comprehensive, authoritative, and detailed hypothetical response to the user's inquiry.

        This response will be used strictly for semantic vector retrieval. Follow these guidelines:
        1. Direct Style: Write the answer immediately as if it were a direct excerpt from a high-quality README, official API documentation, textbook, or codebase comment.
        2. Formats & Syntax: If the query is about programming or systems architecture, include realistic code snippets, configuration blocks, or explicit terminal commands.
        3. No Meta-Language: Do not include introductory or concluding remarks like "Here is the answer," "Based on your query," or "Hypothetically speaking."
        4. Technical Depth: Use exact terminology, parameter names, and technical concepts appropriate for a senior software engineer.

        Return ONLY the raw document text.
            ("human", "Query: {query}")
    """
    response  = structured_output.invoke(
        prompt
    )
    return response.hypothetical_answer