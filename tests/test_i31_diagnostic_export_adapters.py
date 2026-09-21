from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from provoware_laientool.capability_registry import STATUS_OPEN, get_use_case
from provoware_laientool.diagnostic_export_adapter import (
    CANCELLED,
    PASS,
    DiagnosticExportAdapterSession,
    run_cli_export_evidence_flow,
)
from provoware_laientool.diagnostics import DiagnosticEntry, DiagnosticReport


def report() -> DiagnosticReport:
    return DiagnosticReport(
        schema_version="1",
        collection_status="PASS",
        health_status="PASS",
        entries=(DiagnosticEntry("test", "value", "synthetic"),),
        warnings=(),
        redaction_applied=True,
        write_paths_enabled=False,
    )


class I31AdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_registry_remains_open_and_hidden_from_standard_adapters(self) -> None:
        entry = get_use_case("diagnostics.export_local")
        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry.status, STATUS_OPEN)
        self.assertFalse(entry.gui_available)
        self.assertFalse(entry.cli_available)

    def test_shared_session_requires_both_confirmations(self) -> None:
        session = DiagnosticExportAdapterSession(
            report(),
            target_dir=self.root,
            export_format="json",
        )
        preview = session.preview()
        self.assertEqual(preview.status, PASS)
        blocked = session.confirm_and_execute()
        self.assertNotEqual(blocked.status, PASS)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_shared_session_pass_creates_exactly_one_file(self) -> None:
        session = DiagnosticExportAdapterSession(
            report(),
            target_dir=self.root,
            export_format="json",
        )
        self.assertEqual(session.confirm_stage1().status, "CONFIRMED_STAGE_1")
        result = session.confirm_and_execute()
        self.assertEqual(result.status, PASS)
        created = list(self.root.glob("PROVOWARE-Diagnose-I31.*"))
        self.assertEqual(len(created), 1)

    def test_cancel_after_stage1_creates_no_file(self) -> None:
        session = DiagnosticExportAdapterSession(
            report(),
            target_dir=self.root,
            export_format="text",
        )
        session.confirm_stage1()
        self.assertEqual(session.cancel().status, CANCELLED)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_existing_target_uses_three_part_lay_text_and_blocks(self) -> None:
        existing = self.root / "PROVOWARE-Diagnose-I31.txt"
        existing.write_text("bestehend", encoding="utf-8")
        session = DiagnosticExportAdapterSession(
            report(),
            target_dir=self.root,
            export_format="text",
        )
        result = session.preview()
        self.assertNotEqual(result.status, PASS)
        self.assertIn("Was ist passiert?", result.body)
        self.assertIn("Was bedeutet das?", result.body)
        self.assertIn("Was kann ich jetzt tun?", result.body)
        self.assertEqual(existing.read_text(encoding="utf-8"), "bestehend")

    def test_cli_pass_uses_same_core_and_creates_one_file(self) -> None:
        output: list[str] = []
        answers = iter(("2", "1", "1"))
        status = run_cli_export_evidence_flow(
            report(),
            target_dir=self.root,
            input_fn=lambda _: next(answers),
            output_fn=output.append,
        )
        self.assertEqual(status, PASS)
        self.assertEqual(len(list(self.root.glob("PROVOWARE-Diagnose-I31.*"))), 1)
        joined = "\n".join(output)
        self.assertIn("Weiter zur finalen Bestätigung", joined)
        self.assertIn("Diagnosedatei jetzt neu erstellen", joined)

    def test_cli_cancel_creates_no_file(self) -> None:
        answers = iter(("1", "0"))
        status = run_cli_export_evidence_flow(
            report(),
            target_dir=self.root,
            input_fn=lambda _: next(answers),
            output_fn=lambda _: None,
        )
        self.assertEqual(status, CANCELLED)
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
