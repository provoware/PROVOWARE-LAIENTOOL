from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

from provoware_laientool.diagnostic_export_plan import (
    FORMAT_JSON,
    FORMAT_TEXT,
    ExportPlan,
    prepare_diagnostic_export,
)
from provoware_laientool.diagnostics import DiagnosticEntry, DiagnosticReport


def safe_report(*, redacted: bool = True, writes: bool = False) -> DiagnosticReport:
    return DiagnosticReport(
        schema_version="1",
        collection_status="PASS",
        health_status="PASS",
        entries=(
            DiagnosticEntry("platform", "system", "Linux"),
            DiagnosticEntry("start", "profile", "gui-ready"),
        ),
        warnings=(),
        redaction_applied=redacted,
        write_paths_enabled=writes,
    )


class DiagnosticExportPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "Export Ziel"
        self.root.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_json_preparation_is_deterministic_and_read_only(self) -> None:
        first = prepare_diagnostic_export(
            safe_report(),
            target_dir=self.root,
            export_format=FORMAT_JSON,
            filename="PROVOWARE-Diagnose-20260921-180000.json",
        )
        second = prepare_diagnostic_export(
            safe_report(),
            target_dir=self.root,
            export_format=FORMAT_JSON,
            filename="PROVOWARE-Diagnose-20260921-180000.json",
        )

        self.assertEqual(first.status, "PASS")
        self.assertEqual(first, second)
        self.assertIsNotNone(first.plan)
        self.assertIsNotNone(first.payload)
        assert first.plan is not None
        assert first.payload is not None
        self.assertFalse(first.plan.write_enabled)
        self.assertFalse(first.plan.overwrite_allowed)
        self.assertEqual(first.plan.payload_size_bytes, len(first.payload))
        self.assertEqual(len(first.plan.payload_sha256), 64)
        self.assertFalse(Path(first.plan.final_path).exists())
        self.assertEqual(json.loads(first.payload.decode("utf-8"))["schema_version"], "1")

    def test_text_preparation_keeps_unicode_target_path(self) -> None:
        unicode_dir = self.root / "Übergabe"
        unicode_dir.mkdir()
        result = prepare_diagnostic_export(
            safe_report(),
            target_dir=unicode_dir,
            export_format=FORMAT_TEXT,
            filename="PROVOWARE-Diagnose-20260921-180001.txt",
        )

        self.assertEqual(result.status, "PASS")
        assert result.plan is not None
        self.assertIn("Übergabe", result.plan.target_dir)
        self.assertFalse(Path(result.plan.final_path).exists())

    def test_existing_target_blocks_without_modifying_it(self) -> None:
        target = self.root / "PROVOWARE-Diagnose-20260921-180000.json"
        target.write_text("bestehend", encoding="utf-8")

        result = prepare_diagnostic_export(
            safe_report(),
            target_dir=self.root,
            export_format=FORMAT_JSON,
            filename=target.name,
        )

        self.assertEqual(result.status, "BLOCKED")
        self.assertIsNone(result.plan)
        self.assertEqual(target.read_text(encoding="utf-8"), "bestehend")

    def test_symlink_target_directory_is_blocked(self) -> None:
        real = Path(self.temp.name) / "real"
        real.mkdir()
        link = Path(self.temp.name) / "link"
        link.symlink_to(real, target_is_directory=True)

        result = prepare_diagnostic_export(
            safe_report(),
            target_dir=link,
            export_format=FORMAT_JSON,
            filename="PROVOWARE-Diagnose.json",
        )

        self.assertEqual(result.status, "BLOCKED")
        self.assertTrue(any("Symlink" in error for error in result.errors))

    def test_dangling_symlink_target_file_is_blocked(self) -> None:
        target = self.root / "PROVOWARE-Diagnose.json"
        target.symlink_to(self.root / "missing")

        result = prepare_diagnostic_export(
            safe_report(),
            target_dir=self.root,
            export_format=FORMAT_JSON,
            filename=target.name,
        )

        self.assertEqual(result.status, "BLOCKED")
        self.assertTrue(any("Zieldatei" in error for error in result.errors))

    def test_path_in_filename_is_blocked(self) -> None:
        result = prepare_diagnostic_export(
            safe_report(),
            target_dir=self.root,
            export_format=FORMAT_JSON,
            filename="../PROVOWARE-Diagnose.json",
        )
        self.assertEqual(result.status, "BLOCKED")

    def test_wrong_suffix_and_format_are_blocked(self) -> None:
        wrong_suffix = prepare_diagnostic_export(
            safe_report(),
            target_dir=self.root,
            export_format=FORMAT_JSON,
            filename="PROVOWARE-Diagnose.txt",
        )
        wrong_format = prepare_diagnostic_export(
            safe_report(),
            target_dir=self.root,
            export_format="zip",
            filename="PROVOWARE-Diagnose.zip",
        )
        self.assertEqual(wrong_suffix.status, "BLOCKED")
        self.assertEqual(wrong_format.status, "BLOCKED")

    def test_unredacted_report_is_blocked(self) -> None:
        result = prepare_diagnostic_export(
            safe_report(redacted=False),
            target_dir=self.root,
            export_format=FORMAT_JSON,
            filename="PROVOWARE-Diagnose.json",
        )
        self.assertEqual(result.status, "BLOCKED")

    def test_report_with_write_enable_is_blocked(self) -> None:
        result = prepare_diagnostic_export(
            safe_report(writes=True),
            target_dir=self.root,
            export_format=FORMAT_JSON,
            filename="PROVOWARE-Diagnose.json",
        )
        self.assertEqual(result.status, "BLOCKED")

    def test_second_redaction_gate_detects_sensitive_payload(self) -> None:
        report = DiagnosticReport(
            schema_version="1",
            collection_status="PASS",
            health_status="OPEN",
            entries=(
                DiagnosticEntry(
                    "message",
                    "unsafe",
                    "/srv/Private Ablage/ä Datei.txt",
                ),
                DiagnosticEntry(
                    "message",
                    "unsafe_windows",
                    r"C:\Users\Jörg\Meine Datei.txt",
                ),
            ),
            warnings=(),
            redaction_applied=True,
            write_paths_enabled=False,
        )
        result = prepare_diagnostic_export(
            report,
            target_dir=self.root,
            export_format=FORMAT_TEXT,
            filename="PROVOWARE-Diagnose.txt",
        )
        self.assertEqual(result.status, "BLOCKED")
        self.assertIsNone(result.payload)
        self.assertIsNone(result.plan)
        self.assertTrue(any("sensible Inhalte" in error for error in result.errors))

    def test_plan_is_immutable(self) -> None:
        plan = ExportPlan(
            target_dir="/tmp",
            filename="x.json",
            final_path="/tmp/x.json",
            export_format=FORMAT_JSON,
            payload_size_bytes=1,
            payload_sha256="0" * 64,
        )
        with self.assertRaises(FrozenInstanceError):
            plan.write_enabled = True  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
