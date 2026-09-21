#!/usr/bin/env python3
"""Read-only I14 accessibility evidence runner.

The runner never changes user data. It separates objective automated checks
from manual checks that require a real desktop and human observation.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from provoware_laientool.ui_themes import THEMES, stylesheet  # noqa: E402

TEXT_THRESHOLD = 4.5
FOCUS_THRESHOLD = 3.0
SCALES = (100, 150, 200)
FOCUS_SELECTORS = ("QPushButton:focus", "QComboBox:focus", "QTextEdit:focus")
MANUAL_GATES = (
    "100 % ohne abgeschnittene Kernaktion",
    "150 % ohne abgeschnittene Kernaktion",
    "200 % ohne abgeschnittene Kernaktion",
    "vollständiger Tastaturpfad",
    "sichtbarer Fokus an jedem fokussierbaren Kern-Widget",
    "Kontrast im realen Rendering plausibel",
    "Reduced Motion / keine notwendige Bewegungsinformation",
    "Laienverständlichkeit des Standardwegs",
)


def _channel(value: int) -> float:
    normalized = value / 255
    if normalized <= 0.04045:
        return normalized / 12.92
    return ((normalized + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    value = hex_color.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Ungültige Hex-Farbe: {hex_color}")
    red, green, blue = (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
    )
    return (
        0.2126 * _channel(red)
        + 0.7152 * _channel(green)
        + 0.0722 * _channel(blue)
    )


def contrast_ratio(first: str, second: str) -> float:
    a = relative_luminance(first)
    b = relative_luminance(second)
    lighter, darker = max(a, b), min(a, b)
    return (lighter + 0.05) / (darker + 0.05)


def theme_checks() -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for theme in THEMES:
        pairs = (
            ("text/canvas", theme.text, theme.canvas, TEXT_THRESHOLD),
            ("text/surface", theme.text, theme.surface, TEXT_THRESHOLD),
            ("muted/surface", theme.muted, theme.surface, TEXT_THRESHOLD),
            ("focus/raised", theme.focus, theme.raised, FOCUS_THRESHOLD),
        )
        for name, foreground, background, threshold in pairs:
            ratio = contrast_ratio(foreground, background)
            checks.append(
                {
                    "theme": theme.label,
                    "check": name,
                    "ratio": round(ratio, 2),
                    "threshold": threshold,
                    "status": "PASS" if ratio >= threshold else "FAIL",
                }
            )
    return checks


def focus_contract_checks() -> list[dict[str, str]]:
    css = stylesheet(THEMES[0], 100)
    return [
        {
            "selector": selector,
            "status": "PASS" if selector in css else "FAIL",
        }
        for selector in FOCUS_SELECTORS
    ]


def scale_contract_checks() -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for scale in SCALES:
        css = stylesheet(THEMES[0], scale)
        results.append(
            {
                "scale_percent": scale,
                "stylesheet_generated": bool(css.strip()),
                "status": "PASS" if css.strip() else "FAIL",
            }
        )
    return results


def runtime_context() -> dict[str, object]:
    pyside6 = importlib.util.find_spec("PySide6") is not None
    display = os.environ.get("DISPLAY")
    wayland = os.environ.get("WAYLAND_DISPLAY")
    session = os.environ.get("XDG_SESSION_TYPE")
    has_display = bool(display or wayland)
    return {
        "pyside6_available": pyside6,
        "display_session_available": has_display,
        "session_type": session or "unknown",
        "real_gui_run_possible_here": bool(pyside6 and has_display),
    }


def build_report() -> dict[str, object]:
    theme = theme_checks()
    focus = focus_contract_checks()
    scale = scale_contract_checks()
    automated_failures = [
        check
        for check in (*theme, *focus, *scale)
        if check["status"] == "FAIL"
    ]
    automated_status = "FAIL" if automated_failures else "PASS"

    return {
        "evidence": "I14 shell accessibility",
        "mode": "read-only",
        "automated_status": automated_status,
        "theme_contrast": theme,
        "focus_contract": focus,
        "scale_contract": scale,
        "runtime": runtime_context(),
        "manual_gates": [
            {"gate": gate, "status": "OPEN"} for gate in MANUAL_GATES
        ],
        "overall_status": "FAIL" if automated_failures else "OPEN",
        "note": (
            "OPEN bedeutet: automatisierbare Prüfungen sind ausgewertet, "
            "aber reale Bildschirm-/Laienprüfung fehlt. FAIL darf nicht durch "
            "eine manuelle Prüfung überstimmt werden."
        ),
    }


def format_text(report: dict[str, object]) -> str:
    lines = [
        "PROVOWARE I14 – Accessibility Evidence",
        "=======================================",
        f"Automatisiert: {report['automated_status']}",
        f"Gesamt: {report['overall_status']}",
        "",
        "Kontrast:",
    ]
    for check in report["theme_contrast"]:  # type: ignore[index]
        lines.append(
            f" - {check['status']} {check['theme']} {check['check']}: "
            f"{check['ratio']}:1 (Minimum {check['threshold']}:1)"
        )
    lines.extend(["", "Fokusvertrag:"])
    for check in report["focus_contract"]:  # type: ignore[index]
        lines.append(f" - {check['status']} {check['selector']}")
    lines.extend(["", "Skalierungsvertrag:"])
    for check in report["scale_contract"]:  # type: ignore[index]
        lines.append(f" - {check['status']} {check['scale_percent']} %")
    runtime = report["runtime"]  # type: ignore[assignment]
    lines.extend(
        [
            "",
            "Lokale GUI-Voraussetzungen:",
            f" - PySide6: {'JA' if runtime['pyside6_available'] else 'NEIN'}",
            f" - Display-Session: {'JA' if runtime['display_session_available'] else 'NEIN'}",
            f" - Session-Typ: {runtime['session_type']}",
            "",
            "Reale manuelle Gates:",
        ]
    )
    for item in report["manual_gates"]:  # type: ignore[index]
        lines.append(f" - OPEN {item['gate']}")
    lines.extend(["", str(report["note"])])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
