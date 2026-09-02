import json
from pathlib import Path
import aiofiles


async def store_collection_metadata(metadata, userId):
    """Asynchronously store collection metadata to JSON file."""
    METADATA_DIR = Path(__file__).parent
    METADATA_DIR.mkdir(exist_ok=True)

    file_path = METADATA_DIR / f"metadata/collection_metadata_{userId}.json"

    async with aiofiles.open(file_path, "w") as f:
        await f.write(json.dumps(metadata.model_dump(), indent=2))


async def get_collection_metadata():
    """Asynchronously retrieve collection metadata from JSON file."""
    METADATA_DIR = Path(__file__).parent
    file_path = METADATA_DIR / f"metadata/collection_metadata_{4}.json"

    async with aiofiles.open(file_path, "r") as f:
        content = await f.read()
        return json.loads(content)
