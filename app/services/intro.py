# from pydantic import BaseModel, Field
# from app.services.llm.llm_service import llm
# from langchain_core.prompts import ChatPromptTemplate
# from app.graph.state import GraphState
# import time as Time


# class MessageOutput(BaseModel):
#     message: str = Field(description="string response to the query")
#     confidence: float = Field(description="Confidence")


# def intro(state: GraphState):
#     start = Time.time()
#     structured_llm = llm.with_structured_output(MessageOutput)

#     prompt = ChatPromptTemplate.from_template("""
#     You are an AI assistant.

#     Your primary responsibility is to answer user queries about this AI Retrieval & GitHub Code Assistant using ONLY the information provided below.

#     ## Behaviour

#     1. If the user greets you or starts a casual conversation, respond naturally and warmly.

#     Examples:
#     - User: "Hi"
#     Assistant: "Hi! How can I help you today?"

#     - User: "Hey, I'm Shivansh."
#     Assistant: "Hey Shivansh! Nice to meet you. I'm an AI Retrieval & GitHub Code Assistant. I can help answer questions about your uploaded documents, PDFs, GitHub repositories, and remember useful information across conversations. How can I help you today?"

#     - User: "I had a really bad day."
#     Respond with empathy and continue the conversation naturally instead of giving a robotic response.

#     User Query:
#     {query}
#     """)
#     response = structured_llm.invoke(MessageOutput)
#     state["trace"].append(
#         {
#             "node": "intro",
#             "latency_ms": (Time.time() - start) * 1000,
#             "input": state["query"],
#             "output": response.response,
#             "confidence": response.confidence,
#         }
#     )

#     print(f"Generated Response: {response.content}")
#     return {**state, "answer": response.content, "confidence": response.confidence}
