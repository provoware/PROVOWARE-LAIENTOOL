#!/usr/bin/env python3
"""I17 target-system accessibility evidence helper.

This helper does not claim visual PASS. It verifies that the target runtime is
capable of a real GUI run, reuses the automated accessibility contract, and
prints the exact manual gates and screenshot set required for I17.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from accessibility_evidence import build_report  # noqa: E402

SCREENSHOTS = (
    "i17-100-overview.png",
    "i17-150-overview.png",
    "i17-200-overview.png",
    "i17-keyboard-focus.png",
    "i17-file-preview.png",
)

MANUAL_GATES = (
    "100 %: keine abgeschnittene Kernaktion",
    "150 %: keine abgeschnittene Kernaktion",
    "200 %: keine abgeschnittene Kernaktion",
    "Tab/Shift+Tab: kompletter Kernworkflow erreichbar",
    "Fokus: jederzeit sichtbar",
    "Dateivorschau: Ordnerwahl, Abbruch und Ergebnis verständlich",
    "Kontrast: im realen Qt-Rendering plausibel",
    "Reduced Motion: keine notwendige Information hängt von Bewegung ab",
    "Laienprofil: nächster Schritt, Dateiwirkung, Rückweg und Hilfe verständlich",
)


def build_target_report() -> dict[str, object]:
    automated = build_report()
    runtime = automated["runtime"]
    ready = bool(runtime["real_gui_run_possible_here"])
    return {
        "evidence": "I17 real target accessibility",
        "mode": "real-target-required",
        "automated_status": automated["automated_status"],
        "runtime_ready": ready,
        "runtime": runtime,
        "manual_gates": [
            {"gate": gate, "status": "OPEN"} for gate in MANUAL_GATES
        ],
        "screenshots": list(SCREENSHOTS),
        "overall_status": "OPEN",
        "note": (
            "I17 bleibt OPEN, bis die manuellen Gates auf einer echten "
            "PySide6-/Display-Session geprüft und dokumentiert wurden."
        ),
    }


def format_text(report: dict[str, object]) -> str:
    runtime = report["runtime"]
    lines = [
        "PROVOWARE I17 – realer Accessibility-Zielsystemlauf",
        "===================================================",
        f"Automatisierter Vertrag: {report['automated_status']}",
        f"PySide6: {'JA' if runtime['pyside6_available'] else 'NEIN'}",
        f"Display-Session: {'JA' if runtime['display_session_available'] else 'NEIN'}",
        f"Session-Typ: {runtime['session_type']}",
        f"Realer GUI-Lauf hier möglich: {'JA' if report['runtime_ready'] else 'NEIN'}",
        "",
        "Manuelle Gates – alle starten OPEN:",
    ]
    for item in report["manual_gates"]:
        lines.append(f" - OPEN {item['gate']}")
    lines.extend(["", "Erforderliche Screenshots:"])
    for name in report["screenshots"]:
        lines.append(f" - {name}")
    lines.extend(
        [
            "",
            "README-Regel:",
            "Nur echte Zielsystem-Screenshots als Produktabbildung verwenden.",
            "Mockups müssen ausdrücklich als Entwurf gekennzeichnet bleiben.",
            "",
            str(report["note"]),
        ]
    )
    return "\n".join(lines)


def launch_gui() -> int:
    return subprocess.run(
        [sys.executable, str(ROOT / "start.py"), "--gui"],
        cwd=ROOT,
        check=False,
    ).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--launch-gui",
        action="store_true",
        help="Nach der Vorprüfung die echte PySide6-Shell starten.",
    )
    args = parser.parse_args(argv)

    report = build_target_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_text(report))

    if not report["runtime_ready"]:
        return 3

    if args.launch_gui:
        print("\n--- GUI-Lauf startet; danach bleiben die manuellen Gates zu dokumentieren. ---")
        return launch_gui()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
