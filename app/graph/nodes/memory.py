from pydantic import BaseModel
from typing import Any
from sqlalchemy.orm import Session
from app.db.models import Memory
import json
from app.services.llm.llm_service import llm

from app.db.qdrant_client_embedder import embedder, client
from qdrant_client.models import PointStruct


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
            points=[
                PointStruct(
                    id=memory.id,
                    vector=vector,
                    payload={"user_id": userId, "text": decision.memory},
                )
            ],
        )

    return memory
