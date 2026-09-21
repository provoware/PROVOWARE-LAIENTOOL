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


def _literal_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _import_aliases(tree: ast.AST) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".", 1)[0]
                aliases[local] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name == "*":
                    continue
                local = alias.asname or alias.name
                aliases[local] = f"{node.module}.{alias.name}"
    return aliases


def _qualified_name(node: ast.AST, aliases: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        parent = _qualified_name(node.value, aliases)
        if parent:
            return f"{parent}.{node.attr}"
    return None


def _is_path_expr(
    node: ast.AST,
    *,
    path_names: set[str],
    aliases: dict[str, str],
) -> bool:
    if isinstance(node, ast.Name):
        return node.id in path_names
    if isinstance(node, ast.Call):
        name = _qualified_name(node.func, aliases)
        if name in {"Path", "pathlib.Path"}:
            return True
        if isinstance(node.func, ast.Attribute) and node.func.attr in {
            "resolve",
            "absolute",
            "expanduser",
        }:
            return _is_path_expr(node.func.value, path_names=path_names, aliases=aliases)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        return _is_path_expr(node.left, path_names=path_names, aliases=aliases)
    if isinstance(node, ast.Attribute) and node.attr in {"parent"}:
        return _is_path_expr(node.value, path_names=path_names, aliases=aliases)
    return False


def _path_variable_names(tree: ast.AST, aliases: dict[str, str]) -> set[str]:
    names: set[str] = set()
    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            target: ast.AST | None = None
            value: ast.AST | None = None
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                value = node.value
            elif isinstance(node, ast.AnnAssign):
                target = node.target
                value = node.value
            if (
                isinstance(target, ast.Name)
                and value is not None
                and target.id not in names
                and _is_path_expr(value, path_names=names, aliases=aliases)
            ):
                names.add(target.id)
                changed = True
    return names


def analyze_source(source: str, *, filename: str = "<memory>") -> tuple[str, ...]:
    tree = ast.parse(source, filename=filename)
    aliases = _import_aliases(tree)
    path_names = _path_variable_names(tree, aliases)
    violations: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        name = _qualified_name(node.func, aliases)
        line = getattr(node, "lineno", "?")

        if name in FORBIDDEN_QUALIFIED:
            violations.append(f"{filename}:{line}: verbotene Schreib-API {name}")
            continue

        if isinstance(node.func, ast.Attribute) and node.func.attr in FORBIDDEN_ATTRS:
            violations.append(
                f"{filename}:{line}: verbotene Schreib-API .{node.func.attr}()"
            )
            continue

        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "replace"
            and _is_path_expr(
                node.func.value,
                path_names=path_names,
                aliases=aliases,
            )
        ):
            violations.append(
                f"{filename}:{line}: verbotene Path-Schreib-API .replace()"
            )
            continue

        if name in {"open", "builtins.open"} or (
            isinstance(node.func, ast.Attribute) and node.func.attr == "open"
        ):
            mode_node: ast.AST | None = None
            if len(node.args) >= 2:
                mode_node = node.args[1]
            for keyword in node.keywords:
                if keyword.arg == "mode":
                    mode_node = keyword.value

            if mode_node is None:
                continue

            mode = _literal_string(mode_node)
            if mode is None:
                violations.append(
                    f"{filename}:{line}: open()-Modus ist nicht statisch als read-only belegbar"
                )
            elif any(marker in mode for marker in WRITE_MODE_MARKERS):
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
    print(" - Import-Aliase und dynamische open()-Modi werden fail-closed geprüft")
    print(" - Executor-/Persistenzpfade bleiben statisch gesperrt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
