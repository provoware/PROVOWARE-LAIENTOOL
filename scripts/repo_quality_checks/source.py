"""Python syntax and production import-boundary checks."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Callable

Fail = Callable[[str], None]


def check_python_sources(root: Path, fail: Fail) -> None:
    python_files = [root / "start.py"]
    for directory in ("src", "scripts", "tests"):
        base = root / directory
        if base.exists():
            python_files.extend(base.rglob("*.py"))

    for path in sorted(path for path in python_files if path.is_file()):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            fail(f"Python-Syntaxfehler in {path.relative_to(root)}: {exc}")
            continue
        if "src" not in path.parts:
            continue
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            if any(name == "tkinter" or name.startswith("tkinter.") for name in names):
                fail(f"Tkinter-Import verboten: {path.relative_to(root)}")
