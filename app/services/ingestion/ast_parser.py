import ast
from pathlib import Path


def parse_python_file(file_path: str):

    path = Path(file_path)

    try:
        source = path.read_text(encoding="utf-8")

        tree = ast.parse(source, filename=str(path))

        return {
            "success": True,
            "path": str(path),
            "source": source,
            "tree": tree,
            "filename": path.name,
            "extension": path.suffix,
            "module_docstring": ast.get_docstring(tree),
            "line_count": len(source.splitlines()),
        }

    except SyntaxError as e:
        return {
            "success": False,
            "path": str(path),
            "filename": path.name,
            "error": str(e),
            "line": e.lineno,
            "offset": e.offset,
        }

    except Exception as e:
        return {
            "success": False,
            "path": str(path),
            "filename": path.name,
            "error": str(e),
        }
