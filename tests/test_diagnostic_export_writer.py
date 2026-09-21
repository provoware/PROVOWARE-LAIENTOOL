from __future__ import annotations

import errno
import os
import stat
import tempfile
import threading
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from provoware_laientool import diagnostic_export
from provoware_laientool.diagnostic_export import PARTIAL_PREFIX, write_diagnostic_export
from provoware_laientool.diagnostic_export_plan import (
    FORMAT_JSON,
    prepare_diagnostic_export,
)
from provoware_laientool.diagnostics import DiagnosticEntry, DiagnosticReport


def safe_report() -> DiagnosticReport:
    return DiagnosticReport(
        schema_version="1",
        collection_status="PASS",
        health_status="PASS",
        entries=(DiagnosticEntry("platform", "system", "Linux"),),
        warnings=(),
        redaction_applied=True,
        write_paths_enabled=False,
    )


class DiagnosticExportWriterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "Export Ziel"
        self.root.mkdir()
        prepared = prepare_diagnostic_export(
            safe_report(),
            target_dir=self.root,
            export_format=FORMAT_JSON,
            filename="PROVOWARE-Diagnose-20260921-230000.json",
        )
        self.assertEqual(prepared.status, "PASS")
        assert prepared.plan is not None and prepared.payload is not None
        self.payload = prepared.payload
        self.plan = replace(prepared.plan, write_enabled=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def partials(self) -> list[Path]:
        return sorted(self.root.glob(f"{PARTIAL_PREFIX}*"))

    def test_i26_plan_is_not_authorized_by_default(self) -> None:
        prepared = prepare_diagnostic_export(
            safe_report(),
            target_dir=self.root,
            export_format=FORMAT_JSON,
            filename="PROVOWARE-Diagnose-other.json",
        )
        assert prepared.plan is not None and prepared.payload is not None
        result = write_diagnostic_export(prepared.payload, prepared.plan)
        self.assertEqual(result.status, "BLOCKED")
        self.assertFalse(result.committed)
        self.assertFalse(Path(prepared.plan.final_path).exists())

    def test_successful_write_is_private_exact_and_no_partial_remains(self) -> None:
        result = write_diagnostic_export(self.payload, self.plan)
        self.assertEqual(result.status, "PASS")
        self.assertTrue(result.committed)
        final = Path(self.plan.final_path)
        self.assertEqual(final.read_bytes(), self.payload)
        self.assertEqual(result.bytes_written, len(self.payload))
        self.assertEqual(self.partials(), [])
        mode = stat.S_IMODE(final.stat().st_mode)
        self.assertEqual(mode & 0o077, 0)

    def test_existing_final_is_never_overwritten(self) -> None:
        final = Path(self.plan.final_path)
        final.write_text("bestehend", encoding="utf-8")
        result = write_diagnostic_export(self.payload, self.plan)
        self.assertEqual(result.status, "BLOCKED")
        self.assertEqual(final.read_text(encoding="utf-8"), "bestehend")
        self.assertEqual(self.partials(), [])

    def test_payload_hash_and_size_mismatch_block_before_write(self) -> None:
        for payload in (self.payload + b"x", self.payload[:-1]):
            with self.subTest(size=len(payload)):
                result = write_diagnostic_export(payload, self.plan)
                self.assertEqual(result.status, "BLOCKED")
                self.assertFalse(Path(self.plan.final_path).exists())
                self.assertEqual(self.partials(), [])

    def test_plan_final_path_mismatch_is_blocked(self) -> None:
        bad = replace(self.plan, final_path=str(self.root / "anderer.json"))
        result = write_diagnostic_export(self.payload, bad)
        self.assertEqual(result.status, "BLOCKED")
        self.assertEqual(self.partials(), [])

    def test_symlink_target_directory_is_blocked(self) -> None:
        real = Path(self.temp.name) / "real"
        real.mkdir()
        link = Path(self.temp.name) / "link"
        link.symlink_to(real, target_is_directory=True)
        bad = replace(
            self.plan,
            target_dir=str(link),
            final_path=str(link / self.plan.filename),
        )
        result = write_diagnostic_export(self.payload, bad)
        self.assertEqual(result.status, "BLOCKED")

    def test_partial_name_collision_has_no_retry_and_no_overwrite(self) -> None:
        token = "a" * 24
        partial = self.root / f"{PARTIAL_PREFIX}{token}"
        partial.write_text("fremd", encoding="utf-8")
        with patch.object(diagnostic_export.secrets, "token_hex", return_value=token):
            result = write_diagnostic_export(self.payload, self.plan)
        self.assertIn(result.status, {"BLOCKED", "FAILED"})
        self.assertEqual(partial.read_text(encoding="utf-8"), "fremd")
        self.assertFalse(Path(self.plan.final_path).exists())

    def test_enospc_during_write_is_failed_and_owned_partial_is_cleaned(self) -> None:
        with patch.object(
            diagnostic_export.os,
            "write",
            side_effect=OSError(errno.ENOSPC, "No space left on device"),
        ):
            result = write_diagnostic_export(self.payload, self.plan)
        self.assertEqual(result.status, "FAILED")
        self.assertFalse(result.committed)
        self.assertFalse(Path(self.plan.final_path).exists())
        self.assertEqual(self.partials(), [])

    def test_permission_error_before_create_is_blocked(self) -> None:
        real_open = diagnostic_export.os.open

        def denied(path, flags, *args, **kwargs):
            if Path(path) == self.root:
                raise PermissionError(errno.EACCES, "denied")
            return real_open(path, flags, *args, **kwargs)

        with patch.object(diagnostic_export.os, "open", side_effect=denied):
            result = write_diagnostic_export(self.payload, self.plan)
        self.assertEqual(result.status, "BLOCKED")
        self.assertFalse(result.committed)
        self.assertEqual(self.partials(), [])

    def test_crash_before_publish_leaves_only_identifiable_partial(self) -> None:
        with patch.object(diagnostic_export.os, "link", side_effect=SystemExit(77)):
            with self.assertRaises(SystemExit):
                write_diagnostic_export(self.payload, self.plan)
        self.assertFalse(Path(self.plan.final_path).exists())
        partials = self.partials()
        self.assertEqual(len(partials), 1)
        self.assertEqual(partials[0].read_bytes(), self.payload)

    def test_two_writers_same_final_exactly_one_wins(self) -> None:
        barrier = threading.Barrier(2)
        real_link = diagnostic_export.os.link

        def synchronized_link(*args, **kwargs):
            barrier.wait(timeout=5)
            return real_link(*args, **kwargs)

        results = []

        def worker() -> None:
            results.append(write_diagnostic_export(self.payload, self.plan))

        with patch.object(diagnostic_export.os, "link", side_effect=synchronized_link):
            first = threading.Thread(target=worker)
            second = threading.Thread(target=worker)
            first.start()
            second.start()
            first.join(timeout=10)
            second.join(timeout=10)

        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertEqual(sorted(result.status for result in results), ["BLOCKED", "PASS"])
        self.assertEqual(Path(self.plan.final_path).read_bytes(), self.payload)
        self.assertEqual(self.partials(), [])

    def test_no_product_code_creates_write_enabled_plan(self) -> None:
        src = Path(__file__).resolve().parents[1] / "src" / "provoware_laientool"
        offenders = []
        for path in src.glob("*.py"):
            if path.name == "diagnostic_export.py":
                continue
            text = path.read_text(encoding="utf-8")
            if "write_enabled=True" in text or "write_enabled = True" in text:
                offenders.append(path.name)
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
