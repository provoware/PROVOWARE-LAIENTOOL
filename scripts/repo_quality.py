#!/usr/bin/env python3
"""Dependency-free repository contract checks for PROVOWARE-LAIENTOOL."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md",
    "AGENTS.md",
    "PROVOWARE_TODO_INPUT_POOL0.md",
    "todo.txt",
    "docs/adr/ADR-0001-ui-cli-foundation.md",
    "docs/evidence/README.md",
    "docs/UI_DESIGN_SYSTEM.md",
    "docs/theme-tokens.md",
    "docs/B01_PLATFORM_PREFLIGHT.md",
    "docs/B01_PATH_BOUNDARIES.md",
    "docs/B01_SECOND_DEVICE_EVIDENCE.md",
    "docs/evidence/EV-20260921-003-b01b-path-boundaries.md",
    "docs/UPDATE_ORCHESTRATION.md",
    "docs/LAIEN_QUALITY_STANDARD.md",
    "docs/INFO_TEXT_GOVERNANCE.md",
    "docs/GUI_CLI_PARITY.md",
    "docs/I10_CAPABILITY_REGISTRY.md",
    "docs/I11_READONLY_SHELL.md",
    "docs/I12_PREVIEW_MODEL.md",
    "docs/CURRENT_ITERATION.md",
    "scripts/info_text_guard.py",
    "scripts/second_device_evidence.py",
    "docs/evidence/EV-20260921-002-b01a-preflight.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/CODEOWNERS",
    ".github/workflows/repo-quality.yml",
)
TEXT_SUFFIXES = {".md", ".txt", ".py", ".yml", ".yaml"}
PRIORITIES = {"P0", "P1", "P2", "P3"}
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


if len(REQUIRED) != len(set(REQUIRED)):
    duplicates = sorted({rel for rel in REQUIRED if REQUIRED.count(rel) > 1})
    fail(f"Doppelte Pflichtdatei-Einträge im Repository-Gate: {duplicates}")

for rel in REQUIRED:
    if not (ROOT / rel).is_file():
        fail(f"Pflichtdatei fehlt: {rel}")

baseline = ROOT / "PROVOWARE_TODO_INPUT_POOL0.md"
if baseline.is_file():
    text = baseline.read_text(encoding="utf-8")
    for marker in ("REQ-BASELINE-1", *(f"B{i:02d}" for i in range(12))):
        if marker not in text:
            fail(f"Baseline-Marker fehlt: {marker}")

todo = ROOT / "todo.txt"
if todo.is_file():
    entries = [line for line in todo.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not entries:
        fail("todo.txt enthält keine operativen Einträge")
    seen: set[str] = set()
    last_priority = -1
    for number, line in enumerate(entries, 1):
        parts = line.split(" – ")
        if len(parts) != 4:
            fail(f"todo.txt Zeile {number}: erwartet 4 Felder mit ' – '")
            continue
        match = re.match(r"^\[(P[0-3])\]\s+\S", parts[0])
        if not match or match.group(1) not in PRIORITIES:
            fail(f"todo.txt Zeile {number}: ungültige Priorität/Area")
        else:
            priority = int(match.group(1)[1])
            if priority < last_priority:
                fail(f"todo.txt Zeile {number}: Prioritäten müssen P0 → P3 sortiert sein")
            last_priority = priority
        if line in seen:
            fail(f"todo.txt Zeile {number}: doppelter Eintrag")
        seen.add(line)
        if any(not part.strip() for part in parts):
            fail(f"todo.txt Zeile {number}: leeres Feld")

src = ROOT / "src"
if src.exists():
    for path in src.rglob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            fail(f"Python-Syntaxfehler in {path.relative_to(ROOT)}: {exc}")
            continue
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            if any(name == "tkinter" or name.startswith("tkinter.") for name in names):
                fail(f"Tkinter-Import verboten: {path.relative_to(ROOT)}")

for workflow in (ROOT / ".github" / "workflows").glob("*.y*ml"):
    text = workflow.read_text(encoding="utf-8")
    if re.search(r"(?m)^permissions:\s*$", text) is None:
        fail(f"Workflow ohne explizite permissions: {workflow.relative_to(ROOT)}")
    for action in re.findall(r"(?m)^\s*uses:\s*([^\s#]+)", text):
        if action.startswith("./"):
            continue
        ref = action.rsplit("@", 1)[-1] if "@" in action else ""
        if not re.fullmatch(r"[0-9a-fA-F]{40}", ref):
            fail(f"Action nicht auf Commit-SHA gepinnt: {action}")

for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts or path.suffix not in TEXT_SUFFIXES:
        continue
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        continue
    for number, line in enumerate(lines, 1):
        if line.rstrip() != line:
            fail(f"Trailing whitespace: {path.relative_to(ROOT)}:{number}")

if errors:
    print("🔴 Repository-Gate FEHLER")
    for error in errors:
        print(f" - {error}")
    sys.exit(1)

print("🟢 Repository-Gate PASS")
print(" - Pflichtstruktur vorhanden und ohne doppelte Gate-Einträge")
print(" - Baseline-Marker vorhanden")
print(" - TODO-Schema, Sortierung und Duplikate konsistent")
print(" - kein Tkinter im Python-Produktionscode")
print(" - Workflow-Permissions und Action-Pinning geprüft")
print(" - kein Trailing-Whitespace in zentralen Textformaten")
