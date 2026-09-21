from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.i17_target_evidence import (
    MANUAL_GATES,
    MAX_INPUT_ATTEMPTS,
    SCREENSHOTS,
    ask_gate,
    build_target_report,
    create_preview_fixtures,
    overall_status,
    screenshot_state,
)


class I17TargetEvidenceContractTests(unittest.TestCase):
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


class I17GuidedEvidenceTests(unittest.TestCase):
    def test_pass_requires_every_manual_gate_and_screenshot(self) -> None:
        statuses = ["PASS"] * len(MANUAL_GATES)
        shots = {name: True for name in SCREENSHOTS}
        self.assertEqual(overall_status("PASS", True, statuses, shots), "PASS")

    def test_missing_screenshot_keeps_evidence_open(self) -> None:
        statuses = ["PASS"] * len(MANUAL_GATES)
        shots = {name: True for name in SCREENSHOTS}
        shots[SCREENSHOTS[-1]] = False
        self.assertEqual(overall_status("PASS", True, statuses, shots), "OPEN")

    def test_manual_failure_is_fail(self) -> None:
        statuses = ["PASS"] * len(MANUAL_GATES)
        statuses[0] = "FAIL"
        shots = {name: True for name in SCREENSHOTS}
        self.assertEqual(overall_status("PASS", True, statuses, shots), "FAIL")

    def test_invalid_input_is_bounded_and_remains_open(self) -> None:
        answers = iter(["x"] * MAX_INPUT_ATTEMPTS)
        status = ask_gate(MANUAL_GATES[0], input_fn=lambda _: next(answers))
        self.assertEqual(status, "OPEN")

    def test_fixtures_are_synthetic_and_screenshot_scan_is_exact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures = create_preview_fixtures(root)
            self.assertTrue(fixtures["empty"].is_dir())
            self.assertEqual(list(fixtures["empty"].iterdir()), [])
            names = {path.name for path in fixtures["sample"].iterdir()}
            self.assertIn("Datei mit Leerzeichen.txt", names)
            self.assertIn("Grüße-äöü.txt", names)
            (root / SCREENSHOTS[0]).write_bytes(b"png")
            state = screenshot_state(root)
            self.assertTrue(state[SCREENSHOTS[0]])
            self.assertFalse(state[SCREENSHOTS[1]])


if __name__ == "__main__":
    unittest.main()
