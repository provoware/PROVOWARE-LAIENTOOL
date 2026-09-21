#!/usr/bin/env python3
"""Dependency-free repository contract checks for PROVOWARE-LAIENTOOL."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_REQUIRED = (
    "README.md",
    "start.sh",
    "requirements-gui.txt",
    "AGENTS.md",
    "PROVOWARE_TODO_INPUT_POOL0.md",
    "todo.txt",
    "docs/README.md",
    "docs/MAINTENANCE.md",
    "docs/CURRENT_ITERATION.md",
    "docs/INFO_TEXT_GOVERNANCE.md",
    "docs/UPDATE_ORCHESTRATION.md",
    "docs/REGRESSION_MATRIX.md",
    "docs/DEBUGGING_STANDARD.md",
    "docs/LAIEN_QUALITY_STANDARD.md",
    "docs/GUI_CLI_PARITY.md",
    "docs/UI_DESIGN_SYSTEM.md",
    "docs/theme-tokens.md",
    "docs/B01_PLATFORM_PREFLIGHT.md",
    "docs/B01_PATH_BOUNDARIES.md",
    "docs/B01_SECOND_DEVICE_EVIDENCE.md",
    "docs/adr/ADR-0001-ui-cli-foundation.md",
    "docs/evidence/README.md",
    "scripts/info_text_guard.py",
    "scripts/accessibility_evidence.py",
    "scripts/i17_auto_evidence.py",
    "scripts/core_diagnostics.py",
    "scripts/read_only_guard.py",
    "scripts/diagnostic_snapshot.py",
    "scripts/second_device_evidence.py",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/CODEOWNERS",
    ".github/workflows/repo-quality.yml",
)
TEXT_SUFFIXES = {".md", ".txt", ".py", ".sh", ".yml", ".yaml"}
PRIORITIES = {"P0", "P1", "P2", "P3"}
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


if len(CORE_REQUIRED) != len(set(CORE_REQUIRED)):
    duplicates = sorted({rel for rel in CORE_REQUIRED if CORE_REQUIRED.count(rel) > 1})
    fail(f"Doppelte Pflichtdatei-Einträge im Repository-Gate: {duplicates}")

for rel in CORE_REQUIRED:
    if not (ROOT / rel).is_file():
        fail(f"Pflichtdatei fehlt: {rel}")

requirements_gui = ROOT / "requirements-gui.txt"
if requirements_gui.is_file():
    lines = [
        line.strip()
        for line in requirements_gui.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if lines != ["PySide6==6.11.2"]:
        fail("requirements-gui.txt muss exakt PySide6==6.11.2 pinnen")

starter_sh = ROOT / "start.sh"
if starter_sh.is_file():
    starter_text = starter_sh.read_text(encoding="utf-8")
    for marker in (
        "set -euo pipefail",
        ".venv",
        'EXPECTED_PYSIDE6="6.11.2"',
        "-m venv",
        "validate_venv",
        "validate_gui_runtime",
        "--gui",
        "--menu",
        "--preflight",
        "--json",
        "--i17",
        "--i17-auto",
        "--i17-offscreen",
        "--diagnostics",
        "--diagnostics-json",
        "--second-device-evidence",
        "--second-device-evidence-json",
        "scripts/i17_auto_evidence.py",
        "scripts/diagnostic_snapshot.py",
    ):
        if marker not in starter_text:
            fail(f"start.sh Venv-Vertrag fehlt: {marker}")
    for forbidden in ("sudo ", "apt install", "chmod 777"):
        if forbidden in starter_text:
            fail(f"start.sh enthält verbotene Systemmutation: {forbidden!r}")

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

python_files = [ROOT / "start.py"]
for directory in ("src", "scripts", "tests"):
    base = ROOT / directory
    if base.exists():
        python_files.extend(base.rglob("*.py"))

for path in sorted(path for path in python_files if path.is_file()):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        fail(f"Python-Syntaxfehler in {path.relative_to(ROOT)}: {exc}")
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
            fail(f"Tkinter-Import verboten: {path.relative_to(ROOT)}")
for workflow in (ROOT / ".github" / "workflows").glob("*.y*ml"):
    text = workflow.read_text(encoding="utf-8")
    if re.search(r"(?m)^permissions:\s*$", text) is None:
        fail(f"Workflow ohne explizite permissions: {workflow.relative_to(ROOT)}")
    if re.search(r"(?m)^\s{2,}timeout-minutes:\s*[1-9][0-9]*\s*$", text) is None:
        fail(f"Workflow ohne Job-Timeout: {workflow.relative_to(ROOT)}")
    if re.search(r"(?mi)^\s*continue-on-error:\s*true\s*$", text):
        fail(f"Workflow darf Fehler nicht pauschal ignorieren: {workflow.relative_to(ROOT)}")
    for action in re.findall(r"(?m)^\s*uses:\s*([^\s#]+)", text):
        if action.startswith("./"):
            continue
        ref = action.rsplit("@", 1)[-1] if "@" in action else ""
        if not re.fullmatch(r"[0-9a-fA-F]{40}", ref):
            fail(f"Action nicht auf Commit-SHA gepinnt: {action}")

iteration_docs = sorted((ROOT / "docs").glob("I[0-9][0-9]_*.md"))
if not iteration_docs:
    fail("Keine Iterationsdokumente unter docs/I??_*.md gefunden")
docs_index = ROOT / "docs" / "README.md"
if docs_index.is_file():
    index_text = docs_index.read_text(encoding="utf-8")
    for path in iteration_docs:
        if path.name not in index_text:
            fail(f"Iterationsdokument fehlt im docs/README.md-Index: {path.name}")

markdown_link = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
for path in ROOT.rglob("*.md"):
    if ".git" in path.parts:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        fail(f"Markdown-Datei ist nicht UTF-8: {path.relative_to(ROOT)}: {exc}")
        continue
    if re.search(r"\|\\n\|", text):
        fail(f"Wörtliches \\n zwischen Markdown-Tabellenzeilen: {path.relative_to(ROOT)}")
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
            candidate.relative_to(ROOT.resolve())
        except ValueError:
            fail(f"Markdown-Link verlässt Repository: {path.relative_to(ROOT)} -> {target}")
            continue
        if not candidate.exists():
            fail(f"Interner Markdown-Link fehlt: {path.relative_to(ROOT)} -> {target}")

readme_text = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").is_file() else ""
todo_text = (ROOT / "todo.txt").read_text(encoding="utf-8") if (ROOT / "todo.txt").is_file() else ""
if "CI ausstehend" in readme_text:
    fail("README.md enthält flüchtigen CI-Status statt dauerhaftem Capability-Stand")
for phrase in ("CI ausstehend", "über CI einfrieren"):
    if phrase in todo_text:
        fail(f"todo.txt enthält flüchtigen CI-Status: {phrase!r}")
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
print(" - stabile Pflichtstruktur und dynamischer Iterationsindex konsistent")
print(" - start.sh als kanonischer Venv-first Starter und PySide6-Pin konsistent")
print(" - Baseline-Marker vorhanden")
print(" - TODO-Schema, Sortierung und Duplikate konsistent")
print(" - Python-Syntax in Produktcode, Skripten, Tests und Starter geprüft")
print(" - kein Tkinter im Python-Produktionscode")
print(" - Workflow-Permissions, Job-Timeouts, Fehlerhärte und Action-Pinning geprüft")
print(" - interne Markdown-Links, Tabellenumbrüche und stabile Statusformulierungen geprüft")
print(" - kein Trailing-Whitespace in zentralen Textformaten")
