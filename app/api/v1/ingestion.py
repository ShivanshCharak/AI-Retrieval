# api/v1/ingestion.py

from fastapi import APIRouter, File
from pydantic import BaseModel
from pathlib import Path
import aiofiles

from app.services.ingestion.ingestion_service import ingest_document

router = APIRouter()


class IngestionRequest(BaseModel):
    file_path: str


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def ingest(file: File, userId: str):
    """Asynchronously ingest a file and store in vector database."""
    file_path = UPLOAD_DIR / file.filename

    # Async file write using aiofiles
    contents = await file.read()
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)

    # Call async ingest_document function
    result = await ingest_document(file_path, userId)

    return result
