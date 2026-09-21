from __future__ import annotations

import unittest

from scripts.core_diagnostics import run_diagnostic


class CoreDiagnosticsTests(unittest.TestCase):
    def test_professional_core_diagnostic_passes(self) -> None:
        report = run_diagnostic()
        self.assertEqual(report["mode"], "temporary-filesystem-only")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["failure_count"], 0)
        self.assertGreaterEqual(len(report["checks"]), 5)


if __name__ == "__main__":
    unittest.main()
