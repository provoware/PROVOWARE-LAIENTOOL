#!/usr/bin/env python3
"""Diff-based documentation impact guard.

The guard never edits documentation. It fails when a change class that can
make user/project information stale has no matching documentation update.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STATUS_DOCS = {"README.md", "todo.txt"}
PROCESS_DOCS = {
    "AGENTS.md",
    "docs/UPDATE_ORCHESTRATION.md",
    "docs/INFO_TEXT_GOVERNANCE.md",
    "README.md",
}
UX_DOCS = {
    "docs/UI_DESIGN_SYSTEM.md",
    "docs/LAIEN_QUALITY_STANDARD.md",
    "README.md",
    "todo.txt",
}


def changed_files(base: str) -> set[str]:
    command = ["git", "diff", "--name-only", f"{base}..HEAD"]
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff fehlgeschlagen")
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def is_evidence(path: str) -> bool:
    return path.startswith("docs/evidence/") and path.endswith(".md")


def any_doc_changed(changed: set[str], accepted: set[str], *, evidence: bool = False) -> bool:
    return bool(changed & accepted) or (evidence and any(is_evidence(path) for path in changed))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="Basis-Commit für den Impact-Diff")
    args = parser.parse_args()

    try:
        changed = changed_files(args.base)
    except RuntimeError as exc:
        print(f"🔴 Info-Text-Guard konnte Diff nicht bestimmen: {exc}")
        return 2

    failures: list[str] = []

    product_change = any(path == "start.py" or path.startswith("src/") for path in changed)
    process_change = any(
        path == "AGENTS.md"
        or path.startswith(".github/")
        or path in {"scripts/repo_quality.py", "scripts/info_text_guard.py"}
        for path in changed
    )
    ux_change = any(
        any(token in path.lower() for token in ("ui", "gui", "theme", "wizard", "dialog"))
        for path in changed
        if not path.startswith("docs/")
    )

    if product_change and not any_doc_changed(changed, STATUS_DOCS, evidence=True):
        failures.append(
            "Produktkern geändert, aber weder README/todo noch passende Evidence aktualisiert."
        )

    if process_change and not any_doc_changed(changed, PROCESS_DOCS):
        failures.append(
            "Entwicklungs-/CI-Vertrag geändert, aber keine Prozess-/Statusdokumentation aktualisiert."
        )

    if ux_change and not any_doc_changed(changed, UX_DOCS, evidence=True):
        failures.append(
            "UI-/Laienwirkung geändert, aber kein UX-/Laien-Info-Text oder Evidence aktualisiert."
        )

    if failures:
        print("🔴 Info-Text-Impact FEHLER")
        for failure in failures:
            print(f" - {failure}")
        print("Geänderte Dateien:")
        for path in sorted(changed):
            print(f" - {path}")
        return 1

    print("🟢 Info-Text-Impact PASS")
    if not (product_change or process_change or ux_change):
        print(" - keine dokumentationspflichtige Änderungsklasse erkannt")
    else:
        print(" - erkannte Informationswirkung ist durch passende Textänderung abgedeckt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
