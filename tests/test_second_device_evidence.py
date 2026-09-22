from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "second_device_evidence.py"
SPEC = importlib.util.spec_from_file_location("second_device_evidence", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SecondDeviceEvidenceTests(unittest.TestCase):
    def test_redact_payload_keeps_safe_nested_contract(self) -> None:
        payload = {
            "status": "PASS",
            "platform": {
                "python": "3.12.3",
                "machine": "x86_64",
                "secret_path": "/home/alice",
            },
            "capabilities": {
                "linux": True,
                "project_readable": True,
                "downloads_path": "/home/alice/Downloads",
            },
            "start_plan": {
                "profile": "preflight-cli",
                "reason": "lokal",
                "private": "x",
            },
            "notes": ["/home/alice/Downloads"],
        }
        redacted = MODULE.redact_payload(payload)
        self.assertEqual(redacted["status"], "PASS")
        self.assertEqual(
            redacted["platform"],
            {"python": "3.12.3", "machine": "x86_64"},
        )
        self.assertEqual(
            redacted["capabilities"],
            {"linux": True, "project_readable": True},
        )
        self.assertEqual(
            redacted["start_plan"],
            {"profile": "preflight-cli", "reason": "lokal"},
        )
        self.assertNotIn("notes", redacted)

    def test_sha256_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("provoware", encoding="utf-8")
            self.assertEqual(MODULE.sha256(path), MODULE.sha256(path))

    def test_source_identity_prefers_package_manifest_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            start = root / "start.py"
            start.write_text("print('ok')\n", encoding="utf-8")
            commit = "a" * 40
            (root / "PACKAGE_MANIFEST.json").write_text(
                json.dumps({"commit": commit}),
                encoding="utf-8",
            )
            identity = MODULE.source_identity(root, start)
            self.assertTrue(identity["valid"])
            self.assertEqual(identity["kind"], "package-manifest-commit")
            self.assertEqual(identity["commit"], commit)

    def test_source_identity_uses_git_commit_for_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            start = root / "start.py"
            start.write_text("print('ok')\n", encoding="utf-8")
            (root / ".git").mkdir()
            commit = "b" * 40
            with mock.patch.object(MODULE, "git_commit", return_value=commit):
                identity = MODULE.source_identity(root, start)
            self.assertTrue(identity["valid"])
            self.assertEqual(identity["kind"], "git-commit")
            self.assertEqual(identity["commit"], commit)

    def test_invalid_package_manifest_fails_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            start = root / "start.py"
            start.write_text("print('ok')\n", encoding="utf-8")
            (root / "PACKAGE_MANIFEST.json").write_text(
                json.dumps({"commit": "not-a-commit"}),
                encoding="utf-8",
            )
            identity = MODULE.source_identity(root, start)
            self.assertFalse(identity["valid"])
            self.assertEqual(identity["kind"], "invalid-package-manifest")
            self.assertIsNotNone(identity["error"])

    def test_source_identity_falls_back_to_start_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            start = root / "start.py"
            start.write_text("print('ok')\n", encoding="utf-8")
            identity = MODULE.source_identity(root, start)
            self.assertTrue(identity["valid"])
            self.assertEqual(identity["kind"], "start.py-sha256")
            self.assertIsNone(identity["commit"])
            self.assertEqual(identity["fingerprint_sha256"], MODULE.sha256(start))

    def test_redaction_key_sets_contain_no_paths(self) -> None:
        for keys in (
            MODULE.PLATFORM_KEYS,
            MODULE.CAPABILITY_KEYS,
            MODULE.START_PLAN_KEYS,
        ):
            for key in keys:
                self.assertNotIn("path", key.lower())


if __name__ == "__main__":
    unittest.main()
