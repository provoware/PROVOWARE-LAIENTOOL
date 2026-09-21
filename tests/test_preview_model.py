from __future__ import annotations

import tempfile
import unittest
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

from provoware_laientool.preview_model import (
    ACTION_COPY,
    ACTION_MOVE,
    ACTION_TRASH,
    PreviewItem,
    make_plan,
    validate_preview,
)


class PreviewModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "Downloads"
        self.root.mkdir()
        (self.root / "quelle.txt").write_text("abc", encoding="utf-8")
        (self.root / "Unter Ordner").mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def item(self, **changes: object) -> PreviewItem:
        values: dict[str, object] = {
            "id": "op-001",
            "action": ACTION_MOVE,
            "source": "quelle.txt",
            "target": "Unter Ordner/quelle.txt",
            "bytes_estimate": 3,
            "effect": "Datei würde in den Unterordner verschoben.",
            "reversible": True,
            "recovery_hint": "Später über Recovery an den Ursprungsort zurückführen.",
        }
        values.update(changes)
        return PreviewItem(**values)  # type: ignore[arg-type]

    def test_plan_and_items_are_immutable(self) -> None:
        item = self.item()
        plan = make_plan(self.root, (item,))
        with self.assertRaises(FrozenInstanceError):
            item.effect = "anders"  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            plan.total_items = 2  # type: ignore[misc]

    def test_valid_move_preview_passes_without_writes(self) -> None:
        plan = make_plan(self.root, (self.item(),))
        check = validate_preview(plan)
        self.assertTrue(check.allowed)
        self.assertFalse(plan.writes_enabled)
        self.assertFalse((self.root / "Unter Ordner" / "quelle.txt").exists())

    def test_copy_requires_target_inside_root(self) -> None:
        outside = Path(self.temp.name) / "outside.txt"
        item = self.item(action=ACTION_COPY, target=str(outside))
        check = validate_preview(make_plan(self.root, (item,)))
        self.assertFalse(check.allowed)
        self.assertTrue(any("Ziel blockiert" in error for error in check.errors))

    def test_source_must_exist(self) -> None:
        item = self.item(source="missing.txt")
        check = validate_preview(make_plan(self.root, (item,)))
        self.assertFalse(check.allowed)
        self.assertTrue(any("Quelle blockiert" in error for error in check.errors))

    def test_move_must_be_reversible(self) -> None:
        invalid = self.item(action=ACTION_MOVE, reversible=False)
        check = validate_preview(make_plan(self.root, (invalid,)))
        self.assertFalse(check.allowed)
        self.assertIn("Move muss als reversibel markiert sein: op-001", check.errors)

    def test_trash_is_reversible_and_has_no_free_target(self) -> None:
        valid = self.item(
            action=ACTION_TRASH,
            target=None,
            reversible=True,
            effect="Datei würde in einen reversiblen Papierkorbzustand überführt.",
        )
        self.assertTrue(validate_preview(make_plan(self.root, (valid,))).allowed)

        invalid = replace(valid, reversible=False)
        check = validate_preview(make_plan(self.root, (invalid,)))
        self.assertFalse(check.allowed)
        self.assertIn("Trash muss als reversibel markiert sein: op-001", check.errors)

    def test_duplicate_ids_are_blocked(self) -> None:
        first = self.item()
        second = replace(first)
        check = validate_preview(make_plan(self.root, (first, second)))
        self.assertFalse(check.allowed)
        self.assertIn("Doppelte Preview-ID: op-001", check.errors)

    def test_negative_size_is_blocked(self) -> None:
        check = validate_preview(
            make_plan(self.root, (self.item(bytes_estimate=-1),))
        )
        self.assertFalse(check.allowed)
        self.assertIn("Negative Größenangabe bei op-001.", check.errors)

    def test_identical_source_and_target_are_blocked(self) -> None:
        check = validate_preview(
            make_plan(self.root, (self.item(target="quelle.txt"),))
        )
        self.assertFalse(check.allowed)
        self.assertIn("Quelle und Ziel sind identisch bei op-001.", check.errors)


if __name__ == "__main__":
    unittest.main()
