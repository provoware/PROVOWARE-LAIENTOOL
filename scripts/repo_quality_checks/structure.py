"""Stable repository structure, starter and TODO contracts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

Fail = Callable[[str], None]

CORE_REQUIRED = (
    "README.md",
    "PROVOWARE.desktop",
    "start.sh",
    "requirements-gui.txt",
    "AGENTS.md",
    "PROVOWARE_TODO_INPUT_POOL0.md",
    "todo.txt",
    "docs/README.md",
    "docs/MAINTENANCE.md",
    "docs/DATEIENREGISTER.md",
    "docs/CURRENT_ITERATION.md",
    "docs/INFO_TEXT_GOVERNANCE.md",
    "docs/UPDATE_ORCHESTRATION.md",
    "docs/REGRESSION_MATRIX.md",
    "docs/REGRESSIONSMANIFEST.json",
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
    "scripts/i25_auto_evidence.py",
    "scripts/i31_auto_evidence.py",
    "scripts/build_portable_package.py",
    "scripts/validate_portable_package.py",
    "scripts/wheelhouse_integrity.py",
    "scripts/verify_wheelhouse_integrity.py",
    "scripts/plugin_boundary_guard.py",
    "scripts/core_diagnostics.py",
    "scripts/read_only_guard.py",
    "scripts/diagnostic_writer_guard.py",
    "src/provoware_laientool/diagnostic_export.py",
    "src/provoware_laientool/diagnostic_export_adapter.py",
    "src/provoware_laientool/diagnostic_export_gui.py",
    "scripts/diagnostic_snapshot.py",
    "scripts/second_device_evidence.py",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/CODEOWNERS",
    ".github/workflows/repo-quality.yml",
    ".github/workflows/i25-gui-evidence.yml",
    ".github/workflows/i31-export-evidence.yml",
    ".github/workflows/portable-package.yml",
)
PRIORITIES = {"P0", "P1", "P2", "P3"}


def check_structure(root: Path, fail: Fail) -> None:
    if len(CORE_REQUIRED) != len(set(CORE_REQUIRED)):
        duplicates = sorted({rel for rel in CORE_REQUIRED if CORE_REQUIRED.count(rel) > 1})
        fail(f"Doppelte Pflichtdatei-Einträge im Repository-Gate: {duplicates}")

    for rel in CORE_REQUIRED:
        if not (root / rel).is_file():
            fail(f"Pflichtdatei fehlt: {rel}")

    requirements_gui = root / "requirements-gui.txt"
    if requirements_gui.is_file():
        lines = [
            line.strip()
            for line in requirements_gui.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        if lines != ["PySide6==6.11.2"]:
            fail("requirements-gui.txt muss exakt PySide6==6.11.2 pinnen")

    starter_sh = root / "start.sh"
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
            "--i25-evidence",
            "--i25-offscreen",
            "--i31-evidence",
            "--i31-offscreen",
            "--i31-cli-evidence",
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
            "scripts/i25_auto_evidence.py",
            "scripts/i31_auto_evidence.py",
            "scripts/verify_wheelhouse_integrity.py",
            "scripts/diagnostic_snapshot.py",
        ):
            if marker not in starter_text:
                fail(f"start.sh Venv-Vertrag fehlt: {marker}")
        for forbidden in ("sudo ", "apt install", "chmod 777"):
            if forbidden in starter_text:
                fail(f"start.sh enthält verbotene Systemmutation: {forbidden!r}")

    baseline = root / "PROVOWARE_TODO_INPUT_POOL0.md"
    if baseline.is_file():
        text = baseline.read_text(encoding="utf-8")
        for marker in ("REQ-BASELINE-1", *(f"B{i:02d}" for i in range(12))):
            if marker not in text:
                fail(f"Baseline-Marker fehlt: {marker}")

    todo = root / "todo.txt"
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
