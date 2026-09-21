#!/usr/bin/env python3
"""Guided I17 target-system accessibility evidence helper.

The helper keeps automated checks separate from human visual evidence. Guided
mode creates only a dedicated local evidence directory and synthetic fixtures;
it never writes through the product core and never changes selected user data.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

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
    "Screenshots: keine unnötigen privaten Pfade oder Dateinamen sichtbar",
)

GATE_HELP = {
    MANUAL_GATES[0]: "Stelle 100 % ein. Prüfe Lesbarkeit, Lese-Modus und alle Kernaktionen.",
    MANUAL_GATES[1]: "Stelle 150 % ein. Prüfe erneut Lesbarkeit und abgeschnittene Bedienelemente.",
    MANUAL_GATES[2]: "Stelle 200 % ein. Prüfe Navigation, Vorschau und alle notwendigen Buttons.",
    MANUAL_GATES[3]: "Benutze nur Tab und Shift+Tab. Alle READY-Funktionen müssen erreichbar sein.",
    MANUAL_GATES[4]: "Beobachte den Fokusrahmen. Der aktuelle Fokus muss jederzeit erkennbar sein.",
    MANUAL_GATES[5]: "Teste Abbruch, leeren Ordner und den vorbereiteten Unicode-Testordner.",
    MANUAL_GATES[6]: "Prüfe Text, Fokus und wichtige Zustände in der echten Desktop-Darstellung.",
    MANUAL_GATES[7]: "Keine notwendige Information darf nur durch Animation/Bewegung vermittelt werden.",
    MANUAL_GATES[8]: "Nächster Schritt, Dateiwirkung, Rückweg und Hilfe müssen verständlich sein.",
    MANUAL_GATES[9]: "Kontrolliere die fünf Screenshots vor der Ablage auf private Informationen.",
}

MAX_INPUT_ATTEMPTS = 3


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
        "manual_gates": [{"gate": gate, "status": "OPEN"} for gate in MANUAL_GATES],
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
        "Manuelle Gates:",
    ]
    for item in report["manual_gates"]:
        lines.append(f" - {item['status']} {item['gate']}")
    lines.extend(["", "Erforderliche Screenshots:"])
    screenshot_state = report.get("screenshot_state", {})
    for name in report["screenshots"]:
        state = "VORHANDEN" if screenshot_state.get(name, False) else "FEHLT"
        lines.append(f" - {state} {name}")
    if report.get("guided"):
        lines.extend(
            [
                "",
                f"Commit/Fingerprint: {report.get('commit', 'unknown')}",
                f"Erfasst: {report.get('captured_at', 'unknown')}",
                f"Plattform: {report.get('platform', 'unknown')}",
                f"GUI-Prozess gestartet: {'JA' if report.get('gui_started') else 'NEIN'}",
            ]
        )
    lines.extend(["", f"GESAMT: {report['overall_status']}", "", str(report["note"])])
    return "\n".join(lines)


def current_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    value = completed.stdout.strip()
    return value if completed.returncode == 0 and value else "unknown"


def create_evidence_dir(base: Path | None = None) -> Path:
    root = base or (Path.home() / "PROVOWARE-I17-Evidence")
    root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    for counter in range(100):
        suffix = "" if counter == 0 else f"-{counter:02d}"
        candidate = root / f"I17-{stamp}{suffix}"
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            continue
    raise RuntimeError("Kein eindeutiger Evidence-Ordner nach 100 Versuchen verfügbar.")


def create_preview_fixtures(evidence_dir: Path) -> dict[str, Path]:
    empty_dir = evidence_dir / "test-leer"
    sample_dir = evidence_dir / "test-vorschau-unicode"
    empty_dir.mkdir()
    sample_dir.mkdir()
    (sample_dir / "Datei mit Leerzeichen.txt").write_text(
        "PROVOWARE I17 Testdatei – nur synthetische Evidence.\n",
        encoding="utf-8",
    )
    (sample_dir / "Grüße-äöü.txt").write_text(
        "Unicode-Test – keine Nutzdaten.\n",
        encoding="utf-8",
    )
    return {"empty": empty_dir, "sample": sample_dir}


def launch_gui() -> subprocess.Popen[bytes] | None:
    try:
        return subprocess.Popen(
            [sys.executable, str(ROOT / "start.py"), "--gui"],
            cwd=ROOT,
        )
    except OSError:
        return None


def open_desktop(path: Path) -> bool:
    candidates = (
        ("xdg-open", str(path)),
        ("gio", "open", str(path)),
        ("kde-open5", str(path)),
    )
    for command in candidates:
        if shutil.which(command[0]) is None:
            continue
        try:
            subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except OSError:
            continue
    return False


def ask_gate(
    gate: str,
    input_fn: Callable[[str], str] = input,
) -> str:
    print("\n" + "─" * 72)
    print(f"PRÜFUNG: {gate}")
    print(GATE_HELP[gate])
    print("Antwort: [J]a  [N]ein  [O]ffen/unsicher  [A]bbrechen")
    for _ in range(MAX_INPUT_ATTEMPTS):
        try:
            answer = input_fn("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return "ABORT"
        if answer in {"j", "ja", "y", "yes"}:
            return "PASS"
        if answer in {"n", "nein", "no"}:
            return "FAIL"
        if answer in {"o", "offen", "unsicher", "u"}:
            return "OPEN"
        if answer in {"a", "abbrechen", "abort", "q", "quit"}:
            return "ABORT"
        print("Bitte J, N, O oder A eingeben.")
    print("Zu viele ungültige Eingaben – dieser Punkt bleibt OPEN.")
    return "OPEN"


def screenshot_state(evidence_dir: Path) -> dict[str, bool]:
    return {name: (evidence_dir / name).is_file() for name in SCREENSHOTS}


def overall_status(
    automated_status: str,
    runtime_ready: bool,
    manual_statuses: list[str],
    screenshots: dict[str, bool],
) -> str:
    if automated_status == "FAIL" or "FAIL" in manual_statuses:
        return "FAIL"
    if not runtime_ready:
        return "OPEN"
    if any(status != "PASS" for status in manual_statuses):
        return "OPEN"
    if not all(screenshots.values()):
        return "OPEN"
    return "PASS"


def write_guided_report(report: dict[str, object], evidence_dir: Path) -> tuple[Path, Path]:
    json_path = evidence_dir / "I17_EVIDENCE.json"
    text_path = evidence_dir / "I17_AUSWERTUNG.txt"
    payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    json_path.write_text(payload, encoding="utf-8")
    text_path.write_text(format_text(report) + "\n", encoding="utf-8")
    return text_path, json_path


def guided_run(no_open: bool = False, evidence_base: Path | None = None) -> int:
    report = build_target_report()
    print(format_text(report))
    if report["automated_status"] == "FAIL":
        print("\n🔴 Automatisierter Vertrag ist fehlgeschlagen. Kein GUI-Evidence-Lauf.")
        return 2
    if not report["runtime_ready"]:
        print("\n🟨 Keine echte PySide6-/Display-Session verfügbar. I17 bleibt OPEN.")
        return 3

    evidence_dir = create_evidence_dir(evidence_base)
    fixtures = create_preview_fixtures(evidence_dir)
    print("\n🟢 Sicherer lokaler Evidence-Ordner wurde neu angelegt:")
    print(f"   {evidence_dir}")
    print("Es werden dort nur I17-Nachweise und synthetische Testdateien erzeugt.")
    print("\nFür die Dateivorschau:")
    print(f" - leerer Ordner: {fixtures['empty']}")
    print(f" - Unicode/Leerzeichen: {fixtures['sample']}")
    print("\nSpeichere Screenshots mit exakt diesen Namen in den Evidence-Ordner:")
    for name in SCREENSHOTS:
        print(f" - {name}")

    if not no_open:
        open_desktop(evidence_dir)

    gui_process = launch_gui()
    if gui_process is None:
        print("\n🔴 GUI konnte nicht gestartet werden. I17 bleibt OPEN.")
        return 4

    print("\n🟢 GUI gestartet. Arbeite die folgenden Prüfungen der Reihe nach ab.")
    statuses: list[str] = []
    items: list[dict[str, str]] = []
    aborted = False
    for gate in MANUAL_GATES:
        if aborted:
            status = "OPEN"
        else:
            status = ask_gate(gate)
            if status == "ABORT":
                aborted = True
        statuses.append(status)
        items.append({"gate": gate, "status": status})

    shots = screenshot_state(evidence_dir)
    missing = [name for name, present in shots.items() if not present]
    if missing and not aborted:
        print("\n🟨 Noch fehlende Screenshots:")
        for name in missing:
            print(f" - {name}")
        print("Du kannst sie jetzt speichern. Danach einmal Enter drücken.")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass
        shots = screenshot_state(evidence_dir)

    report.update(
        {
            "guided": True,
            "captured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "commit": current_commit(),
            "platform": platform.platform(),
            "gui_started": True,
            "gui_running_at_finish": gui_process.poll() is None,
            "manual_gates": items,
            "screenshot_state": shots,
            "overall_status": overall_status(
                str(report["automated_status"]),
                bool(report["runtime_ready"]),
                statuses,
                shots,
            ),
            "note": (
                "PASS wird nur vergeben, wenn Automatik, echte Desktop-Session, "
                "alle manuellen Gates und alle fünf Screenshot-Dateien belegt sind. "
                "OPEN bedeutet: Nachweis unvollständig. FAIL bedeutet: mindestens "
                "ein technisches oder manuell bestätigtes Gate ist fehlgeschlagen."
            ),
        }
    )
    text_path, json_path = write_guided_report(report, evidence_dir)

    print("\n" + "=" * 72)
    print(f"I17-B Ergebnis: {report['overall_status']}")
    print(f"Auswertung: {text_path}")
    print(f"JSON-Evidence: {json_path}")
    if gui_process.poll() is None:
        print("Die GUI läuft noch und kann jetzt normal geschlossen werden.")
    if not no_open:
        open_desktop(text_path)

    return 0 if report["overall_status"] == "PASS" else 5


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--launch-gui",
        action="store_true",
        help="Nach der Vorprüfung die echte PySide6-Shell starten.",
    )
    parser.add_argument(
        "--guided",
        action="store_true",
        help="Geführter I17-B-Lauf mit manuellen Gates und lokaler Evidence.",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Ordner/Auswertung nicht automatisch im Desktop öffnen.",
    )
    parser.add_argument(
        "--evidence-base",
        type=Path,
        default=None,
        help="Optionaler Basisordner für geführte lokale Evidence.",
    )
    args = parser.parse_args(argv)

    if args.guided:
        return guided_run(no_open=args.no_open, evidence_base=args.evidence_base)

    report = build_target_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_text(report))

    if not report["runtime_ready"]:
        return 3

    if args.launch_gui:
        print("\n--- GUI-Lauf startet; danach bleiben die manuellen Gates zu dokumentieren. ---")
        process = launch_gui()
        if process is None:
            return 4
        return process.wait()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
