from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen3:1.7b", temperature=0)
llm_phi = ChatOllama(
    model="phi",
)
