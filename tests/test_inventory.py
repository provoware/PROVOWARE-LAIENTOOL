from __future__ import annotations

import os
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import patch

from provoware_laientool.inventory import (
    ISSUE_ACCESS_ERROR,
    ISSUE_ROOT_BLOCKED,
    ISSUE_SYMLINK_BLOCKED,
    InventoryItem,
    scan_inventory,
)


class InventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "Downloads"
        self.root.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_nested_unicode_and_spaces_are_inventoried_read_only(self) -> None:
        folder = self.root / "Unter Ordner"
        folder.mkdir()
        first = self.root / "ä Datei.txt"
        second = folder / "Bild 01.png"
        first.write_bytes(b"abc")
        second.write_bytes(b"12345")

        result = scan_inventory(self.root)

        self.assertTrue(result.root_allowed)
        self.assertTrue(result.complete)
        self.assertEqual(result.file_count, 2)
        self.assertEqual(result.total_bytes, 8)
        self.assertEqual(
            [item.relative_path for item in result.items],
            ["Unter Ordner/Bild 01.png", "ä Datei.txt"],
        )
        self.assertTrue(first.exists())
        self.assertTrue(second.exists())

    def test_items_are_immutable(self) -> None:
        item = InventoryItem("datei.txt", 3)
        with self.assertRaises(FrozenInstanceError):
            item.size_bytes = 4  # type: ignore[misc]

    def test_symlink_is_reported_and_never_followed(self) -> None:
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_bytes(b"secret")
        link = self.root / "outside-link"
        link.symlink_to(outside)

        result = scan_inventory(self.root)

        self.assertEqual(result.file_count, 0)
        self.assertTrue(result.complete)
        self.assertEqual(len(result.issues), 1)
        self.assertEqual(result.issues[0].code, ISSUE_SYMLINK_BLOCKED)
        self.assertEqual(result.issues[0].relative_path, "outside-link")

    def test_missing_root_fails_closed(self) -> None:
        result = scan_inventory(self.root / "missing")

        self.assertFalse(result.root_allowed)
        self.assertFalse(result.complete)
        self.assertEqual(result.items, ())
        self.assertEqual(result.issues[0].code, ISSUE_ROOT_BLOCKED)

    def test_result_order_is_deterministic(self) -> None:
        for name in ("z.txt", "A.txt", "b.txt"):
            (self.root / name).write_text(name, encoding="utf-8")

        first = scan_inventory(self.root)
        second = scan_inventory(self.root)

        self.assertEqual(first.items, second.items)
        self.assertEqual(
            [item.relative_path for item in first.items],
            ["A.txt", "b.txt", "z.txt"],
        )

    def test_directory_read_error_is_reported_without_aborting_root(self) -> None:
        safe = self.root / "safe.txt"
        safe.write_text("ok", encoding="utf-8")
        blocked = self.root / "blocked"
        blocked.mkdir()

        real_scandir = os.scandir

        def guarded_scandir(path: os.PathLike[str] | str):
            if Path(path) == blocked:
                raise PermissionError("test-denied")
            return real_scandir(path)

        with patch("provoware_laientool.inventory.os.scandir", side_effect=guarded_scandir):
            result = scan_inventory(self.root)

        self.assertEqual(result.file_count, 1)
        self.assertFalse(result.complete)
        self.assertTrue(any(issue.code == ISSUE_ACCESS_ERROR for issue in result.issues))
        self.assertTrue(safe.exists())


if __name__ == "__main__":
    unittest.main()
