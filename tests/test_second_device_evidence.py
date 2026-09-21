from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

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
