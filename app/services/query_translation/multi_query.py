from pydantic import BaseModel, Field
from app.graph.state import GraphState
from app.services.llm.llm_service import llm
from langchain_core.prompts import ChatPromptTemplate


class MultiQueryOutput(BaseModel):
    queries: list[str] = Field(
        description="List of alternative query formulations and closely related concepts."
    )


def generate_multi_queries(query: str, metadata: str = "") -> list[str]:
    structured_llm = llm.with_structured_output(MultiQueryOutput)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an expert AI search refinement agent. Your task is to analyze a user's input query ( and break it down into exactly 5 distinct variations.

Follow these strict structural constraints:
- Do not expand abbreviations (e.g., LLM, API, RAG) if the precise architectural context is omitted.
- Keep every generated variation highly concise and direct.
- Alternative Phrasing: Generate variations that preserve the core engineering intent while using different technical vocabulary or syntax.
- Neighboring Concepts: Include variations targeting concepts immediately adjacent or critical to the user's topic.
- Ensure every generated query revolves around the provided metadata.
- Do not leave any generated query empty.

Collection Context:
{metadata}

Output exactly 5 variations total.
                """,
            ),
            (
                "human",
                "Original Query: {query}",
            ),
        ]
    )

    query_generation_chain = prompt_template | structured_llm

    response = query_generation_chain.invoke(
        {
            "query": query,
            "metadata": metadata,
        }
    )

    print(f"Generated Queries: {response.queries}")
    return response.queries
