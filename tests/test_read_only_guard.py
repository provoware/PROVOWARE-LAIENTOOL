from __future__ import annotations

import unittest

from scripts.read_only_guard import analyze_source, scan_product_tree


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

    def test_open_write_mode_is_blocked(self) -> None:
        violations = analyze_source("open('x', 'wb')")
        self.assertTrue(any("schreibender open" in item for item in violations))

    def test_dynamic_open_mode_fails_closed(self) -> None:
        violations = analyze_source("mode = 'rb'\nopen('x', mode)")
        self.assertTrue(any("nicht statisch" in item for item in violations))

    def test_read_only_open_mode_is_allowed(self) -> None:
        self.assertEqual(analyze_source("open('x', 'rb')"), ())

    def test_plain_read_only_code_is_allowed(self) -> None:
        self.assertEqual(analyze_source("value = Path('x').exists()"), ())


if __name__ == "__main__":
    unittest.main()
