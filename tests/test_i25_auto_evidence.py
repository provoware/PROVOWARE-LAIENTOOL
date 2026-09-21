from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.i25_auto_evidence import (
    FILE_DIALOG_SCREENSHOT,
    FOCUS_SCREENSHOT,
    HUMAN_TIMEOUT_SECONDS,
    PREVIEW_SCREENSHOT,
    SCALES,
    SCREENSHOTS,
    TARGET_DIALOG_SCREENSHOT,
    chromium_binary,
    create_fixtures,
    overall_status,
    technical_status,
)


class I25AutoEvidenceContractTests(unittest.TestCase):
    def test_expected_scales_and_screenshots_are_stable(self) -> None:
        self.assertEqual(SCALES, (100, 150, 200))
        self.assertEqual(SCREENSHOTS[150], "i25-150-overview.png")
        self.assertEqual(FOCUS_SCREENSHOT, "i25-keyboard-focus.png")
        self.assertEqual(FILE_DIALOG_SCREENSHOT, "i25-file-selection.png")
        self.assertEqual(TARGET_DIALOG_SCREENSHOT, "i25-target-selection.png")
        self.assertEqual(PREVIEW_SCREENSHOT, "i25-transfer-preview.png")

    def test_human_wait_is_bounded(self) -> None:
        self.assertGreater(HUMAN_TIMEOUT_SECONDS, 0)
        self.assertLessEqual(HUMAN_TIMEOUT_SECONDS, 900)

    def test_fixtures_are_synthetic_and_same_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixtures = create_fixtures(Path(tmp))
            self.assertTrue(fixtures["root"].is_dir())
            self.assertTrue((fixtures["root"] / "Ziel" / "Unter Ziel").is_dir())
            self.assertTrue((fixtures["source"] / "Grüße-äöü.txt").is_file())

    def test_technical_status_needs_all_automatic_gates(self) -> None:
        report = {
            "scale_checks": [{"status": "PASS"} for _ in SCALES],
            "focus_check": {"status": "PASS"},
            "workflow_check": {"status": "PASS"},
        }
        self.assertEqual(technical_status(report), "PASS")
        report["workflow_check"]["status"] = "FAIL"
        self.assertEqual(technical_status(report), "FAIL")

    def test_human_gate_is_only_final_gate(self) -> None:
        self.assertEqual(overall_status("PASS", "OPEN"), "OPEN")
        self.assertEqual(overall_status("PASS", "PASS"), "PASS")
        self.assertEqual(overall_status("PASS", "FAIL"), "FAIL")
        self.assertEqual(overall_status("FAIL", "PASS"), "FAIL")

    def test_chromium_lookup_is_explicit(self) -> None:
        with patch("scripts.i25_auto_evidence.shutil.which") as which:
            which.side_effect = lambda name: "/usr/bin/chromium" if name == "chromium" else None
            self.assertEqual(chromium_binary(), "chromium")


if __name__ == "__main__":
    unittest.main()
