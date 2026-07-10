# api/v1/ingestion.py

from fastapi import APIRouter, File
from pydantic import BaseModel
from pathlib import Path

from app.services.ingestion.ingestion_service import ingest_document

router = APIRouter()


class IngestionRequest(BaseModel):
    file_path: str


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def ingest(file: File, userId: str):
    file_path = UPLOAD_DIR / file.filename
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    result = ingest_document(file_path, userId)

    return result
