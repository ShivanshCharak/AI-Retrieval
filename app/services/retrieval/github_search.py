import re

import os

from app.services.ingestion.github_loader import clone_repo
from app.services.ingestion.ast_parser import parse_python_file
from app.services.retrieval.vector_search import vector_store
from app.services.ingestion.symbol_extractor import (
    extract_calls,
    extract_symbols,
    extract_imports,
    extract_constants,
    extract_global_variables,
)
from langchain_core.documents import Document


def github_search(query: str, userId: str):
    url = extract_github_url(query)
    print(url)
    repo_path = clone_repo(url)
    repo = []
    documents = []
    for root, _, files in os.walk(repo_path):
        for file in files:

            if not file.endswith(".py"):
                continue
            file_path = os.path.join(root, file)
            parsed = parse_python_file(file_path)
            source = parsed["source"]
            if not parsed["success"]:
                continue
            tree = parsed["tree"]
            symbols = extract_symbols(tree, source)
            repo.append(
                {
                    "file": file_path,
                    "symbols": extract_symbols(tree, source),
                    "id": f"{file_path}:{symbols[0]['name']}",
                    "calls": extract_calls(tree),
                    "imports": extract_imports(tree),
                    "constants": extract_constants(tree),
                    "global_variables": extract_global_variables(tree),
                }
            )
            for symbol in symbols:
                documents.append(
                    Document(
                        page_content=symbol["source"],
                        metadata={
                            "user_id": userId,
                            "repo_url": url,
                            "id": f"{file_path}:{symbol['name']}",
                            "file": file_path,
                            "name": symbol["name"],
                            "type": symbol["type"],
                            "line": symbol["line"],
                            "end_line": symbol["end_line"],
                            "args": symbol.get("args"),
                            "docstring": symbol.get("docstring"),
                            "calls": symbol.get("calls"),
                        },
                    )
                )
    vector_store.add_documents(documents)
    return repo


def extract_github_url(text: str):
    match = re.search(r"https?://\S+", text)
    return match.group(0) if match else None
