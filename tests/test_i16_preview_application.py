from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from provoware_laientool import cli_shell, gui_shell
from provoware_laientool.application_core import (
    action_requires_root,
    execute,
    prepare_trash_preview,
)
from provoware_laientool.inventory import (
    ISSUE_ACCESS_ERROR,
    InventoryIssue,
    InventoryResult,
)
from provoware_laientool.preview_model import ACTION_TRASH, validate_preview


class PreviewApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "Downloads"
        self.root.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_inventory_files_become_reversible_trash_preview(self) -> None:
        (self.root / "a.txt").write_bytes(b"abc")
        folder = self.root / "Unter Ordner"
        folder.mkdir()
        (folder / "ü b.png").write_bytes(b"12345")

        preparation = prepare_trash_preview(self.root)

        self.assertEqual(preparation.status, "PASS")
        self.assertIsNotNone(preparation.plan)
        self.assertIsNotNone(preparation.check)
        assert preparation.plan is not None
        assert preparation.check is not None

        self.assertTrue(preparation.check.allowed)
        self.assertEqual(preparation.plan.total_items, 2)
        self.assertEqual(preparation.plan.total_bytes_estimate, 8)
        self.assertFalse(preparation.plan.writes_enabled)
        self.assertTrue(all(item.action == ACTION_TRASH for item in preparation.plan.items))
        self.assertTrue(all(item.target is None for item in preparation.plan.items))
        self.assertTrue(all(item.reversible for item in preparation.plan.items))
        self.assertTrue(validate_preview(preparation.plan).allowed)

    def test_incomplete_inventory_never_becomes_preview_plan(self) -> None:
        incomplete = InventoryResult(
            root=str(self.root),
            root_allowed=True,
            items=(),
            issues=(
                InventoryIssue(
                    ISSUE_ACCESS_ERROR,
                    "blocked",
                    "Ordner konnte nicht gelesen werden.",
                ),
            ),
        )

        with patch(
            "provoware_laientool.application_core.scan_inventory",
            return_value=incomplete,
        ):
            preparation = prepare_trash_preview(self.root)

        self.assertEqual(preparation.status, "OPEN")
        self.assertIsNone(preparation.plan)
        self.assertIsNone(preparation.check)

    def test_missing_root_is_blocked(self) -> None:
        preparation = prepare_trash_preview(self.root / "missing")

        self.assertEqual(preparation.status, "BLOCKED")
        self.assertFalse(preparation.inventory.root_allowed)
        self.assertIsNone(preparation.plan)

    def test_execute_without_explicit_root_stays_open(self) -> None:
        result = execute("files.preview_trash")

        self.assertEqual(result.status, "OPEN")
        self.assertIn("kein Ordner ausgewählt", result.body)
        self.assertIn("keine Datei verändert", result.body)

    def test_execute_formats_valid_preview_without_writing(self) -> None:
        source = self.root / "Datei mit Leerzeichen.txt"
        source.write_bytes(b"data")

        result = execute("files.preview_trash", root=str(self.root))

        self.assertEqual(result.status, "PASS")
        self.assertIn("Reine Vorschau", result.body)
        self.assertIn("Datei mit Leerzeichen.txt", result.body)
        self.assertIn("Ein Executor ist weiterhin gesperrt", result.body)
        self.assertTrue(source.exists())


class SharedAdapterContractTests(unittest.TestCase):
    def test_preview_use_case_requires_root_in_shared_core(self) -> None:
        self.assertTrue(action_requires_root("files.preview_trash"))
        self.assertFalse(action_requires_root("app.overview"))

    def test_gui_and_cli_do_not_duplicate_inventory_preview_logic(self) -> None:
        for module in (cli_shell, gui_shell):
            source = inspect.getsource(module)
            self.assertNotIn("scan_inventory", source)
            self.assertNotIn("PreviewItem", source)
            self.assertNotIn("make_plan", source)
            self.assertIn("action_requires_root", source)
            self.assertIn("execute", source)

    def test_preview_is_exposed_in_numeric_menu(self) -> None:
        ids = {use_case_id for _, use_case_id, _ in cli_shell.menu_entries()}
        self.assertIn("files.preview_trash", ids)

    def test_cli_collects_root_and_uses_same_application_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Downloads"
            root.mkdir()
            (root / "test.txt").write_text("test", encoding="utf-8")

            entry_number = next(
                number
                for number, use_case_id, _ in cli_shell.menu_entries()
                if use_case_id == "files.preview_trash"
            )
            answers = iter((str(entry_number), str(root), "", "0"))
            output: list[str] = []

            result = cli_shell.run(
                input_fn=lambda prompt: next(answers),
                output_fn=output.append,
            )

        self.assertEqual(result, 0)
        rendered = "\n".join(output)
        self.assertIn("Dateivorschau – PASS", rendered)
        self.assertIn("Reine Vorschau", rendered)


if __name__ == "__main__":
    unittest.main()
