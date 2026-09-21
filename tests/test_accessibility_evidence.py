from __future__ import annotations

import unittest

from scripts.accessibility_evidence import (
    FOCUS_THRESHOLD,
    TEXT_THRESHOLD,
    build_report,
    contrast_ratio,
    focus_contract_checks,
    scale_contract_checks,
    theme_checks,
)


class ContrastMathTests(unittest.TestCase):
    def test_black_white_ratio_is_about_twenty_one(self) -> None:
        self.assertAlmostEqual(contrast_ratio("#000000", "#ffffff"), 21.0, places=2)

    def test_all_current_theme_text_contrasts_pass(self) -> None:
        checks = theme_checks()
        self.assertTrue(checks)
        for check in checks:
            threshold = check["threshold"]
            self.assertIn(threshold, (TEXT_THRESHOLD, FOCUS_THRESHOLD))
            self.assertEqual(check["status"], "PASS", check)


class FocusContractTests(unittest.TestCase):
    def test_focus_contract_is_complete_for_core_widgets(self) -> None:
        checks = {item["selector"]: item["status"] for item in focus_contract_checks()}
        self.assertEqual(checks["QPushButton:focus"], "PASS")
        self.assertEqual(checks["QComboBox:focus"], "PASS")
        self.assertEqual(checks["QTextEdit:focus"], "PASS")


class ScaleContractTests(unittest.TestCase):
    def test_100_150_200_stylesheets_are_generated(self) -> None:
        checks = scale_contract_checks()
        self.assertEqual([item["scale_percent"] for item in checks], [100, 150, 200])
        self.assertTrue(all(item["status"] == "PASS" for item in checks))


class EvidenceStatusTests(unittest.TestCase):
    def test_automated_evidence_passes_while_manual_remains_open(self) -> None:
        report = build_report()
        self.assertEqual(report["automated_status"], "PASS")
        self.assertEqual(report["overall_status"], "OPEN")
        self.assertTrue(all(item["status"] == "OPEN" for item in report["manual_gates"]))


if __name__ == "__main__":
    unittest.main()
