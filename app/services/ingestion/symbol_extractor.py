import ast


def extract_symbols(tree: ast.AST, source):

    symbols = []

    calls = []
    returns = []
    raises = []

    for node in ast.walk(tree):

        # Classes
        if isinstance(node, ast.ClassDef):

            symbols.append(
                {
                    "type": "class",
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "bases": [ast.unparse(base) if hasattr(ast, "unparse") else None for base in node.bases],
                    "decorators": [ast.unparse(d) if hasattr(ast, "unparse") else None for d in node.decorator_list],
                    "docstring": ast.get_docstring(node),
                    "source": ast.get_source_segment(source, node),
                }
            )

        # Normal functions
        elif isinstance(node, ast.FunctionDef):

            symbols.append(
                {
                    "type": "function",
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "args": [a.arg for a in node.args.args],
                    "returns": (ast.unparse(node.returns) if node.returns and hasattr(ast, "unparse") else None),
                    "decorators": [ast.unparse(d) if hasattr(ast, "unparse") else None for d in node.decorator_list],
                    "docstring": ast.get_docstring(node),
                    "source": ast.get_source_segment(source, node),
                }
            )

        # Async functions
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

            calls = []
            returns = []
            raises = []

            for child in ast.walk(node):

                if isinstance(child, ast.Call):

                    if isinstance(child.func, ast.Name):
                        calls.append(child.func.id)

                    elif isinstance(child.func, ast.Attribute):
                        calls.append(ast.unparse(child.func))

                elif isinstance(child, ast.Return):

                    if child.value:
                        returns.append(ast.unparse(child.value))
                    else:
                        returns.append(None)

                elif isinstance(child, ast.Raise):

                    if child.exc:
                        raises.append(ast.unparse(child.exc))

            symbols.append(
                {
                    "type": "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function",
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "args": [a.arg for a in node.args.args],
                    "returns_annotation": (ast.unparse(node.returns) if node.returns else None),
                    "returns": returns,
                    "raises": raises,
                    "calls": sorted(set(calls)),
                    "decorators": [ast.unparse(d) for d in node.decorator_list],
                    "docstring": ast.get_docstring(node),
                    "source": ast.get_source_segment(source, node),
                }
            )

    return symbols


def extract_calls(tree: ast.AST):

    calls = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                calls.append(node.func.id)

            elif isinstance(node.func, ast.Attribute):

                calls.append(ast.unparse(node.func))

    return sorted(set(calls))


def extract_imports(tree: ast.AST):

    imports = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):

            for name in node.names:

                imports.append(name.name)

        elif isinstance(node, ast.ImportFrom):

            imports.append(
                {
                    "module": node.module,
                    "names": [n.name for n in node.names],
                }
            )

    return imports


def extract_global_variables(tree: ast.AST):

    variables = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Assign):

            for target in node.targets:

                if isinstance(target, ast.Name):

                    variables.append(
                        {
                            "name": target.id,
                            "line": node.lineno,
                        }
                    )

    return variables


def extract_constants(tree: ast.AST):

    constants = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Assign):

            for target in node.targets:

                if isinstance(target, ast.Name) and target.id.isupper():

                    constants.append(
                        {
                            "name": target.id,
                            "line": node.lineno,
                        }
                    )

    return constants
