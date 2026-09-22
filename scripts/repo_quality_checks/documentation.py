"""Documentation index, link, status and text-hygiene checks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

Fail = Callable[[str], None]
TEXT_SUFFIXES = {".md", ".txt", ".py", ".sh", ".yml", ".yaml"}


def check_information_registry(root: Path, fail: Fail) -> None:
    information_registry = root / "docs" / "DATEIENREGISTER.md"
    if not information_registry.is_file():
        return
    registry_text = information_registry.read_text(encoding="utf-8")
    registered_information = (
        "README.md",
        "AGENTS.md",
        "todo.txt",
        "PROVOWARE_TODO_INPUT_POOL0.md",
        "requirements-gui.txt",
        "docs/README.md",
        "docs/CURRENT_ITERATION.md",
        "docs/INFO_TEXT_GOVERNANCE.md",
        "docs/MAINTENANCE.md",
        "docs/REGRESSION_MATRIX.md",
        "docs/REGRESSIONSMANIFEST.json",
        "docs/evidence/README.md",
    )
    for rel in registered_information:
        if f"`{rel}`" not in registry_text:
            fail(f"Informationsdatei fehlt im Register: {rel}")


def check_iteration_index(root: Path, fail: Fail) -> None:
    iteration_docs = sorted((root / "docs").glob("I[0-9][0-9]_*.md"))
    if not iteration_docs:
        fail("Keine Iterationsdokumente unter docs/I??_*.md gefunden")
    docs_index = root / "docs" / "README.md"
    if docs_index.is_file():
        index_text = docs_index.read_text(encoding="utf-8")
        for path in iteration_docs:
            if path.name not in index_text:
                fail(f"Iterationsdokument fehlt im docs/README.md-Index: {path.name}")


def check_markdown_links(root: Path, fail: Fail) -> None:
    markdown_link = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            fail(f"Markdown-Datei ist nicht UTF-8: {path.relative_to(root)}: {exc}")
            continue
        if re.search(r"\|\\n\|", text):
            fail(f"Wörtliches \\n zwischen Markdown-Tabellenzeilen: {path.relative_to(root)}")
        link_text = re.sub(r"(?ms)^\x60\x60\x60.*?^\x60\x60\x60\s*$", "", text)
        for target in markdown_link.findall(link_text):
            target = target.strip()
            if not target or target.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            target = target.split("#", 1)[0].split("?", 1)[0].strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            if not target:
                continue
            candidate = (path.parent / target).resolve()
            try:
                candidate.relative_to(root.resolve())
            except ValueError:
                fail(f"Markdown-Link verlässt Repository: {path.relative_to(root)} -> {target}")
                continue
            if not candidate.exists():
                fail(f"Interner Markdown-Link fehlt: {path.relative_to(root)} -> {target}")


def check_stable_status_text(root: Path, fail: Fail) -> None:
    readme_text = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    todo_text = (root / "todo.txt").read_text(encoding="utf-8") if (root / "todo.txt").is_file() else ""
    if "CI ausstehend" in readme_text:
        fail("README.md enthält flüchtigen CI-Status statt dauerhaftem Capability-Stand")
    for phrase in ("CI ausstehend", "über CI einfrieren"):
        if phrase in todo_text:
            fail(f"todo.txt enthält flüchtigen CI-Status: {phrase!r}")


def check_trailing_whitespace(root: Path, fail: Fail) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix not in TEXT_SUFFIXES:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, 1):
            if line.rstrip() != line:
                fail(f"Trailing whitespace: {path.relative_to(root)}:{number}")
