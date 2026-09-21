#!/usr/bin/env python3
"""Fail-closed repository guard for the still-disabled plugin runtime."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
ALLOWED_PLUGIN_CONTRACT = SRC / "provoware_laientool" / "plugin_contract.py"
FORBIDDEN_IMPORT_PREFIXES = ("importlib", "pkg_resources", "requests", "httpx")
FORBIDDEN_TEXT_MARKERS = (
    "pip install",
    "entry_points(",
    "spec_from_file_location(",
    "exec_module(",
)
FORBIDDEN_FILENAMES = {"plugin_loader.py", "plugin_manager.py", "plugin_runtime.py"}


def analyze_source(source: str, *, label: str = "<memory>") -> tuple[str, ...]:
    failures: list[str] = []
    try:
        tree = ast.parse(source, filename=label)
    except SyntaxError as exc:
        return (f"Syntaxfehler in {label}: {exc}",)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        else:
            names = []

        for name in names:
            if any(
                name == prefix or name.startswith(prefix + ".")
                for prefix in FORBIDDEN_IMPORT_PREFIXES
            ):
                failures.append(
                    f"{label}: gesperrter Plugin-/Netzwerkimport: {name}"
                )

        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "__import__"
        ):
            failures.append(f"{label}: dynamischer __import__ ist gesperrt.")

    lowered = source.lower()
    for marker in FORBIDDEN_TEXT_MARKERS:
        if marker.lower() in lowered:
            failures.append(f"{label}: gesperrter Plugin-Marker: {marker}")
    return tuple(failures)


def scan_repository() -> tuple[str, ...]:
    failures: list[str] = []
    for path in sorted(SRC.rglob("*.py")):
        if path.resolve() == ALLOWED_PLUGIN_CONTRACT.resolve():
            continue
        relative = path.relative_to(ROOT)
        if path.name in FORBIDDEN_FILENAMES:
            failures.append(f"Verbotener Plugin-Runtime-Dateiname: {relative}")
        if "plugins" in {part.lower() for part in relative.parts}:
            failures.append(f"Plugin-Runtime-Verzeichnis ist noch gesperrt: {relative}")
        try:
            source = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            failures.append(f"Nicht-UTF-8 Python-Datei: {relative}: {exc}")
            continue
        failures.extend(analyze_source(source, label=str(relative)))
    return tuple(failures)


def main() -> int:
    failures = scan_repository()
    if failures:
        print("🔴 Plugin-Boundary-Gate FEHLER")
        for item in failures:
            print(f" - {item}")
        return 1

    print("🟢 Plugin-Boundary-Gate PASS")
    print(" - keine dynamischen Plugin-Loader")
    print(" - kein Auto-Install/Entry-Point-Laden")
    print(" - keine gesperrten Plugin-Runtime-Verzeichnisse")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
