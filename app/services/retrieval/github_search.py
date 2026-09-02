import re

import os
import json
import hashlib

from pathlib import Path
from app.services.ingestion.github_loader import clone_repo
from app.services.ingestion.ast_parser import parse_python_file
from app.services.ingestion.metadata_extraction import generate_collection_metadata
from app.services.ingestion.ingestion_helper.chunker import split_documents
from app.services.retrieval_service import retrieve_context
from app.services.retrieval.vector_search import vector_store
from app.services.ingestion.metadata_extraction import build_repo_scope_metadata
from app.graph.state import GraphState
from app.services.ingestion.symbol_extractor import (
    extract_calls,
    extract_symbols,
    extract_imports,
    extract_constants,
    extract_global_variables,
)
from qdrant_client.models import Filter, FieldCondition, MatchValue

# from app.graph.graph import GraphState
from langchain_core.documents import Document


def repo_already_indexed(user_id: str, repo_url: str) -> bool:
    result = vector_store.client.scroll(
        collection_name="documents",
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="metadata.user_id",
                    match=MatchValue(value=user_id),
                ),
                FieldCondition(
                    key="metadata.repo_url",
                    match=MatchValue(value=repo_url),
                ),
            ]
        ),
        limit=1,
        with_payload=False,
        with_vectors=False,
    )

    points, _ = result

    return len(points) > 0


def github_embedder(url: str, userId: str):

    if repo_already_indexed(userId, url):
        print("Repository already indexed. Skipping embedding.")
        return
    repo_path = clone_repo(url)

    repo = []
    documents = []
    for root, _, files in os.walk(repo_path):
        for file in files:

            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)

            # # Stable path inside repository
            relative_file_path = os.path.relpath(file_path, repo_path)

            parsed = parse_python_file(file_path)

            if not parsed["success"]:
                continue

            source = parsed["source"]
            tree = parsed["tree"]

            symbols = extract_symbols(tree, source)
            # # print("symbols", symbols)
            structure = {
                "file": relative_file_path,
                "symbols": symbols,
                "id": relative_file_path,
                "calls": extract_calls(tree),
                "imports": extract_imports(tree),
                "constants": extract_constants(tree),
                "global_variables": extract_global_variables(tree),
            }
            repo.append(structure)

            for symbol in symbols:
                relative_file = str(Path(file_path).relative_to(repo_path))

                code_text = f"""
            File: {relative_file}
            Symbol: {symbol["name"]}
            Type: {symbol["type"]}

            # Decorators:
            {", ".join(symbol.get("decorators", []))}

            # Calls:
            {", ".join(symbol.get("calls", []))}

            # Docstring:
            {symbol.get("docstring") or ""}

            # Source:
            {symbol["source"]}
            """

                documents.append(
                    Document(
                        page_content=code_text,
                        metadata={
                            "user_id": int(userId),
                            "repo_url": url,
                            "file": relative_file,
                            "name": symbol["name"],
                            "type": symbol["type"],
                            "line": symbol["line"],
                            "end_line": symbol["end_line"],
                            "args": symbol.get("args"),
                            "docstring": symbol.get("docstring"),
                            "calls": symbol.get("calls", []),
                            "decorators": symbol.get("decorators", []),
                        },
                    )
                )
    scope_metadata = build_repo_scope_metadata(repo)
    save_repo_scope_metadata(userId, url, scope_metadata)

    chunks = split_documents(documents)

    for chunk in chunks:
        chunk.metadata["user_id"] = userId

    vector_store.add_documents(chunks)
    return repo


async def github_parser(state: GraphState):
    text = state["query"]

    match = re.search(r"https?://github\.com/\S+", text)

    url = None
    query = text

    if match:
        url = match.group(0).rstrip(".,)")
        query = (text[: match.start()] + text[match.end() :]).strip()

        print("query:", query)
        print("repo_url:", url)

        github_embedder(url, state["userId"])

    documents = await retrieve_context(
        query=query,
        user_id=state["userId"],
        repo_url=url,
    )

    return documents


SCOPE_CACHE_DIR = "scope_cache"


def _scope_key(userId: str) -> str:
    return hashlib.sha256(f"{userId}".encode()).hexdigest()


def save_repo_scope_metadata(userId: str, url: str, scope_metadata: dict):
    os.makedirs(SCOPE_CACHE_DIR, exist_ok=True)
    path = os.path.join(SCOPE_CACHE_DIR, f"{_scope_key(userId)}.json")
    with open(path, "w") as f:
        json.dump(scope_metadata, f)


def load_repo_scope_metadata(userId: str, url: str) -> dict | None:
    path = os.path.join(SCOPE_CACHE_DIR, f"{_scope_key(userId)}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


# if __name__ == "__main__":
#     github_parser(
#         "https://github.com/ShivanshCharak/AI-Retrieval what ai technology is used here",
#         4,
#     )
