from __future__ import annotations

import json
import unittest
from pathlib import Path

from provoware_laientool.diagnostics import (
    build_diagnostic_report,
    diagnostic_to_json,
    format_diagnostic_text,
    redact_text,
)
from provoware_laientool.preflight import (
    CapabilityInfo,
    PlatformInfo,
    PreflightResult,
    StartPlan,
)
from provoware_laientool.recovery_contract import (
    STATE_APPLYING,
    JournalSnapshot,
)


def sample_preflight(status: str = "PASS") -> PreflightResult:
    return PreflightResult(
        status=status,
        platform=PlatformInfo(
            system="Linux",
            release="6.8.0",
            machine="x86_64",
            python="3.12.3",
            distro_id="ubuntu",
            distro_name="Ubuntu 24.04 LTS",
            distro_version="24.04",
            desktop="KDE",
            session_type="x11",
            filesystem_encoding="utf-8",
            runtime_source="system",
        ),
        capabilities=CapabilityInfo(
            linux=True,
            supported_distro_family=True,
            python_supported=True,
            graphical_session=True,
            pyside6_available=True,
            utf8_filesystem=True,
            home_available=True,
            downloads_available=True,
            project_readable=True,
        ),
        start_plan=StartPlan(
            profile="gui-ready",
            gui_possible=True,
            portable_runtime_preferred=False,
            reason="bereit",
        ),
        notes=("Alles bereit.",),
    )


class RedactionTests(unittest.TestCase):
    def test_home_email_and_tokens_are_redacted(self) -> None:
        text = (
            "/home/alice/Downloads/file.txt alice@example.com "
            "ghp_123456789012345678901234 sk-abcdefghijklmnopqrstuvwxyz12345 "
            "Bearer abcdefghijklmnop"
        )
        redacted = redact_text(text, home=Path("/home/alice"))
        self.assertNotIn("/home/alice", redacted)
        self.assertNotIn("alice@example.com", redacted)
        self.assertNotIn("ghp_", redacted)
        self.assertNotIn("sk-", redacted)
        self.assertNotIn("abcdefghijklmnop", redacted)
        self.assertIn("$HOME", redacted)
        self.assertIn("<EMAIL>", redacted)
        self.assertIn("<TOKEN>", redacted)

    def test_other_text_is_preserved(self) -> None:
        self.assertEqual(redact_text("Ubuntu 24.04 / KDE"), "Ubuntu 24.04 / KDE")


class DiagnosticReportTests(unittest.TestCase):
    def test_report_is_read_only_and_redacted(self) -> None:
        report = build_diagnostic_report(
            preflight=sample_preflight(),
            extra_messages=("Fehler in /home/alice/private.txt",),
            home=Path("/home/alice"),
        )
        self.assertEqual(report.collection_status, "PASS")
        self.assertEqual(report.health_status, "PASS")
        self.assertFalse(report.write_paths_enabled)
        self.assertTrue(report.redaction_applied)
        joined = "\n".join(entry.value for entry in report.entries)
        self.assertNotIn("/home/alice", joined)
        self.assertIn("$HOME/private.txt", joined)

    def test_start_profile_is_present_as_single_entry(self) -> None:
        report = build_diagnostic_report(preflight=sample_preflight())
        matches = [
            entry
            for entry in report.entries
            if entry.category == "start" and entry.key == "profile"
        ]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].value, "gui-ready")

    def test_open_preflight_produces_open_health(self) -> None:
        report = build_diagnostic_report(preflight=sample_preflight("OPEN"))
        self.assertEqual(report.health_status, "OPEN")

    def test_recovery_unknown_effect_is_visible_without_ids(self) -> None:
        snapshot = JournalSnapshot(
            entry_id="secret-entry-id",
            preview_plan_id="secret-plan-id",
            preview_item_id="secret-item-id",
            state=STATE_APPLYING,
            attempt=2,
            last_error="Fehler in /home/alice/x",
        )
        report = build_diagnostic_report(
            preflight=sample_preflight(),
            recovery=snapshot,
            home=Path("/home/alice"),
        )
        text = format_diagnostic_text(report)
        self.assertIn("effect_known: nein", text)
        self.assertIn("automatic_retry: nein", text)
        self.assertNotIn("secret-entry-id", text)
        self.assertNotIn("secret-plan-id", text)
        self.assertNotIn("secret-item-id", text)
        self.assertNotIn("/home/alice", text)

    def test_json_is_parseable_and_contains_no_write_enable(self) -> None:
        report = build_diagnostic_report(preflight=sample_preflight())
        payload = json.loads(diagnostic_to_json(report))
        self.assertEqual(payload["schema_version"], "1")
        self.assertFalse(payload["write_paths_enabled"])


if __name__ == "__main__":
    unittest.main()
