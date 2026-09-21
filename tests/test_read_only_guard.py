from __future__ import annotations

import unittest

from scripts.read_only_guard import (
    WRITER_RELATIVE,
    analyze_product_source,
    analyze_source,
    scan_product_tree,
)


class ReadOnlyGuardTests(unittest.TestCase):
    def test_current_product_tree_is_write_locked(self) -> None:
        self.assertEqual(scan_product_tree(), ())

    def test_path_write_text_is_blocked(self) -> None:
        violations = analyze_source("Path('x').write_text('data')")
        self.assertTrue(any("write_text" in item for item in violations))

    def test_os_rename_is_blocked(self) -> None:
        violations = analyze_source("import os\nos.rename('a', 'b')")
        self.assertTrue(any("os.rename" in item for item in violations))

    def test_shutil_copy_is_blocked(self) -> None:
        violations = analyze_source("import shutil\nshutil.copy('a', 'b')")
        self.assertTrue(any("shutil.copy" in item for item in violations))

    def test_import_alias_is_blocked(self) -> None:
        violations = analyze_source(
            "from shutil import move as mv\nmv('a', 'b')"
        )
        self.assertTrue(any("shutil.move" in item for item in violations))

    def test_module_alias_is_blocked(self) -> None:
        violations = analyze_source(
            "import os as operating\noperating.rename('a', 'b')"
        )
        self.assertTrue(any("os.rename" in item for item in violations))

    def test_low_level_write_primitives_are_blocked_outside_writer(self) -> None:
        samples = (
            "import os\nos.open('x', os.O_CREAT | os.O_EXCL | os.O_WRONLY)",
            "import os\nos.write(3, b'x')",
            "import os\nos.link('a', 'b')",
        )
        for source in samples:
            with self.subTest(source=source):
                self.assertTrue(analyze_source(source))

    def test_exact_writer_path_uses_specialized_guard(self) -> None:
        safe = (
            "import os\n"
            "partial_path = 'partial'\n"
            "final_path = 'final'\n"
            "partial_fd = os.open(partial_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)\n"
            "os.write(partial_fd, b'data')\n"
            "os.fsync(partial_fd)\n"
            "os.close(partial_fd)\n"
            "os.link(partial_path, final_path, follow_symlinks=False)\n"
            "os.unlink(partial_path)\n"
        )
        self.assertEqual(analyze_product_source(WRITER_RELATIVE, safe), ())
        self.assertTrue(
            analyze_product_source("src/provoware_laientool/other.py", safe)
        )

    def test_open_write_mode_is_blocked(self) -> None:
        violations = analyze_source("open('x', 'wb')")
        self.assertTrue(any("schreibender open" in item for item in violations))

    def test_dynamic_open_mode_fails_closed(self) -> None:
        violations = analyze_source("mode = 'rb'\nopen('x', mode)")
        self.assertTrue(any("nicht statisch" in item for item in violations))

    def test_read_only_open_mode_is_allowed(self) -> None:
        self.assertEqual(analyze_source("open('x', 'rb')"), ())

    def test_string_replace_is_allowed(self) -> None:
        self.assertEqual(
            analyze_source("value = 'a-b'.replace('-', '')"),
            (),
        )

    def test_path_replace_is_blocked(self) -> None:
        violations = analyze_source(
            "from pathlib import Path\np = Path('a')\np.replace('b')"
        )
        self.assertTrue(any("Path-Schreib-API .replace" in item for item in violations))

    def test_derived_path_replace_is_blocked(self) -> None:
        violations = analyze_source(
            "from pathlib import Path\nroot = Path('a')\ntarget = root / 'b'\ntarget.replace('c')"
        )
        self.assertTrue(any("Path-Schreib-API .replace" in item for item in violations))

    def test_plain_read_only_code_is_allowed(self) -> None:
        self.assertEqual(analyze_source("value = Path('x').exists()"), ())


if __name__ == "__main__":
    unittest.main()
