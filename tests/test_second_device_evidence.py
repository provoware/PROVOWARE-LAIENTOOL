from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "second_device_evidence.py"
SPEC = importlib.util.spec_from_file_location("second_device_evidence", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SecondDeviceEvidenceTests(unittest.TestCase):
    def test_redact_payload_keeps_only_safe_keys(self) -> None:
        payload = {
            "profile": "preflight-cli",
            "downloads_path": "/home/alice/Downloads",
            "python_version": "3.12.3",
            "nested": {"secret": "x"},
        }
        self.assertEqual(
            MODULE.redact_payload(payload),
            {"profile": "preflight-cli", "python_version": "3.12.3"},
        )

    def test_sha256_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("provoware", encoding="utf-8")
            self.assertEqual(MODULE.sha256(path), MODULE.sha256(path))

    def test_safe_keys_do_not_include_paths(self) -> None:
        for key in MODULE.SAFE_KEYS:
            self.assertNotIn("path", key.lower())


if __name__ == "__main__":
    unittest.main()
