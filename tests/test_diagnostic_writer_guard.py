from __future__ import annotations

import unittest

from scripts.diagnostic_writer_guard import analyze_writer_source


def safe_writer() -> str:
    return (
        "import os\n"
        "target_dir = '.'\n"
        "partial_name = 'partial'\n"
        "final_name = 'final'\n"
        "target_dir_fd = os.open(target_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)\n"
        "partial_fd = os.open(partial_name, os.O_CREAT | os.O_EXCL | os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600, dir_fd=target_dir_fd)\n"
        "os.write(partial_fd, b'data')\n"
        "os.fsync(partial_fd)\n"
        "os.close(partial_fd)\n"
        "os.link(partial_name, final_name, src_dir_fd=target_dir_fd, dst_dir_fd=target_dir_fd, follow_symlinks=False)\n"
        "os.unlink(partial_name, dir_fd=target_dir_fd)\n"
    )


class DiagnosticWriterGuardTests(unittest.TestCase):
    def test_exact_dirfd_no_clobber_sequence_is_allowed(self) -> None:
        self.assertEqual(analyze_writer_source(safe_writer()), ())

    def test_target_directory_fd_requires_exact_safe_flags(self) -> None:
        source = (
            "import os\ntarget_dir='.'\n"
            "target_dir_fd=os.open(target_dir, os.O_RDONLY | os.O_DIRECTORY)"
        )
        self.assertTrue(any("target_dir_fd braucht exakt" in item for item in analyze_writer_source(source)))

    def test_directory_open_requires_target_role(self) -> None:
        source = (
            "import os\nother_dir='.'\n"
            "target_dir_fd=os.open(other_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)"
        )
        self.assertTrue(any("target_dir" in item for item in analyze_writer_source(source)))

    def test_partial_create_requires_safe_directory_fd(self) -> None:
        source = (
            "import os\npartial_name='p'\n"
            "partial_fd=os.open(partial_name, os.O_CREAT | os.O_EXCL | os.O_RDWR)"
        )
        self.assertTrue(any("target_dir_fd" in item for item in analyze_writer_source(source)))

    def test_unknown_directory_fd_is_blocked(self) -> None:
        source = (
            "import os\npartial_name='p'\nunknown_fd=7\n"
            "partial_fd=os.open(partial_name, os.O_CREAT | os.O_EXCL | os.O_RDWR, dir_fd=unknown_fd)"
        )
        self.assertTrue(any("target_dir_fd" in item for item in analyze_writer_source(source)))

    def test_dynamic_or_numeric_flags_fail_closed(self) -> None:
        cases = (
            "import os\npartial_name='p'\nflags=os.O_CREAT|os.O_EXCL|os.O_RDWR\nos.open(partial_name, flags)",
            "import os\npartial_name='p'\nos.open(partial_name, 194)",
        )
        for source in cases:
            with self.subTest(source=source):
                self.assertTrue(any(
                    "Flags müssen vollständig statisch" in item
                    for item in analyze_writer_source(source)
                ))

    def test_dangerous_open_flags_are_blocked(self) -> None:
        prefix = (
            "import os\ntarget_dir='.'\npartial_name='p'\n"
            "target_dir_fd=os.open(target_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)\n"
        )
        for flag in ("O_TRUNC", "O_APPEND", "O_TMPFILE"):
            with self.subTest(flag=flag):
                source = prefix + (
                    f"os.open(partial_name, os.O_CREAT | os.O_EXCL | os.O_RDWR | os.{flag}, "
                    "dir_fd=target_dir_fd)"
                )
                self.assertTrue(any("verbotene Flags" in item for item in analyze_writer_source(source)))

    def test_os_write_must_use_proven_partial_fd(self) -> None:
        self.assertTrue(any(
            "Partial-FD" in item for item in analyze_writer_source("import os\nos.write(7, b'x')")
        ))

    def test_link_requires_same_safe_dirfd(self) -> None:
        prefix = (
            "import os\ntarget_dir='.'\npartial_name='p'\nfinal_name='f'\n"
            "target_dir_fd=os.open(target_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)\n"
        )
        bad = prefix + (
            "os.link(partial_name, final_name, src_dir_fd=target_dir_fd, "
            "dst_dir_fd=other_fd, follow_symlinks=False)"
        )
        self.assertTrue(any("denselben sicheren target_dir_fd" in item for item in analyze_writer_source(bad)))

    def test_link_requires_partial_to_final_and_nofollow(self) -> None:
        prefix = (
            "import os\ntarget_dir='.'\npartial_name='p'\nfinal_name='f'\nother_name='o'\n"
            "target_dir_fd=os.open(target_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)\n"
        )
        cases = (
            prefix + "os.link(other_name, final_name, src_dir_fd=target_dir_fd, dst_dir_fd=target_dir_fd, follow_symlinks=False)",
            prefix + "os.link(partial_name, other_name, src_dir_fd=target_dir_fd, dst_dir_fd=target_dir_fd, follow_symlinks=False)",
            prefix + "os.link(partial_name, final_name, src_dir_fd=target_dir_fd, dst_dir_fd=target_dir_fd)",
        )
        for source in cases:
            with self.subTest(source=source):
                self.assertTrue(analyze_writer_source(source))

    def test_unlink_requires_owned_partial_and_safe_dirfd(self) -> None:
        prefix = (
            "import os\ntarget_dir='.'\npartial_name='p'\nfinal_name='f'\n"
            "target_dir_fd=os.open(target_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)\n"
        )
        self.assertEqual(
            analyze_writer_source(prefix + "os.unlink(partial_name, dir_fd=target_dir_fd)"),
            (),
        )
        self.assertTrue(analyze_writer_source(prefix + "os.unlink(final_name, dir_fd=target_dir_fd)"))
        self.assertTrue(analyze_writer_source("import os\npartial_name='p'\nos.unlink(partial_name)"))

    def test_indirect_low_level_writes_are_blocked(self) -> None:
        for api in ("pwrite", "writev", "sendfile", "copy_file_range", "splice", "fdopen"):
            with self.subTest(api=api):
                self.assertTrue(analyze_writer_source(f"import os\nos.{api}(1, 2)"))

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
