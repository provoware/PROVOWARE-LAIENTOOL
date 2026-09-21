from __future__ import annotations

import unittest

from scripts.diagnostic_writer_guard import analyze_writer_source


def safe_writer() -> str:
    return (
        "import os\n"
        "partial_path = 'partial'\n"
        "final_path = 'final'\n"
        "partial_fd = os.open(partial_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_CLOEXEC)\n"
        "os.write(partial_fd, b'data')\n"
        "os.fsync(partial_fd)\n"
        "os.close(partial_fd)\n"
        "os.link(partial_path, final_path, follow_symlinks=False)\n"
        "os.unlink(partial_path)\n"
    )


class DiagnosticWriterGuardTests(unittest.TestCase):
    def test_exact_no_clobber_sequence_is_allowed(self) -> None:
        self.assertEqual(analyze_writer_source(safe_writer()), ())

    def test_write_without_exclusive_create_is_blocked(self) -> None:
        violations = analyze_writer_source(
            "import os\npartial_path='p'\nos.open(partial_path, os.O_CREAT | os.O_WRONLY)"
        )
        self.assertTrue(any("O_CREAT|O_EXCL" in item for item in violations))

    def test_dynamic_or_numeric_flags_fail_closed(self) -> None:
        cases = (
            "import os\npartial_path='p'\nflags=os.O_CREAT|os.O_EXCL|os.O_WRONLY\nos.open(partial_path, flags)",
            "import os\npartial_path='p'\nos.open(partial_path, 193)",
        )
        for source in cases:
            with self.subTest(source=source):
                self.assertTrue(any(
                    "Flags müssen vollständig statisch" in item
                    for item in analyze_writer_source(source)
                ))

    def test_dangerous_open_flags_are_blocked(self) -> None:
        for flag in ("O_TRUNC", "O_APPEND", "O_TMPFILE"):
            with self.subTest(flag=flag):
                source = (
                    "import os\npartial_path='p'\n"
                    f"os.open(partial_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.{flag})"
                )
                self.assertTrue(any("verbotene Flags" in item for item in analyze_writer_source(source)))

    def test_write_path_must_be_explicit_partial_path(self) -> None:
        violations = analyze_writer_source(
            "import os\nfinal_path='f'\nos.open(final_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)"
        )
        self.assertTrue(any("partial_path" in item for item in violations))

    def test_os_write_must_use_exclusive_partial_fd(self) -> None:
        self.assertTrue(any("Partial-FD" in item for item in analyze_writer_source("import os\nos.write(7, b'x')")))

    def test_indirect_low_level_writes_are_blocked(self) -> None:
        for api in ("pwrite", "writev", "sendfile", "copy_file_range", "splice", "fdopen"):
            with self.subTest(api=api):
                self.assertTrue(analyze_writer_source(f"import os\nos.{api}(1, 2)"))

    def test_link_is_only_partial_to_final_and_no_symlink_follow(self) -> None:
        cases = (
            "import os\npartial_path='p'\nother_path='o'\nos.link(other_path, partial_path, follow_symlinks=False)",
            "import os\npartial_path='p'\nother_path='o'\nos.link(partial_path, other_path, follow_symlinks=False)",
            "import os\npartial_path='p'\nfinal_path='f'\nos.link(partial_path, final_path)",
        )
        for source in cases:
            with self.subTest(source=source):
                self.assertTrue(analyze_writer_source(source))

    def test_unlink_only_allows_explicit_partial_path(self) -> None:
        self.assertEqual(analyze_writer_source("import os\npartial_path='p'\nos.unlink(partial_path)"), ())
        self.assertTrue(any(
            "partial_path" in item
            for item in analyze_writer_source("import os\nfinal_path='f'\nos.unlink(final_path)")
        ))

    def test_high_level_writes_and_overwrite_publish_are_blocked(self) -> None:
        samples = (
            "open('x', 'wb')",
            "from pathlib import Path\nPath('x').write_bytes(b'x')",
            "import os\nos.replace('a', 'b')",
            "import os\nos.rename('a', 'b')",
        )
        for source in samples:
            with self.subTest(source=source):
                self.assertTrue(analyze_writer_source(source))

    def test_escape_hatch_imports_are_blocked(self) -> None:
        for module in ("socket", "subprocess", "tempfile", "ctypes", "mmap", "shutil", "io", "zipfile"):
            with self.subTest(module=module):
                self.assertTrue(any(
                    "Import im Writer verboten" in item
                    for item in analyze_writer_source(f"import {module}")
                ))


if __name__ == "__main__":
    unittest.main()
