#!/usr/bin/env python3
"""Fail-closed static guard for the currently locked read-only product code.

The guard scans only src/provoware_laientool. It rejects obvious filesystem
write APIs until a later explicit executor gate deliberately changes this
contract.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "provoware_laientool"

FORBIDDEN_ATTRS = {
    "write_text",
    "write_bytes",
    "unlink",
    "rename",
    "replace",
    "mkdir",
    "touch",
    "chmod",
    "symlink_to",
    "hardlink_to",
}

FORBIDDEN_QUALIFIED = {
    "os.remove",
    "os.unlink",
    "os.rename",
    "os.replace",
    "os.mkdir",
    "os.makedirs",
    "os.rmdir",
    "os.removedirs",
    "os.chmod",
    "shutil.copy",
    "shutil.copy2",
    "shutil.copyfile",
    "shutil.copytree",
    "shutil.move",
    "shutil.rmtree",
}

WRITE_MODE_MARKERS = {"w", "a", "x", "+"}


def _qualified_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _qualified_name(node.value)
        if parent:
            return f"{parent}.{node.attr}"
    return None


def _literal_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def analyze_source(source: str, *, filename: str = "<memory>") -> tuple[str, ...]:
    tree = ast.parse(source, filename=filename)
    violations: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        name = _qualified_name(node.func)
        line = getattr(node, "lineno", "?")

        if name in FORBIDDEN_QUALIFIED:
            violations.append(f"{filename}:{line}: verbotene Schreib-API {name}")
            continue

        if isinstance(node.func, ast.Attribute) and node.func.attr in FORBIDDEN_ATTRS:
            violations.append(
                f"{filename}:{line}: verbotene Schreib-API .{node.func.attr}()"
            )
            continue

        if name == "open" or (
            isinstance(node.func, ast.Attribute) and node.func.attr == "open"
        ):
            mode_node: ast.AST | None = None
            if len(node.args) >= 2:
                mode_node = node.args[1]
            for keyword in node.keywords:
                if keyword.arg == "mode":
                    mode_node = keyword.value
            mode = _literal_string(mode_node)
            if mode is not None and any(marker in mode for marker in WRITE_MODE_MARKERS):
                violations.append(
                    f"{filename}:{line}: schreibender open()-Modus {mode!r}"
                )

    return tuple(violations)


def scan_product_tree(root: Path = SRC) -> tuple[str, ...]:
    violations: list[str] = []
    for path in sorted(root.rglob("*.py")):
        try:
            source = path.read_text(encoding="utf-8")
            relative = str(path.relative_to(ROOT))
            violations.extend(analyze_source(source, filename=relative))
        except (OSError, UnicodeError, SyntaxError) as exc:
            violations.append(f"{path}: Guard konnte Datei nicht sicher prüfen: {exc}")
    return tuple(violations)


def main() -> int:
    violations = scan_product_tree()
    if violations:
        print("🔴 Read-only-Lock FEHLER")
        for violation in violations:
            print(f" - {violation}")
        return 1

    print("🟢 Read-only-Lock PASS")
    print(" - keine offensichtliche Dateisystem-Schreib-API im Produktionscode")
    print(" - Executor-/Persistenzpfade bleiben statisch gesperrt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
