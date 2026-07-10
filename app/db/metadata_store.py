import json
from pathlib import Path


def store_collection_metadata(metadata, userId):
    METADATA_DIR = Path(__file__).parent
    METADATA_DIR.mkdir(exist_ok=True)
    with open(METADATA_DIR / f"metadata/collection_metadata_{userId}.json", "w") as f:
        json.dump(metadata.model_dump(), f, indent=2)


def get_collection_metadata():

    with open("collection_metadata.json", "r") as f:
        return json.load(f)
