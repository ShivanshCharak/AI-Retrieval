from langchain_ollama import ChatOllama
from ragas.llms import llm_factory

ragas_llm = llm_factory(
    ChatOllama(
        model="qwen3:1.7b",
        temperature=0,
    )
)
