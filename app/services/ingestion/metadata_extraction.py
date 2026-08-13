from pydantic import BaseModel
import os


from app.services.llm.llm_service import llm


class CollectionMetadata(BaseModel):
    summary: str
    topics: list[str]


def generate_collection_metadata(docs):

    text = "\n".join(doc.page_content[:1000] for doc in docs[:5])

    structured = llm.with_structured_output(CollectionMetadata)

    prompt = f"""
            Analyze this document collection.

            Generate:

            1. Short summary
            2. Top 10 topics each topic shud have atleats 100words scentnec explaining the context of the current topic present in the pdf

            Document:
            {text}
            """
    ans = structured.invoke(prompt)

    return ans


def build_repo_scope_metadata(repo: list[dict]) -> dict:
    total_files = len(repo)
    total_symbols = 0
    total_calls = 0
    total_imports = set()
    total_constants = 0
    total_globals = 0
    symbol_types = {}
    largest_files = []
    call_graph_edges = 0
    external_imports = set()
    internal_imports = set()

    for entry in repo:
        symbols = entry["symbols"]
        total_symbols += len(symbols)
        total_calls += len(entry["calls"])
        total_constants += len(entry["constants"])
        total_globals += len(entry["global_variables"])

        for sym in symbols:
            t = sym["type"]
            symbol_types[t] = symbol_types.get(t, 0) + 1

        for imp in entry["imports"]:
            # normalize: handle both dict-shaped and plain-string imports
            if isinstance(imp, dict):
                imp_key = imp.get("module") or imp.get("name") or str(imp)
            else:
                imp_key = imp

            total_imports.add(imp_key)

            if imp_key.startswith(entry["file"].split("/")[0]):
                internal_imports.add(imp_key)
            else:
                external_imports.add(imp_key)

        call_graph_edges += len(entry["calls"])
        largest_files.append((entry["file"], len(symbols)))

    largest_files.sort(key=lambda x: -x[1])

    return {
        "total_files": total_files,
        "total_symbols": total_symbols,
        "symbol_types": symbol_types,
        "total_calls": total_calls,
        "call_graph_edges": call_graph_edges,
        "total_constants": total_constants,
        "total_globals": total_globals,
        "unique_imports": len(total_imports),
        "external_deps": sorted(external_imports),
        "internal_modules": sorted(internal_imports),
        "largest_files": largest_files[:10],
    }
