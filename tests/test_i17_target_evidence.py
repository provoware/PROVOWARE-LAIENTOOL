from __future__ import annotations

import unittest
from unittest.mock import patch

from scripts.i17_target_evidence import (
    MANUAL_GATES,
    SCREENSHOTS,
    build_target_report,
)


class I17TargetEvidenceTests(unittest.TestCase):
    def test_manual_gates_never_auto_pass(self) -> None:
        report = build_target_report()
        self.assertEqual(report["overall_status"], "OPEN")
        self.assertTrue(report["manual_gates"])
        self.assertTrue(
            all(item["status"] == "OPEN" for item in report["manual_gates"])
        )

    def test_required_screenshot_set_is_stable(self) -> None:
        self.assertEqual(
            SCREENSHOTS,
            (
                "i17-100-overview.png",
                "i17-150-overview.png",
                "i17-200-overview.png",
                "i17-keyboard-focus.png",
                "i17-file-preview.png",
            ),
        )

    def test_runtime_ready_requires_real_gui_capability(self) -> None:
        fake = {
            "automated_status": "PASS",
            "runtime": {
                "pyside6_available": True,
                "display_session_available": False,
                "session_type": "unknown",
                "real_gui_run_possible_here": False,
            },
        }
        with patch("scripts.i17_target_evidence.build_report", return_value=fake):
            report = build_target_report()
        self.assertFalse(report["runtime_ready"])

    def test_gate_set_includes_preview_and_layperson_checks(self) -> None:
        joined = "\n".join(MANUAL_GATES)
        self.assertIn("Dateivorschau", joined)
        self.assertIn("Laienprofil", joined)
        self.assertIn("200 %", joined)


if __name__ == "__main__":
    unittest.main()
