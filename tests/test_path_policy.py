from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from provoware_laientool.path_policy import validate_existing_root, validate_path


class PathPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "Downloads"
        self.root.mkdir()
        (self.root / "normal.txt").write_text("ok", encoding="utf-8")
        (self.root / "Unter Ordner").mkdir()
        (self.root / "Unter Ordner" / "größer.txt").write_text("ok", encoding="utf-8")
        self.outside = self.base / "outside.txt"
        self.outside.write_text("outside", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_explicit_root_is_valid(self) -> None:
        self.assertTrue(validate_existing_root(self.root).allowed)

    def test_normal_child_is_allowed(self) -> None:
        self.assertTrue(validate_path(self.root, Path("normal.txt")).allowed)

    def test_unicode_and_spaces_are_allowed_inside_root(self) -> None:
        self.assertTrue(validate_path(self.root, Path("Unter Ordner") / "größer.txt").allowed)

    def test_parent_traversal_is_blocked(self) -> None:
        self.assertFalse(validate_path(self.root, Path("..") / "outside.txt").allowed)

    def test_absolute_outside_path_is_blocked(self) -> None:
        self.assertFalse(validate_path(self.root, self.outside).allowed)

    @unittest.skipUnless(hasattr(os, "symlink"), "Symlinks werden nicht unterstützt")
    def test_symlink_inside_root_is_blocked_by_default(self) -> None:
        link = self.root / "link"
        link.symlink_to(self.root / "normal.txt")
        self.assertFalse(validate_path(self.root, link).allowed)

    @unittest.skipUnless(hasattr(os, "symlink"), "Symlinks werden nicht unterstützt")
    def test_symlink_escape_is_blocked_even_when_symlink_allowed(self) -> None:
        link = self.root / "escape"
        link.symlink_to(self.outside)
        self.assertFalse(validate_path(self.root, link, allow_symlink=True).allowed)

    @unittest.skipUnless(hasattr(os, "symlink"), "Symlinks werden nicht unterstützt")
    def test_broken_symlink_is_blocked(self) -> None:
        link = self.root / "broken"
        link.symlink_to(self.base / "missing-target")
        self.assertFalse(validate_path(self.root, link).allowed)

    def test_missing_path_is_blocked_by_default(self) -> None:
        self.assertFalse(validate_path(self.root, Path("missing.txt")).allowed)

    def test_missing_child_can_be_planned_without_creation(self) -> None:
        self.assertTrue(validate_path(self.root, Path("future.txt"), must_exist=False).allowed)

    def test_nonexistent_root_is_blocked(self) -> None:
        self.assertFalse(validate_existing_root(self.base / "missing-root").allowed)


if __name__ == "__main__":
    unittest.main()
