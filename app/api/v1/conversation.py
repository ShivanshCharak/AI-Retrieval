from fastapi import (
    APIRouter,
    Request,
    HTTPException,
    Depends,
    UploadFile,
    File,
    Form,
)

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, JSON
from pydantic import BaseModel, Field


from app.db.models import Conversation
from app.db.database import get_db

import jwt

router = APIRouter()
SECRET_KEY = "4WfP4JbL6lLQ5zQZ_8K4YxW5RkM8bM7T9dN2L8xR1cA"


# ============================================================
# Schemas
# ============================================================


class Source(BaseModel):
    label: str
    title: str
    page: str
    source: str


class AddMessage(BaseModel):
    role: str
    content: str
    sources: list[Source] = Field(default_factory=list)


class SyncConversation(BaseModel):
    messages: list[dict]


# ============================================================
# Authentication
# ============================================================


def get_current_user_id(request: Request) -> int:
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    try:
        print("befire payload")

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"],
        )

        print("payload", payload)
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

        return int(user_id)

    except jwt.InvalidTokenError as e:
        print("JWT ERROR:", type(e).__name__)
        print("JWT ERROR DETAIL:", str(e))

        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )


# ============================================================
# Get all conversations
# ============================================================


@router.get("/conversations")
async def all_conversations(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    conversations_result = await db.scalars(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = conversations_result.all()

    return {
        "result": [
            {
                "id": conversation.id,
                "title": conversation.title,
            }
            for conversation in conversations
        ]
    }


# ============================================================
# Get one conversation
# ============================================================


@router.get("/conversation/{conv_id}")
async def get_conversation(
    conv_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    conversation = await db.scalar(
        select(Conversation).where(
            Conversation.id == conv_id,
            Conversation.user_id == user_id,
        )
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return {
        "result": {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "title": conversation.title,
            "messages": conversation.messages,
            "sources": conversation.sources,
            "files": conversation.files,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
        }
    }


# ============================================================
# Create conversation
# ============================================================


@router.post("/conversation")
async def create_conversation(
    message: str = Form(...),
    uploaded_files: list[UploadFile] | None = File(None),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    files = []

    if uploaded_files:
        files = [file.filename for file in uploaded_files if file.filename]

    conversation = Conversation(
        user_id=user_id,
        # First 50 characters become sidebar title
        title=message[:50],
        messages=[
            {
                "role": "user",
                "content": message,
                "sources": [],
            }
        ],
        files=files,
    )

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    return {
        "conversation_id": conversation.id,
        "title": conversation.title,
    }


# ============================================================
# Add message to existing conversation
# ============================================================


@router.post("/conversation/{conv_id}/message")
async def add_message(
    conv_id: int,
    data: AddMessage,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    conversation = await db.scalar(
        select(Conversation).where(
            Conversation.id == conv_id,
            Conversation.user_id == user_id,
        )
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    new_message = {
        "role": data.role,
        "content": data.content,
        "sources": [source.model_dump() for source in data.sources],
    }

    conversation.messages = [
        *conversation.messages,
        new_message,
    ]

    await db.commit()
    await db.refresh(conversation)

    return {
        "success": True,
        "conversation_id": conversation.id,
        "message": new_message,
    }


# ============================================================
# Sync entire conversation
# ============================================================


@router.put("/conversation/{conv_id}/sync")
async def sync_conversation(
    conv_id: int,
    data: SyncConversation,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    conversation = await db.scalar(
        select(Conversation).where(
            Conversation.id == conv_id,
            Conversation.user_id == user_id,
        )
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    conversation.messages = data.messages

    await db.commit()
    await db.refresh(conversation)

    return {
        "success": True,
        "conversation_id": conversation.id,
        "messages": conversation.messages,
    }


# ============================================================
# Create empty conversation
# ============================================================


@router.post("/conversation/new")
async def create_empty_conversation(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    conversation = Conversation(
        user_id=user_id,
        title=None,
        messages=[],
        files=[],
    )

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    return {
        "conversation_id": conversation.id,
        "title": conversation.title,
    }
