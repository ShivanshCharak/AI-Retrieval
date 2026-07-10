import os

from ast_parser import parse_python_file
from symbol_extractor import extract_symbols, extract_calls, extract_imports


def index_repo(repo_path):

    repo_index = []

    for root, _, files in os.walk(repo_path):

        for file in files:

            if not file.endswith(".py"):
                continue

            path = os.path.join(root, file)

            try:

                tree = parse_python_file(path)

                symbols = extract_symbols(tree)
                calls = extract_calls(tree)
                imports = extract_imports(tree)

                repo_index.append(
                    {
                        "file": path,
                        "symbols": symbols,
                        "calls": calls,
                        "imports": imports,
                    }
                )

            except Exception as e:
                print(e)

    return repo_index
