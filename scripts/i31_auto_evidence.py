#!/usr/bin/env python3
"""Automated I31 GUI/CLI export evidence using only synthetic temporary data."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from provoware_laientool.diagnostic_export_adapter import (  # noqa: E402
    CANCELLED,
    PASS,
    run_cli_export_evidence_flow,
)
from provoware_laientool.diagnostic_export_gui import create_export_evidence_window  # noqa: E402
from provoware_laientool.diagnostics import DiagnosticEntry, DiagnosticReport  # noqa: E402

SCALES = (100, 150, 200)


def synthetic_report() -> DiagnosticReport:
    return DiagnosticReport(
        schema_version="1",
        collection_status="PASS",
        health_status="PASS",
        entries=(
            DiagnosticEntry("test", "quelle", "synthetische I31 Evidence"),
            DiagnosticEntry("test", "unicode", "Größe äöü"),
        ),
        warnings=(),
        redaction_applied=True,
        write_paths_enabled=False,
    )


def current_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def create_evidence_dir() -> Path:
    base = Path.home() / ".local" / "share" / "provoware-laientool" / "evidence"
    base.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    path = base / f"i31-{stamp}"
    suffix = 1
    while path.exists():
        path = base / f"i31-{stamp}-{suffix}"
        suffix += 1
    path.mkdir()
    return path


def save_png(widget, path: Path) -> bool:
    return bool(widget.grab().save(str(path), "PNG"))


def visible_geometry_ok(widget) -> bool:
    size = widget.size()
    return widget.isVisible() and size.width() > 0 and size.height() > 0


def run_cli_checks(report: DiagnosticReport, base: Path) -> dict[str, object]:
    success_dir = base / "cli-success"
    success_dir.mkdir()
    outputs: list[str] = []
    answers = iter(("2", "1", "1"))
    status = run_cli_export_evidence_flow(
        report,
        target_dir=success_dir,
        input_fn=lambda _: next(answers),
        output_fn=outputs.append,
    )
    created = list(success_dir.glob("PROVOWARE-Diagnose-I31.*"))

    cancel_dir = base / "cli-cancel"
    cancel_dir.mkdir()
    cancel_output: list[str] = []
    cancel_answers = iter(("1", "0"))
    cancel_status = run_cli_export_evidence_flow(
        report,
        target_dir=cancel_dir,
        input_fn=lambda _: next(cancel_answers),
        output_fn=cancel_output.append,
    )

    failures: list[str] = []
    if status != PASS:
        failures.append(f"CLI PASS-Pfad: {status}")
    if len(created) != 1:
        failures.append(f"CLI PASS-Pfad erzeugte {len(created)} statt exakt 1 Datei.")
    if cancel_status != CANCELLED:
        failures.append(f"CLI Cancel-Pfad: {cancel_status}")
    if list(cancel_dir.iterdir()):
        failures.append("CLI Cancel-Pfad erzeugte eine Datei.")
    joined = "\n".join(outputs)
    for marker in (
        "Weiter zur finalen Bestätigung",
        "Diagnosedatei jetzt neu erstellen",
        "Bestehende Dateien werden nicht überschrieben",
        "Diagnosedatei erstellt",
    ):
        if marker not in joined:
            failures.append(f"CLI-Ausgabe fehlt: {marker}")

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "success_output": outputs,
        "cancel_output": cancel_output,
        "created_files": [str(path.name) for path in created],
    }


def run_gui_checks(report: DiagnosticReport, base: Path, evidence_dir: Path) -> dict[str, object]:
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    app = None
    failures: list[str] = []
    scale_results: list[dict[str, object]] = []

    for scale in SCALES:
        target = base / f"gui-scale-{scale}"
        target.mkdir()
        app, window = create_export_evidence_window(report, target_dir=target)
        window.set_scale_percent(scale)
        window.resize(1280, 900)
        window.show()
        app.processEvents()

        local: list[str] = []
        for widget in window.core_widgets():
            if not visible_geometry_ok(widget):
                local.append(f"{scale} %: unsichtbares/ungültiges Kernwidget.")

        window.preview_button.setFocus(Qt.FocusReason.TabFocusReason)
        app.processEvents()
        if app.focusWidget() is not window.preview_button:
            local.append(f"{scale} %: Vorschau-Button erhält keinen Fokus.")
        else:
            QTest.keyClick(window.preview_button, Qt.Key.Key_Tab)
            app.processEvents()
            if app.focusWidget() is window.preview_button:
                local.append(f"{scale} %: Tab bewegt den Fokus nicht.")

        window.prepare_preview()
        app.processEvents()
        if not window.stage1_button.isEnabled():
            local.append(f"{scale} %: erste Bestätigung wird nach Preview nicht freigegeben.")
        window.confirm_stage1()
        app.processEvents()
        if not window.commit_button.isEnabled():
            local.append(f"{scale} %: finale Bestätigung wird nach Stage 1 nicht freigegeben.")
        if app.focusWidget() is window.commit_button:
            local.append(f"{scale} %: Schreibbutton besitzt unerlaubten Default-Fokus.")

        shot = evidence_dir / f"i31-{scale}-final-confirmation.png"
        if not save_png(window, shot):
            local.append(f"{scale} %: Screenshot fehlgeschlagen.")
        window.close()
        app.processEvents()

        scale_results.append(
            {"scale_percent": scale, "status": "PASS" if not local else "FAIL", "failures": local}
        )
        failures.extend(local)

    cancel_dir = base / "gui-cancel"
    cancel_dir.mkdir()
    app, cancel_window = create_export_evidence_window(report, target_dir=cancel_dir)
    cancel_window.show()
    cancel_window.prepare_preview()
    cancel_window.confirm_stage1()
    cancel_window.cancel_flow()
    app.processEvents()
    if cancel_window.last_status != CANCELLED:
        failures.append(f"GUI Cancel-Status: {cancel_window.last_status}")
    if list(cancel_dir.iterdir()):
        failures.append("GUI Cancel erzeugte eine Datei.")
    cancel_window.close()

    pass_dir = base / "gui-pass"
    pass_dir.mkdir()
    app, pass_window = create_export_evidence_window(report, target_dir=pass_dir)
    pass_window.show()
    pass_window.prepare_preview()
    pass_window.confirm_stage1()
    pass_window.commit_stage2()
    app.processEvents()
    created = list(pass_dir.glob("PROVOWARE-Diagnose-I31.*"))
    if pass_window.last_status != PASS:
        failures.append(f"GUI PASS-Status: {pass_window.last_status}")
    if len(created) != 1:
        failures.append(f"GUI PASS erzeugte {len(created)} statt exakt 1 Datei.")
    if "Was ist passiert?" not in pass_window.output.toPlainText():
        failures.append("GUI Erfolgsausgabe folgt nicht dem Laientextvertrag.")
    save_png(pass_window, evidence_dir / "i31-pass-result.png")
    pass_window.close()

    failure_dir = base / "gui-failure"
    failure_dir.mkdir()
    existing = failure_dir / "PROVOWARE-Diagnose-I31.txt"
    existing.write_text("bestehend", encoding="utf-8")
    app, failure_window = create_export_evidence_window(report, target_dir=failure_dir)
    failure_window.show()
    failure_window.prepare_preview()
    app.processEvents()
    body = failure_window.output.toPlainText()
    if failure_window.stage1_button.isEnabled():
        failures.append("GUI Failure-Pfad bietet trotz Zielkonflikt Bestätigung 1 an.")
    for marker in ("Was ist passiert?", "Was bedeutet das?", "Was kann ich jetzt tun?"):
        if marker not in body:
            failures.append(f"GUI Failure-Ausgabe fehlt: {marker}")
    if existing.read_text(encoding="utf-8") != "bestehend":
        failures.append("Vorhandene Testdatei wurde verändert.")
    save_png(failure_window, evidence_dir / "i31-blocked-existing-target.png")
    failure_window.close()

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "scale_checks": scale_results,
        "pass_created_files": [path.name for path in created],
    }


def write_evidence(evidence_dir: Path, result: dict[str, object]) -> None:
    (evidence_dir / "i31-evidence.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    lines = [
        "PROVOWARE I31 AUTO EVIDENCE",
        f"Commit: {result['commit']}",
        f"Status: {result['status']}",
        f"CLI: {result['cli']['status']}",
        f"GUI: {result['gui']['status']}",
        "",
        "Failures:",
    ]
    failures = list(result["cli"]["failures"]) + list(result["gui"]["failures"])
    lines.extend(f"- {item}" for item in failures)
    if not failures:
        lines.append("- keine")
    (evidence_dir / "i31-evidence.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_human_gate(report: DiagnosticReport) -> int:
    from PySide6.QtWidgets import QMessageBox

    with tempfile.TemporaryDirectory(prefix="provoware-i31-human-") as temp:
        target = Path(temp) / "synthetischer-export"
        target.mkdir()
        app, window = create_export_evidence_window(report, target_dir=target)
        window.show()
        app.exec()

        answer = QMessageBox.question(
            None,
            "I31 – finale Gesamtabnahme",
            (
                "War jederzeit klar, dass nur synthetische Testdaten verwendet werden, "
                "wann tatsächlich eine Datei erstellt wird, wo sie landet und wie du vorher sicher abbrichst?"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return 0 if answer == QMessageBox.StandardButton.Yes else 2


def run_cli_demo(report: DiagnosticReport) -> int:
    with tempfile.TemporaryDirectory(prefix="provoware-i31-cli-") as temp:
        target = Path(temp) / "synthetischer-export"
        target.mkdir()
        status = run_cli_export_evidence_flow(report, target_dir=target)
        print(f"\nPrüfmodus beendet: {status}")
        print("Der temporäre Testordner wird anschließend entfernt.")
        return 0 if status in {PASS, CANCELLED} else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offscreen", action="store_true")
    parser.add_argument("--auto-only", action="store_true")
    parser.add_argument("--cli-demo", action="store_true")
    args = parser.parse_args(argv)

    if args.offscreen:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    report = synthetic_report()
    if args.cli_demo:
        return run_cli_demo(report)

    evidence_dir = create_evidence_dir()
    with tempfile.TemporaryDirectory(prefix="provoware-i31-auto-") as temp:
        base = Path(temp)
        cli = run_cli_checks(report, base)
        gui = run_gui_checks(report, base, evidence_dir)

    result = {
        "schema_version": "1",
        "iteration": "I31",
        "commit": current_commit(),
        "synthetic_data_only": True,
        "cli": cli,
        "gui": gui,
        "status": "PASS" if cli["status"] == "PASS" and gui["status"] == "PASS" else "FAIL",
    }
    write_evidence(evidence_dir, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Evidence: {evidence_dir}")

    if result["status"] != "PASS":
        return 1
    if args.auto_only:
        return 0
    return run_human_gate(report)


if __name__ == "__main__":
    raise SystemExit(main())
