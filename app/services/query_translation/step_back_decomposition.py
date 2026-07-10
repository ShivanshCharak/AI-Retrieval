from app.services.llm.llm_service import llm
from pydantic import BaseModel
class DecompositionOutput(BaseModel):
    sub_questions: list[str]

def decompose_query(query: str):
    structured_llm = llm.with_structured_output(
        DecompositionOutput
    )
    prompt = """You are an expert developer assistant. Your task is to take a highly specific, technical user query and generate a broader, more abstract "step-back" question.

            This step-back question should target the foundational concepts, underlying architecture, or core programming principles behind the user's specific problem.

            Rules:
            1. Abstract the Specifics: Remove concrete values like specific variable names, file paths, or unique error hex codes.
            2. Identify the Core Framework/Protocol: Focus on the high-level system behaviors, lifecycles, or design patterns involved.
            3. Keep it Concise: The output must be a single, direct conceptual question.
            4. No Meta-Language: Return ONLY the raw question text. Do not include introductory phrases.
                ("human", "Original Query: {query}")"""
    response  = structured_llm.invoke(prompt)
    return response.sub_questions
