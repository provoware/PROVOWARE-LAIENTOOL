#!/usr/bin/env python3
"""Automated I17 Qt evidence with Chromium as the visible report surface."""

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
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

SCALES = (100, 150, 200)
SCREENSHOTS = {
    100: "i17-100-overview.png",
    150: "i17-150-overview.png",
    200: "i17-200-overview.png",
}
FOCUS_SCREENSHOT = "i17-keyboard-focus.png"
PREVIEW_SCREENSHOT = "i17-file-preview.png"
HUMAN_TIMEOUT_SECONDS = 600


def current_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else "unknown"


def create_evidence_dir(base: Path | None = None) -> Path:
    root = base or (Path.home() / "PROVOWARE-I17-Evidence")
    root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    for counter in range(100):
        suffix = "" if counter == 0 else f"-{counter:02d}"
        candidate = root / f"I17-AUTO-{stamp}{suffix}"
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            continue
    raise RuntimeError("Kein eindeutiger Evidence-Ordner verfügbar.")


def create_fixtures(root: Path) -> dict[str, Path]:
    empty_dir = root / "fixture-leer"
    sample_dir = root / "fixture-unicode leerzeichen"
    empty_dir.mkdir()
    sample_dir.mkdir()
    (sample_dir / "Datei mit Leerzeichen.txt").write_text(
        "PROVOWARE I17 synthetische Testdatei.\n", encoding="utf-8"
    )
    (sample_dir / "Grüße-äöü.txt").write_text(
        "Unicode-Test ohne Nutzdaten.\n", encoding="utf-8"
    )
    return {"empty": empty_dir, "sample": sample_dir}


def widget_label(widget) -> str:
    accessible = widget.accessibleName().strip()
    if accessible:
        return accessible
    text_method = getattr(widget, "text", None)
    if callable(text_method):
        text = str(text_method()).strip()
        if text:
            return text
    return widget.objectName() or widget.__class__.__name__


def geometry_failures(window, widget) -> list[str]:
    from PySide6.QtCore import QPoint, QRect

    if not widget.isVisible():
        return ["nicht sichtbar"]
    top_left = widget.mapTo(window, QPoint(0, 0))
    rect = QRect(top_left, widget.size())
    problems: list[str] = []
    if not window.rect().contains(rect):
        problems.append(
            f"außerhalb Fenster x={rect.x()} y={rect.y()} "
            f"w={rect.width()} h={rect.height()}"
        )
    minimum = widget.minimumSizeHint()
    if minimum.isValid() and widget.width() + 1 < minimum.width():
        problems.append(f"Breite {widget.width()} < Minimum {minimum.width()}")
    if minimum.isValid() and widget.height() + 1 < minimum.height():
        problems.append(f"Höhe {widget.height()} < Minimum {minimum.height()}")
    return problems


def save_png(window, path: Path) -> bool:
    return bool(window.grab().save(str(path), "PNG"))


def run_scale_checks(app, window, evidence_dir: Path) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for scale in SCALES:
        window.set_scale_percent(scale)
        app.processEvents()
        failures: list[str] = []
        for widget in window.core_widgets():
            failures.extend(
                f"{widget_label(widget)}: {problem}"
                for problem in geometry_failures(window, widget)
            )
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

    widgets = list(window.keyboard_focus_widgets())
    expected = [widget_label(widget) for widget in widgets]
    failures: list[str] = []

    widgets[0].setFocus(Qt.FocusReason.TabFocusReason)
    app.processEvents()
    forward = [widget_label(app.focusWidget()) if app.focusWidget() else "NONE"]
    for _ in range(len(widgets) - 1):
        QTest.keyClick(app.focusWidget(), Qt.Key.Key_Tab)
        app.processEvents()
        forward.append(widget_label(app.focusWidget()) if app.focusWidget() else "NONE")
    if forward != expected:
        failures.append(f"Tab erwartet={expected!r}; beobachtet={forward!r}")

    widgets[-1].setFocus(Qt.FocusReason.BacktabFocusReason)
    app.processEvents()
    backward = [widget_label(app.focusWidget()) if app.focusWidget() else "NONE"]
    for _ in range(len(widgets) - 1):
        QTest.keyClick(
            app.focusWidget(),
            Qt.Key.Key_Tab,
            Qt.KeyboardModifier.ShiftModifier,
        )
        app.processEvents()
        backward.append(widget_label(app.focusWidget()) if app.focusWidget() else "NONE")
    expected_backward = list(reversed(expected))
    if backward != expected_backward:
        failures.append(
            f"Shift+Tab erwartet={expected_backward!r}; beobachtet={backward!r}"
        )

    widgets[2].setFocus(Qt.FocusReason.TabFocusReason)
    app.processEvents()
    screenshot = evidence_dir / FOCUS_SCREENSHOT
    if not save_png(window, screenshot):
        failures.append("Fokus-Screenshot konnte nicht gespeichert werden.")

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "forward": forward,
        "backward": backward,
        "screenshot": screenshot.name,
    }


def run_preview_check(app, window, fixtures: dict[str, Path], evidence_dir: Path) -> dict[str, object]:
    failures: list[str] = []

    window.show_action_for_root("files.preview_trash", "")
    app.processEvents()
    if "kein Ordner ausgewählt" not in window.output.toPlainText():
        failures.append("Abbruch/keine Auswahl wird nicht sicher erklärt.")

    window.show_action_for_root("files.preview_trash", str(fixtures["empty"]))
    app.processEvents()
    if "keine regulären Dateien" not in window.output.toPlainText():
        failures.append("Leerer Ordner wird nicht verständlich erklärt.")

    window.show_action_for_root("files.preview_trash", str(fixtures["sample"]))
    app.processEvents()
    text = window.output.toPlainText()
    for fragment in (
        "Reine Vorschau",
        "Datei mit Leerzeichen.txt",
        "Grüße-äöü.txt",
        "Ein Executor ist weiterhin gesperrt",
    ):
        if fragment not in text:
            failures.append(f"Preview-Ausgabe fehlt: {fragment}")

    if len(list(fixtures["sample"].iterdir())) != 2:
        failures.append("Synthetische Fixture wurde unerwartet verändert.")

    screenshot = evidence_dir / PREVIEW_SCREENSHOT
    if not save_png(window, screenshot):
        failures.append("Preview-Screenshot konnte nicht gespeichert werden.")

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "screenshot": screenshot.name,
    }


def technical_status(report: dict[str, object]) -> str:
    items = [*report["scale_checks"], report["focus_check"], report["preview_check"]]
    return "PASS" if all(item["status"] == "PASS" for item in items) else "FAIL"


def overall_status(technical: str, human: str) -> str:
    if technical == "FAIL" or human == "FAIL":
        return "FAIL"
    if technical == "PASS" and human == "PASS":
        return "PASS"
    return "OPEN"


def render_text(report: dict[str, object]) -> str:
    lines = [
        "PROVOWARE I17-D – Automated Qt Evidence",
        "========================================",
        f"Commit: {report['commit']}",
        f"Qt-Modus: {report['qt_platform']}",
    ]
    for item in report["scale_checks"]:
        lines.append(f"{item['status']} · {item['scale_percent']} %")
        lines.extend(f"  ! {failure}" for failure in item["failures"])
    for label, item in (
        ("Tab/Shift+Tab/Fokus", report["focus_check"]),
        ("Dateivorschau", report["preview_check"]),
    ):
        lines.append(f"{item['status']} · {label}")
        lines.extend(f"  ! {failure}" for failure in item["failures"])
    lines.extend(
        [
            "",
            f"I17-AUTO: {report['technical_status']}",
            f"I17-HUMAN: {report['human_status']}",
            f"GESAMT: {report['overall_status']}",
        ]
    )
    return "\n".join(lines) + "\n"


def render_html(report: dict[str, object], action: str | None = None) -> str:
    def badge(value: str) -> str:
        css = {"PASS": "pass", "FAIL": "fail", "OPEN": "open"}.get(value, "open")
        return f'<span class="badge {css}">{html.escape(value)}</span>'

    rows: list[str] = []
    for item in report["scale_checks"]:
        detail = "<br>".join(html.escape(x) for x in item["failures"]) or "keine Befunde"
        rows.append(
            f"<tr><td>{item['scale_percent']} % Layout</td>"
            f"<td>{badge(item['status'])}</td><td>{detail}</td>"
            f"<td><a href='/{html.escape(item['screenshot'])}'>Screenshot</a></td></tr>"
        )
    for label, item in (
        ("Tab / Shift+Tab / Fokus", report["focus_check"]),
        ("Synthetische Dateivorschau", report["preview_check"]),
    ):
        detail = "<br>".join(html.escape(x) for x in item["failures"]) or "keine Befunde"
        rows.append(
            f"<tr><td>{html.escape(label)}</td><td>{badge(item['status'])}</td>"
            f"<td>{detail}</td><td><a href='/{html.escape(item['screenshot'])}'>Screenshot</a></td></tr>"
        )

    images = "".join(
        f"<figure><img src='/{html.escape(name)}'><figcaption>{html.escape(name)}</figcaption></figure>"
        for name in (
            SCREENSHOTS[100],
            SCREENSHOTS[150],
            SCREENSHOTS[200],
            FOCUS_SCREENSHOT,
            PREVIEW_SCREENSHOT,
        )
    )

    human = ""
    if action and report["technical_status"] == "PASS":
        human = (
            "<section><h2>Eine letzte menschliche Frage</h2>"
            "<p>Ist die Oberfläche insgesamt verständlich, ruhig und ohne zusätzliche "
            "Erklärung für einen Laien bedienbar?</p>"
            f"<form method='post' action='{html.escape(action)}'>"
            "<button class='yes' name='answer' value='PASS'>Ja · PASS</button>"
            "<button class='no' name='answer' value='FAIL'>Nein · FAIL</button>"
            "<button class='maybe' name='answer' value='OPEN'>Unsicher · OPEN</button>"
            "</form><p class='muted'>Nur lokal auf 127.0.0.1. Keine Übertragung ins Internet.</p>"
            "</section>"
        )

    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PROVOWARE I17-D</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:1200px;margin:auto;padding:24px;background:#111316;color:#f4f7fb}}
section{{background:#191c20;border:1px solid #343a42;border-radius:14px;padding:18px;margin:14px 0}}
.badge{{font-weight:700;padding:4px 9px;border-radius:999px}}
.pass{{background:#173c29;color:#a9ffd0}} .fail{{background:#4b1f24;color:#ffd0d4}} .open{{background:#493d16;color:#ffeaa0}}
table{{width:100%;border-collapse:collapse}} th,td{{text-align:left;padding:10px;border-bottom:1px solid #343a42;vertical-align:top}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}}
img{{width:100%;border:1px solid #4d5662;border-radius:10px}}
a{{color:#7db7ff}} .muted{{color:#b2bac5}}
button{{font-size:1.1rem;font-weight:700;padding:14px 20px;margin:6px;border:0;border-radius:10px;cursor:pointer;color:white}}
.yes{{background:#2c8b57}} .no{{background:#a83d49}} .maybe{{background:#9a7b23}}
</style></head><body>
<h1>PROVOWARE I17-D – Accessibility Evidence</h1>
<section><p><strong>Commit:</strong> {html.escape(str(report['commit']))}<br>
<strong>Plattform:</strong> {html.escape(str(report['platform']))}<br>
<strong>Qt:</strong> {html.escape(str(report['qt_platform']))}</p>
<p>I17-AUTO {badge(str(report['technical_status']))}
&nbsp; I17-HUMAN {badge(str(report['human_status']))}
&nbsp; GESAMT {badge(str(report['overall_status']))}</p></section>
<section><h2>Automatische Prüfungen</h2>
<table><tr><th>Gate</th><th>Status</th><th>Befund</th><th>Evidence</th></tr>
{''.join(rows)}</table></section>
<section><h2>Screenshots</h2><div class="gallery">{images}</div></section>
{human}
</body></html>"""


def write_reports(report: dict[str, object], root: Path) -> None:
    (root / "I17_EVIDENCE.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (root / "I17_AUSWERTUNG.txt").write_text(render_text(report), encoding="utf-8")
    (root / "I17_REPORT.html").write_text(render_html(report), encoding="utf-8")


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
                body = render_html(report, f"/human?token={token}").encode("utf-8")
                self.send_bytes(200, "text/html; charset=utf-8", body)
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
        app, window = create_main_window()
    except RuntimeError as exc:
        print(f"🔴 {exc}")
        return 3

    root = create_evidence_dir()
    fixtures = create_fixtures(root)
    window.show()
    app.processEvents()

    report: dict[str, object] = {
        "evidence": "I17-D automated Qt accessibility",
        "commit": current_commit(),
        "captured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "qt_platform": app.platformName(),
        "scale_checks": run_scale_checks(app, window, root),
        "focus_check": run_focus_check(app, window, root),
        "preview_check": run_preview_check(app, window, fixtures, root),
        "human_status": "OPEN",
    }
    report["technical_status"] = technical_status(report)
    report["overall_status"] = overall_status(str(report["technical_status"]), "OPEN")
    write_reports(report, root)
    window.close()
    app.processEvents()

    if report["technical_status"] == "PASS" and not auto_only and not offscreen:
        report["human_status"] = chromium_human_gate(report, root)
        report["overall_status"] = overall_status(
            str(report["technical_status"]), str(report["human_status"])
        )
        write_reports(report, root)
    elif not auto_only:
        browser = chromium_binary()
        if browser:
            subprocess.Popen(
                [browser, (root / "I17_REPORT.html").as_uri()],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

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
