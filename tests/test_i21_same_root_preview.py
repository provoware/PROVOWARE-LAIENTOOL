from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from provoware_laientool.application_core import (
    prepare_copy_preview,
    prepare_move_preview,
)
from provoware_laientool.preview_model import ACTION_COPY, ACTION_MOVE


class SameRootCopyMovePreviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "Downloads"
        self.root.mkdir()
        self.source_dir = self.root / "unsortiert"
        self.source_dir.mkdir()
        self.target_dir = self.root / "Dokumente"
        self.target_dir.mkdir()
        self.source = self.source_dir / "datei.txt"
        self.source.write_text("abc", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_copy_preview_passes_without_writing(self) -> None:
        result = prepare_copy_preview(
            self.root,
            ("unsortiert/datei.txt",),
            self.target_dir,
        )

        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.errors, ())
        self.assertIsNotNone(result.plan)
        self.assertIsNotNone(result.check)
        assert result.plan is not None
        assert result.check is not None
        self.assertTrue(result.check.allowed)
        self.assertFalse(result.plan.writes_enabled)
        self.assertEqual(result.plan.total_items, 1)
        item = result.plan.items[0]
        self.assertEqual(item.action, ACTION_COPY)
        self.assertEqual(Path(item.source), self.source)
        self.assertEqual(Path(item.target or ""), self.target_dir / "datei.txt")
        self.assertTrue(item.reversible)
        self.assertTrue(self.source.exists())
        self.assertFalse((self.target_dir / "datei.txt").exists())

    def test_move_preview_passes_without_writing(self) -> None:
        result = prepare_move_preview(
            self.root,
            ("unsortiert/datei.txt",),
            self.target_dir,
        )

        self.assertEqual(result.status, "PASS")
        assert result.plan is not None
        self.assertEqual(result.plan.items[0].action, ACTION_MOVE)
        self.assertTrue(self.source.exists())
        self.assertFalse((self.target_dir / "datei.txt").exists())

    def test_existing_target_blocks_overwrite(self) -> None:
        existing = self.target_dir / "datei.txt"
        existing.write_text("bestehend", encoding="utf-8")

        result = prepare_copy_preview(
            self.root,
            ("unsortiert/datei.txt",),
            self.target_dir,
        )

        self.assertEqual(result.status, "BLOCKED")
        self.assertIsNone(result.plan)
        self.assertTrue(any("Ziel existiert bereits" in error for error in result.errors))
        self.assertEqual(existing.read_text(encoding="utf-8"), "bestehend")
        self.assertTrue(self.source.exists())

    def test_target_outside_root_is_blocked(self) -> None:
        outside = Path(self.temp.name) / "Extern"
        outside.mkdir()

        result = prepare_move_preview(
            self.root,
            ("unsortiert/datei.txt",),
            outside,
        )

        self.assertEqual(result.status, "BLOCKED")
        self.assertIsNone(result.plan)
        self.assertTrue(any("Zielordner blockiert" in error for error in result.errors))

    def test_symlink_target_directory_is_blocked(self) -> None:
        real_target = self.root / "Real"
        real_target.mkdir()
        link_target = self.root / "Link"
        link_target.symlink_to(real_target, target_is_directory=True)

        result = prepare_copy_preview(
            self.root,
            ("unsortiert/datei.txt",),
            link_target,
        )

        self.assertEqual(result.status, "BLOCKED")
        self.assertIsNone(result.plan)

    def test_target_must_be_existing_directory(self) -> None:
        missing = self.root / "missing"

        result = prepare_copy_preview(
            self.root,
            ("unsortiert/datei.txt",),
            missing,
        )

        self.assertEqual(result.status, "BLOCKED")
        self.assertIsNone(result.plan)

        file_target = self.root / "ziel.txt"
        file_target.write_text("x", encoding="utf-8")
        result = prepare_copy_preview(
            self.root,
            ("unsortiert/datei.txt",),
            file_target,
        )
        self.assertEqual(result.status, "BLOCKED")
        self.assertTrue(any("vorhandener Ordner" in error for error in result.errors))

    def test_source_equal_target_is_blocked(self) -> None:
        result = prepare_move_preview(
            self.root,
            ("unsortiert/datei.txt",),
            self.source_dir,
        )

        self.assertEqual(result.status, "BLOCKED")
        self.assertIsNone(result.plan)
        self.assertTrue(any("Quelle und Ziel sind identisch" in error for error in result.errors))

    def test_uninventoried_selection_is_blocked(self) -> None:
        result = prepare_copy_preview(
            self.root,
            ("missing.txt",),
            self.target_dir,
        )

        self.assertEqual(result.status, "BLOCKED")
        self.assertIsNone(result.plan)
        self.assertIn(
            "Auswahl nicht im aktuellen Inventar: missing.txt",
            result.errors,
        )

    def test_duplicate_selection_is_blocked(self) -> None:
        result = prepare_copy_preview(
            self.root,
            ("unsortiert/datei.txt", "unsortiert/datei.txt"),
            self.target_dir,
        )

        self.assertEqual(result.status, "BLOCKED")
        self.assertIsNone(result.plan)
        self.assertIn(
            "Doppelte Auswahl: unsortiert/datei.txt",
            result.errors,
        )

    def test_empty_selection_stays_open(self) -> None:
        result = prepare_copy_preview(self.root, (), self.target_dir)

        self.assertEqual(result.status, "OPEN")
        self.assertIsNone(result.plan)
        self.assertEqual(result.errors, ("Keine Datei ausgewählt.",))

    def test_missing_root_is_blocked(self) -> None:
        result = prepare_copy_preview(
            self.root / "missing",
            ("datei.txt",),
            self.target_dir,
        )

        self.assertEqual(result.status, "BLOCKED")
        self.assertIsNone(result.plan)

    def test_multiple_files_keep_deterministic_selection_order(self) -> None:
        second = self.source_dir / "ä zweite.txt"
        second.write_text("12345", encoding="utf-8")

        result = prepare_move_preview(
            self.root,
            ("unsortiert/ä zweite.txt", "unsortiert/datei.txt"),
            self.target_dir,
        )

        self.assertEqual(result.status, "PASS")
        assert result.plan is not None
        self.assertEqual(
            [Path(item.source).name for item in result.plan.items],
            ["ä zweite.txt", "datei.txt"],
        )
        self.assertEqual(result.plan.total_bytes_estimate, 8)
        self.assertFalse((self.target_dir / "ä zweite.txt").exists())
        self.assertFalse((self.target_dir / "datei.txt").exists())


if __name__ == "__main__":
    unittest.main()
