#!/usr/bin/env python3
"""Dependency-free repository contract checks for PROVOWARE-LAIENTOOL."""

from __future__ import annotations

import sys
from pathlib import Path

from repo_quality_checks.documentation import (
    check_information_registry,
    check_iteration_index,
    check_markdown_links,
    check_stable_status_text,
    check_trailing_whitespace,
)
from repo_quality_checks.regression import check_regression_manifest
from repo_quality_checks.source import check_python_sources
from repo_quality_checks.structure import check_structure
from repo_quality_checks.workflows import check_workflows

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


check_structure(ROOT, fail)
check_regression_manifest(ROOT, fail)
check_information_registry(ROOT, fail)
check_python_sources(ROOT, fail)
check_workflows(ROOT, fail)
check_iteration_index(ROOT, fail)
check_markdown_links(ROOT, fail)
check_stable_status_text(ROOT, fail)
check_trailing_whitespace(ROOT, fail)

if errors:
    print("🔴 Repository-Gate FEHLER")
    for error in errors:
        print(f" - {error}")
    sys.exit(1)

print("🟢 Repository-Gate PASS")
print(" - stabile Pflichtstruktur und dynamischer Iterationsindex konsistent")
print(" - start.sh als kanonischer Venv-first Starter, Offline-Wheelhouse und PySide6-Pin konsistent")
print(" - Baseline-Marker vorhanden")
print(" - TODO-Schema, Sortierung und Duplikate konsistent")
print(" - Regressionsmanifest, Fehlerfamilien und Prüfpfade konsistent")
print(" - führende Informationsdateien im Dateienregister erfasst")
print(" - Python-Syntax in Produktcode, Skripten, Tests und Starter geprüft")
print(" - kein Tkinter im Python-Produktionscode")
print(" - Workflow-Permissions, Job-Timeouts, Concurrency, Post-Merge-GUI-Gate und Action-Pinning geprüft")
print(" - interne Markdown-Links, Tabellenumbrüche und stabile Statusformulierungen geprüft")
print(" - kein Trailing-Whitespace in zentralen Textformaten")
