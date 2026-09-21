from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.i17_auto_evidence import (
    FOCUS_SCREENSHOT,
    HUMAN_TIMEOUT_SECONDS,
    PREVIEW_SCREENSHOT,
    SCALES,
    SCREENSHOTS,
    chromium_binary,
    create_fixtures,
    overall_status,
    render_html,
    technical_status,
)


class I17AutoEvidenceContractTests(unittest.TestCase):
    def test_expected_scales_and_screenshots_are_stable(self) -> None:
        self.assertEqual(SCALES, (100, 150, 200))
        self.assertEqual(SCREENSHOTS[100], "i17-100-overview.png")
        self.assertEqual(SCREENSHOTS[150], "i17-150-overview.png")
        self.assertEqual(SCREENSHOTS[200], "i17-200-overview.png")
        self.assertEqual(FOCUS_SCREENSHOT, "i17-keyboard-focus.png")
        self.assertEqual(PREVIEW_SCREENSHOT, "i17-file-preview.png")

    def test_human_wait_is_bounded(self) -> None:
        self.assertGreater(HUMAN_TIMEOUT_SECONDS, 0)
        self.assertLessEqual(HUMAN_TIMEOUT_SECONDS, 900)

    def test_fixtures_are_synthetic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixtures = create_fixtures(Path(tmp))
            self.assertEqual(list(fixtures["empty"].iterdir()), [])
            self.assertEqual(
                {path.name for path in fixtures["sample"].iterdir()},
                {"Datei mit Leerzeichen.txt", "Grüße-äöü.txt"},
            )

    def test_technical_status_needs_every_automatic_gate(self) -> None:
        report = {
            "scale_checks": [{"status": "PASS"} for _ in SCALES],
            "focus_check": {"status": "PASS"},
            "preview_check": {"status": "PASS"},
        }
        self.assertEqual(technical_status(report), "PASS")
        report["focus_check"]["status"] = "FAIL"
        self.assertEqual(technical_status(report), "FAIL")

    def test_human_gate_stays_separate(self) -> None:
        self.assertEqual(overall_status("PASS", "OPEN"), "OPEN")
        self.assertEqual(overall_status("PASS", "PASS"), "PASS")
        self.assertEqual(overall_status("PASS", "FAIL"), "FAIL")
        self.assertEqual(overall_status("FAIL", "PASS"), "FAIL")

    def test_html_contains_single_human_question_and_chromium_evidence(self) -> None:
        report = {
            "commit": "abc",
            "captured_at": "now",
            "platform": "test",
            "qt_platform": "wayland",
            "scale_checks": [
                {
                    "scale_percent": scale,
                    "status": "PASS",
                    "failures": [],
                    "screenshot": SCREENSHOTS[scale],
                }
                for scale in SCALES
            ],
            "focus_check": {
                "status": "PASS",
                "failures": [],
                "screenshot": FOCUS_SCREENSHOT,
            },
            "preview_check": {
                "status": "PASS",
                "failures": [],
                "screenshot": PREVIEW_SCREENSHOT,
            },
            "technical_status": "PASS",
            "human_status": "OPEN",
            "overall_status": "OPEN",
        }
        rendered = render_html(report, "/human")
        self.assertIn("I17-AUTO", rendered)
        self.assertIn("I17-HUMAN", rendered)
        self.assertIn("Eine letzte menschliche Frage", rendered)
        self.assertIn("i17-file-preview.png", rendered)

    def test_chromium_lookup_is_explicit(self) -> None:
        with patch("scripts.i17_auto_evidence.shutil.which") as which:
            which.side_effect = lambda name: "/usr/bin/chromium" if name == "chromium" else None
            self.assertEqual(chromium_binary(), "chromium")


if __name__ == "__main__":
    unittest.main()
