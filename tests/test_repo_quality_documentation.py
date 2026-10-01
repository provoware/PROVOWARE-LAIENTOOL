from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.repo_quality_checks.documentation import check_trailing_whitespace


class TrailingWhitespaceScopeTests(unittest.TestCase):
    def test_ignored_local_venv_is_not_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vendor_file = root / ".venv" / "vendor.py"
            vendor_file.parent.mkdir()
            vendor_file.write_text("third_party = True  \n", encoding="utf-8")
            errors: list[str] = []

            check_trailing_whitespace(root, errors.append)

            self.assertEqual(errors, [])

    def test_repository_text_file_is_still_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_file = root / "scripts" / "example.py"
            source_file.parent.mkdir()
            source_file.write_text("value = 1  \n", encoding="utf-8")
            errors: list[str] = []

            check_trailing_whitespace(root, errors.append)

            self.assertEqual(errors, ["Trailing whitespace: scripts/example.py:1"])


if __name__ == "__main__":
    unittest.main()
