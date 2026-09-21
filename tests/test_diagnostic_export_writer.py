from __future__ import annotations

from dataclasses import replace
import errno
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from provoware_laientool.diagnostic_export import (
    BLOCKED_NOT_AUTHORIZED, BLOCKED_PAYLOAD_INVALID, BLOCKED_TARGET_EXISTS,
    BLOCKED_TARGET_UNSAFE, PASS, WRITE_COMMIT_RACE, WRITE_NO_SPACE,
    WRITE_PARTIAL_REMAINS, WRITE_PERMISSION_ERROR, write_diagnostic_export,
)
from provoware_laientool.diagnostic_export_plan import FORMAT_JSON, FORMAT_TEXT, prepare_diagnostic_export
from provoware_laientool.diagnostics import DiagnosticEntry, DiagnosticReport


def report() -> DiagnosticReport:
    return DiagnosticReport(
        schema_version="1", collection_status="PASS", health_status="PASS",
        entries=(DiagnosticEntry("platform", "system", "Linux"),), warnings=(),
        redaction_applied=True, write_paths_enabled=False,
    )


class DiagnosticWriterTestlabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = (Path(self.temp.name) / "Export Ziel ä").resolve()
        self.root.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def prepared(self, *, fmt: str = FORMAT_JSON, name: str = "PROVOWARE-Diagnose-20260922-000000.json"):
        prep = prepare_diagnostic_export(report(), target_dir=self.root, export_format=fmt, filename=name)
        self.assertEqual(prep.status, "PASS")
        assert prep.plan is not None and prep.payload is not None
        return prep.payload, replace(prep.plan, write_enabled=True)

    def partials(self) -> list[Path]:
        return list(self.root.glob(".PROVOWARE-Diagnose.partial-*"))

    def test_requires_explicit_write_authorization(self) -> None:
        prep = prepare_diagnostic_export(report(), target_dir=self.root, export_format=FORMAT_JSON, filename="PROVOWARE-Diagnose.json")
        assert prep.plan is not None and prep.payload is not None
        result = write_diagnostic_export(prep.payload, prep.plan)
        self.assertEqual(result.status, BLOCKED_NOT_AUTHORIZED)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_successful_json_export_is_create_only_and_verified(self) -> None:
        payload, plan = self.prepared()
        result = write_diagnostic_export(payload, plan)
        self.assertEqual(result.status, PASS)
        self.assertEqual(Path(result.final_path).read_bytes(), payload)
        self.assertEqual(result.bytes_written, len(payload))
        self.assertEqual(self.partials(), [])

    def test_text_export_supports_unicode_and_spaces(self) -> None:
        payload, plan = self.prepared(fmt=FORMAT_TEXT, name="PROVOWARE-Diagnose-20260922-000001.txt")
        result = write_diagnostic_export(payload, plan)
        self.assertEqual(result.status, PASS)
        self.assertEqual(Path(result.final_path).read_bytes(), payload)

    def test_existing_target_is_never_overwritten(self) -> None:
        payload, plan = self.prepared()
        final = Path(plan.final_path)
        final.write_bytes(b"bestehend")
        result = write_diagnostic_export(payload, plan)
        self.assertEqual(result.status, BLOCKED_TARGET_EXISTS)
        self.assertEqual(final.read_bytes(), b"bestehend")

    def test_payload_hash_or_size_mismatch_blocks_before_write(self) -> None:
        payload, plan = self.prepared()
        result = write_diagnostic_export(payload + b"x", plan)
        self.assertEqual(result.status, BLOCKED_PAYLOAD_INVALID)
        self.assertFalse(Path(plan.final_path).exists())
        self.assertEqual(self.partials(), [])

    def test_forged_symlink_target_directory_is_blocked(self) -> None:
        payload, plan = self.prepared()
        real = Path(self.temp.name) / "real"; real.mkdir()
        link = Path(self.temp.name) / "link"; link.symlink_to(real, target_is_directory=True)
        forged = replace(plan, target_dir=str(link), final_path=str(link / plan.filename))
        self.assertEqual(write_diagnostic_export(payload, forged).status, BLOCKED_TARGET_UNSAFE)

    def test_enospc_is_classified_and_owned_partial_is_cleaned(self) -> None:
        payload, plan = self.prepared()
        with patch("provoware_laientool.diagnostic_export.os.write", side_effect=OSError(errno.ENOSPC, "full")):
            result = write_diagnostic_export(payload, plan)
        self.assertEqual(result.status, WRITE_NO_SPACE)
        self.assertFalse(Path(plan.final_path).exists())
        self.assertEqual(self.partials(), [])

    def test_permission_error_is_classified(self) -> None:
        payload, plan = self.prepared()
        original_open = os.open
        def guarded_open(path, flags, *args, **kwargs):
            if ".partial-" in str(path):
                raise PermissionError("denied")
            return original_open(path, flags, *args, **kwargs)
        with patch("provoware_laientool.diagnostic_export.os.open", side_effect=guarded_open):
            result = write_diagnostic_export(payload, plan)
        self.assertEqual(result.status, WRITE_PERMISSION_ERROR)
        self.assertFalse(Path(plan.final_path).exists())

    def test_target_created_at_commit_wins_and_is_preserved(self) -> None:
        payload, plan = self.prepared()
        final = Path(plan.final_path)
        def racing_link(*args, **kwargs):
            final.write_bytes(b"racer")
            raise FileExistsError("race")
        with patch("provoware_laientool.diagnostic_export.os.link", side_effect=racing_link):
            result = write_diagnostic_export(payload, plan)
        self.assertEqual(result.status, WRITE_COMMIT_RACE)
        self.assertEqual(final.read_bytes(), b"racer")
        self.assertEqual(self.partials(), [])

    def test_parallel_same_name_has_exactly_one_winner(self) -> None:
        payload, plan = self.prepared()
        barrier = threading.Barrier(2)
        original_link = os.link
        def synchronized_link(src, dst, *, follow_symlinks=True):
            barrier.wait(timeout=5)
            return original_link(src, dst, follow_symlinks=follow_symlinks)
        results = []
        def worker() -> None:
            results.append(write_diagnostic_export(payload, plan))
        with patch("provoware_laientool.diagnostic_export.os.link", side_effect=synchronized_link):
            threads = [threading.Thread(target=worker), threading.Thread(target=worker)]
            for thread in threads: thread.start()
            for thread in threads: thread.join(timeout=10)
        self.assertEqual(sorted(result.status for result in results), [PASS, WRITE_COMMIT_RACE])
        self.assertEqual(Path(plan.final_path).read_bytes(), payload)
        self.assertEqual(self.partials(), [])

    def test_process_style_crash_after_partial_create_leaves_only_partial(self) -> None:
        payload, plan = self.prepared()
        with patch("provoware_laientool.diagnostic_export.os.write", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                write_diagnostic_export(payload, plan)
        self.assertFalse(Path(plan.final_path).exists())
        self.assertEqual(len(self.partials()), 1)

    def test_process_style_crash_before_commit_leaves_only_partial(self) -> None:
        payload, plan = self.prepared()
        with patch("provoware_laientool.diagnostic_export.os.link", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                write_diagnostic_export(payload, plan)
        self.assertFalse(Path(plan.final_path).exists())
        self.assertEqual(len(self.partials()), 1)

    def test_partial_name_collision_does_not_retry_or_delete_foreign_file(self) -> None:
        payload, plan = self.prepared()
        partial = self.root / ".PROVOWARE-Diagnose.partial-fixed"
        partial.write_bytes(b"foreign")
        with patch("provoware_laientool.diagnostic_export.secrets.token_hex", return_value="fixed"):
            result = write_diagnostic_export(payload, plan)
        self.assertEqual(result.status, WRITE_COMMIT_RACE)
        self.assertEqual(partial.read_bytes(), b"foreign")
        self.assertFalse(Path(plan.final_path).exists())

    def test_final_publish_with_partial_cleanup_failure_is_reported(self) -> None:
        payload, plan = self.prepared()
        original_unlink = os.unlink
        def deny_partial(path, *args, **kwargs):
            if ".partial-" in str(path): raise PermissionError("keep")
            return original_unlink(path, *args, **kwargs)
        with patch("provoware_laientool.diagnostic_export.os.unlink", side_effect=deny_partial):
            result = write_diagnostic_export(payload, plan)
        self.assertEqual(result.status, WRITE_PARTIAL_REMAINS)
        self.assertEqual(Path(plan.final_path).read_bytes(), payload)
        self.assertEqual(len(self.partials()), 1)


if __name__ == "__main__":
    unittest.main()
