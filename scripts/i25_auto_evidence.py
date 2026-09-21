#!/usr/bin/env python3
"""Automated I25 Qt evidence with exactly one optional final human gate."""

from __future__ import annotations

import argparse
import html
import json
import os
import platform
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from provoware_laientool.application_core import (  # noqa: E402
    execute,
    prepare_inventory_view,
    prepare_target_directories,
)
from provoware_laientool.inventory_view import InventoryViewSpec, SORT_NAME_ASC  # noqa: E402

SCALES = (100, 150, 200)
SCREENSHOTS = {scale: f"i25-{scale}-overview.png" for scale in SCALES}
FOCUS_SCREENSHOT = "i25-keyboard-focus.png"
FILE_DIALOG_SCREENSHOT = "i25-file-selection.png"
TARGET_DIALOG_SCREENSHOT = "i25-target-selection.png"
PREVIEW_SCREENSHOT = "i25-transfer-preview.png"
HUMAN_TIMEOUT_SECONDS = 600


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
    path = base / f"i25-{stamp}"
    suffix = 1
    while path.exists():
        path = base / f"i25-{stamp}-{suffix}"
        suffix += 1
    path.mkdir()
    return path


def create_fixtures(base: Path) -> dict[str, Path]:
    fixture = base / "synthetic"
    root = fixture / "Downloads"
    source = root / "Eingang"
    target = root / "Ziel"
    nested = target / "Unter Ziel"
    outside = fixture / "Extern"
    source.mkdir(parents=True)
    nested.mkdir(parents=True)
    outside.mkdir()
    (source / "Datei mit Leerzeichen.txt").write_text("eins", encoding="utf-8")
    (source / "Grüße-äöü.txt").write_text("zwei", encoding="utf-8")
    try:
        (root / "Extern-Link").symlink_to(outside, target_is_directory=True)
    except OSError:
        pass
    return {"root": root, "source": source, "target": target, "outside": outside}


def save_png(widget, path: Path) -> bool:
    pixmap = widget.grab()
    return bool(pixmap.save(str(path), "PNG"))


def visible_geometry_ok(widget) -> bool:
    size = widget.size()
    return widget.isVisible() and size.width() > 0 and size.height() > 0


def run_scale_checks(app, window, evidence_dir: Path) -> list[dict[str, object]]:
    results = []
    for scale in SCALES:
        failures: list[str] = []
        window.set_scale_percent(scale)
        window.resize(1280, 900)
        window.show()
        app.processEvents()
        for widget in window.core_widgets():
            if not visible_geometry_ok(widget):
                failures.append(f"Widget nicht sichtbar/benutzbar: {widget.objectName() or widget.__class__.__name__}")
        screenshot = evidence_dir / SCREENSHOTS[scale]
        if not save_png(window, screenshot):
            failures.append("Screenshot konnte nicht gespeichert werden.")
        results.append(
            {
                "scale_percent": scale,
                "status": "PASS" if not failures else "FAIL",
                "failures": failures,
                "screenshot": screenshot.name,
            }
        )
    return results


def run_focus_check(app, window, evidence_dir: Path) -> dict[str, object]:
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    failures: list[str] = []
    widgets = list(window.keyboard_focus_widgets())
    expected = [widget.accessibleName() or widget.text() if hasattr(widget, "text") else widget.objectName() for widget in widgets]
    widgets[0].setFocus(Qt.FocusReason.TabFocusReason)
    app.processEvents()
    seen = []
    for _ in range(len(widgets)):
        current = app.focusWidget()
        seen.append(current)
        QTest.keyClick(current, Qt.Key.Key_Tab)
        app.processEvents()
    if seen != widgets:
        failures.append("Tab-Reihenfolge entspricht nicht dem definierten Fokusvertrag.")

    widgets[-1].setFocus(Qt.FocusReason.TabFocusReason)
    app.processEvents()
    backward = []
    for _ in range(len(widgets)):
        current = app.focusWidget()
        backward.append(current)
        QTest.keyClick(current, Qt.Key.Key_Tab, Qt.KeyboardModifier.ShiftModifier)
        app.processEvents()
    if backward != list(reversed(widgets)):
        failures.append("Shift+Tab-Reihenfolge entspricht nicht dem definierten Fokusvertrag.")

    widgets[2].setFocus(Qt.FocusReason.TabFocusReason)
    app.processEvents()
    screenshot = evidence_dir / FOCUS_SCREENSHOT
    if not save_png(window, screenshot):
        failures.append("Fokus-Screenshot konnte nicht gespeichert werden.")
    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "focus_count": len(widgets),
        "screenshot": screenshot.name,
    }


def run_workflow_check(app, window, fixtures: dict[str, Path], evidence_dir: Path) -> dict[str, object]:
    from PySide6.QtWidgets import QAbstractItemView

    failures: list[str] = []
    root = fixtures["root"]
    preparation = prepare_inventory_view(
        root,
        InventoryViewSpec(sort=SORT_NAME_ASC, limit=100),
    )
    if preparation.status != "PASS" or preparation.view is None:
        failures.append(f"Inventarvorbereitung: {preparation.status}")
        return {"status": "FAIL", "failures": failures}

    file_dialog, file_list = window.build_file_selection_dialog(preparation)
    file_dialog.show()
    app.processEvents()
    if file_list.selectionMode() != QAbstractItemView.ExtendedSelection:
        failures.append("Dateiauswahl ist nicht als Mehrfachauswahl konfiguriert.")
    if file_list.count() != 2:
        failures.append(f"Erwartet 2 synthetische Dateien, gefunden {file_list.count()}.")
    file_list.setCurrentRow(0)
    file_list.item(1).setSelected(True)
    app.processEvents()
    file_shot = evidence_dir / FILE_DIALOG_SCREENSHOT
    if not save_png(file_dialog, file_shot):
        failures.append("Dateiauswahl-Screenshot fehlgeschlagen.")
    file_dialog.close()

    target_dialog, target_list, targets = window.build_target_selection_dialog(root)
    if target_dialog is None or target_list is None or targets.status != "PASS":
        failures.append(f"Zielwahlliste nicht vollständig: {targets.status}")
    else:
        expected = (".", "Eingang", "Ziel", "Ziel/Unter Ziel")
        if targets.directories != expected:
            failures.append(f"Same-Root-Zielliste abweichend: {targets.directories!r}")
        if any("Extern-Link" in value for value in targets.directories):
            failures.append("Symlink-Ziel wurde auswählbar angeboten.")
        target_dialog.show()
        target_list.setCurrentRow(targets.directories.index("Ziel"))
        app.processEvents()
        target_shot = evidence_dir / TARGET_DIALOG_SCREENSHOT
        if not save_png(target_dialog, target_shot):
            failures.append("Zielauswahl-Screenshot fehlgeschlagen.")
        target_dialog.close()

    selected = ("Eingang/Datei mit Leerzeichen.txt", "Eingang/Grüße-äöü.txt")
    target = str(fixtures["target"])
    for use_case_id in ("files.preview_copy", "files.preview_move"):
        result = execute(
            use_case_id,
            root=str(root),
            selected_relative_paths=selected,
            target_dir=target,
        )
        if result.status != "PASS":
            failures.append(f"{use_case_id}: {result.status}")
        if "Es wurden keine Dateien verändert" not in result.body:
            failures.append(f"{use_case_id}: Sicherheitsbestätigung fehlt.")

    blocked = execute(
        "files.preview_copy",
        root=str(root),
        selected_relative_paths=(selected[0],),
        target_dir=str(fixtures["outside"]),
    )
    if blocked.status != "BLOCKED":
        failures.append("Externer Zielpfad wird im Core nicht BLOCKED.")

    window.show_transfer_preview_for_paths(
        "files.preview_copy",
        str(root),
        selected,
        target,
    )
    app.processEvents()
    preview_text = window.output.toPlainText()
    for fragment in ("Reine Vorschau", "Dateien: 2", "Zielordner", "Es wurden keine Dateien verändert"):
        if fragment not in preview_text:
            failures.append(f"Preview-Ausgabe fehlt: {fragment}")
    preview_shot = evidence_dir / PREVIEW_SCREENSHOT
    if not save_png(window, preview_shot):
        failures.append("Preview-Screenshot fehlgeschlagen.")

    if any((fixtures["target"] / name).exists() for name in ("Datei mit Leerzeichen.txt", "Grüße-äöü.txt")):
        failures.append("Transfer-Preview hat unerwartet Zieldateien erzeugt.")
    if not all((fixtures["source"] / name).is_file() for name in ("Datei mit Leerzeichen.txt", "Grüße-äöü.txt")):
        failures.append("Quelldateien wurden verändert.")

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "file_screenshot": FILE_DIALOG_SCREENSHOT,
        "target_screenshot": TARGET_DIALOG_SCREENSHOT,
        "preview_screenshot": PREVIEW_SCREENSHOT,
    }


def technical_status(report: dict[str, object]) -> str:
    checks = [*report["scale_checks"], report["focus_check"], report["workflow_check"]]
    return "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"


def overall_status(technical: str, human: str) -> str:
    if technical == "FAIL" or human == "FAIL":
        return "FAIL"
    if technical == "PASS" and human == "PASS":
        return "PASS"
    return "OPEN"


def render_text(report: dict[str, object]) -> str:
    lines = [
        "PROVOWARE I25 – Automated Transfer Preview Evidence",
        "==================================================",
        f"Commit: {report['commit']}",
        f"Qt-Modus: {report['qt_platform']}",
    ]
    for item in report["scale_checks"]:
        lines.append(f"{item['status']} · {item['scale_percent']} %")
        lines.extend(f"  ! {failure}" for failure in item["failures"])
    for label, item in (
        ("Tab/Shift+Tab/Fokus", report["focus_check"]),
        ("Transfer-Workflow", report["workflow_check"]),
    ):
        lines.append(f"{item['status']} · {label}")
        lines.extend(f"  ! {failure}" for failure in item["failures"])
    lines += [
        "",
        f"I25-AUTO: {report['technical_status']}",
        f"I25-HUMAN: {report['human_status']}",
        f"GESAMT: {report['overall_status']}",
    ]
    return "\n".join(lines) + "\n"


def render_html(report: dict[str, object], action: str | None = None) -> str:
    def badge(value: str) -> str:
        css = {"PASS": "pass", "FAIL": "fail", "OPEN": "open"}.get(value, "open")
        return f'<span class="badge {css}">{html.escape(value)}</span>'

    rows = []
    for item in report["scale_checks"]:
        details = "<br>".join(html.escape(x) for x in item["failures"]) or "keine Befunde"
        rows.append(f"<tr><td>{item['scale_percent']} % Layout</td><td>{badge(item['status'])}</td><td>{details}</td></tr>")
    for label, item in (("Tab / Shift+Tab / Fokus", report["focus_check"]), ("Transfer-Workflow", report["workflow_check"])):
        details = "<br>".join(html.escape(x) for x in item["failures"]) or "keine Befunde"
        rows.append(f"<tr><td>{html.escape(label)}</td><td>{badge(item['status'])}</td><td>{details}</td></tr>")

    image_names = [
        *[SCREENSHOTS[scale] for scale in SCALES],
        FOCUS_SCREENSHOT,
        FILE_DIALOG_SCREENSHOT,
        TARGET_DIALOG_SCREENSHOT,
        PREVIEW_SCREENSHOT,
    ]
    images = "".join(
        f"<figure><img src='/{html.escape(name)}'><figcaption>{html.escape(name)}</figcaption></figure>"
        for name in image_names
        if (Path(report["evidence_dir"]) / name).is_file()
    )
    human = ""
    if action and report["technical_status"] == "PASS":
        human = (
            "<section><h2>Nur noch eine menschliche Frage</h2>"
            "<p>Ist der komplette Copy-/Move-Vorschau-Workflow insgesamt verständlich, ruhig und ohne zusätzliche Erklärung bedienbar?</p>"
            f"<form method='post' action='{html.escape(action)}'>"
            "<button class='yes' name='answer' value='PASS'>Ja · PASS</button>"
            "<button class='no' name='answer' value='FAIL'>Nein · FAIL</button>"
            "<button class='maybe' name='answer' value='OPEN'>Unsicher · OPEN</button>"
            "</form></section>"
        )
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PROVOWARE I25 Evidence</title><style>
body{{font-family:system-ui,sans-serif;max-width:1250px;margin:auto;padding:28px;background:#101218;color:#f4f7fb;font-size:18px}}
section{{background:#191d27;border:1px solid #414b62;border-radius:16px;padding:20px;margin:16px 0}}
.badge{{font-weight:800;padding:5px 10px;border-radius:999px}} .pass{{background:#173c29;color:#a9ffd0}} .fail{{background:#4b1f24;color:#ffd0d4}} .open{{background:#493d16;color:#ffeaa0}}
table{{width:100%;border-collapse:collapse}} th,td{{text-align:left;padding:11px;border-bottom:1px solid #343a42}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}} img{{width:100%;border:1px solid #56617a;border-radius:10px}}
button{{font-size:1.15rem;font-weight:800;padding:15px 22px;margin:7px;border:0;border-radius:10px;color:white}} .yes{{background:#2c8b57}} .no{{background:#a83d49}} .maybe{{background:#9a7b23}}
</style></head><body><h1>PROVOWARE I25 – automatische Evidence</h1>
<section><p><strong>Commit:</strong> {html.escape(str(report['commit']))}<br><strong>Plattform:</strong> {html.escape(str(report['platform']))}</p>
<p>I25-AUTO {badge(str(report['technical_status']))} &nbsp; I25-HUMAN {badge(str(report['human_status']))} &nbsp; GESAMT {badge(str(report['overall_status']))}</p></section>
<section><h2>Automatische Prüfungen</h2><table><tr><th>Gate</th><th>Status</th><th>Befund</th></tr>{''.join(rows)}</table></section>
<section><h2>Automatisch erzeugte Screenshots</h2><div class="gallery">{images}</div></section>{human}</body></html>"""


def write_reports(report: dict[str, object], root: Path) -> None:
    report["evidence_dir"] = str(root)
    (root / "I25_EVIDENCE.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (root / "I25_AUSWERTUNG.txt").write_text(render_text(report), encoding="utf-8")
    (root / "I25_REPORT.html").write_text(render_html(report), encoding="utf-8")


def chromium_binary() -> str | None:
    for candidate in ("chromium", "chromium-browser"):
        if shutil.which(candidate):
            return candidate
    return None


def chromium_human_gate(report: dict[str, object], root: Path) -> str:
    browser = chromium_binary()
    if browser is None:
        return "OPEN"
    done = threading.Event()
    answer = {"value": "OPEN"}
    token = secrets.token_urlsafe(24)
    safe_root = root.resolve()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:
            return
        def send_bytes(self, status: int, content_type: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def do_GET(self) -> None:
            if self.path == "/":
                self.send_bytes(200, "text/html; charset=utf-8", render_html(report, f"/human?token={token}").encode("utf-8"))
                return
            name = self.path.lstrip("/")
            path = safe_root / name
            if "/" in name or not name.endswith(".png") or path.parent != safe_root or not path.is_file():
                self.send_bytes(404, "text/plain; charset=utf-8", b"Not found")
                return
            self.send_bytes(200, "image/png", path.read_bytes())
        def do_POST(self) -> None:
            if self.path != f"/human?token={token}":
                self.send_bytes(403, "text/plain; charset=utf-8", b"Forbidden")
                return
            length = min(int(self.headers.get("Content-Length", "0")), 1024)
            values = parse_qs(self.rfile.read(length).decode("utf-8", errors="replace"))
            value = values.get("answer", ["OPEN"])[0]
            if value not in {"PASS", "FAIL", "OPEN"}:
                value = "OPEN"
            answer["value"] = value
            report["human_status"] = value
            report["overall_status"] = overall_status(str(report["technical_status"]), value)
            write_reports(report, root)
            self.send_bytes(200, "text/html; charset=utf-8", render_html(report).encode("utf-8"))
            done.set()

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/"
    try:
        subprocess.Popen([browser, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"🌐 Chromium: {url}")
        done.wait(HUMAN_TIMEOUT_SECONDS)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    return answer["value"]


def run_pipeline(*, offscreen: bool = False, auto_only: bool = False) -> int:
    if offscreen:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from provoware_laientool.gui_shell import create_main_window

    try:
        app, window = create_main_window(evidence_mode=True)
    except RuntimeError as exc:
        print(f"🔴 {exc}")
        return 3

    root = create_evidence_dir()
    fixtures = create_fixtures(root)
    window.show()
    app.processEvents()
    report: dict[str, object] = {
        "evidence": "I25 automated transfer preview",
        "commit": current_commit(),
        "captured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "qt_platform": app.platformName(),
        "evidence_dir": str(root),
        "scale_checks": run_scale_checks(app, window, root),
        "focus_check": run_focus_check(app, window, root),
        "workflow_check": run_workflow_check(app, window, fixtures, root),
        "human_status": "OPEN",
    }
    report["technical_status"] = technical_status(report)
    report["overall_status"] = overall_status(str(report["technical_status"]), "OPEN")
    write_reports(report, root)
    window.close()
    app.processEvents()

    if report["technical_status"] == "PASS" and not auto_only and not offscreen:
        report["human_status"] = chromium_human_gate(report, root)
        report["overall_status"] = overall_status(str(report["technical_status"]), str(report["human_status"]))
        write_reports(report, root)

    print(render_text(report), end="")
    print(f"Evidence-Ordner: {root}")
    if report["overall_status"] == "PASS":
        return 0
    if report["technical_status"] == "FAIL":
        return 2
    return 5


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offscreen", action="store_true")
    parser.add_argument("--auto-only", action="store_true")
    args = parser.parse_args(argv)
    return run_pipeline(offscreen=args.offscreen, auto_only=args.auto_only)


if __name__ == "__main__":
    raise SystemExit(main())
