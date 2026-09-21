from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from provoware_laientool.application_core import execute, prepare_target_directories
from provoware_laientool.capability_registry import (
    STATUS_OPEN,
    get_use_case,
    validate_registry,
)
from provoware_laientool.cli_shell import run_transfer_preview_flow


class I25ApplicationAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "Downloads"
        self.root.mkdir()
        self.source_dir = self.root / "Eingang"
        self.source_dir.mkdir()
        self.target = self.root / "Ziel"
        self.target.mkdir()
        self.nested_target = self.target / "Unter Ziel"
        self.nested_target.mkdir()
        (self.source_dir / "eins.txt").write_text("eins", encoding="utf-8")
        (self.source_dir / "zwei ä.txt").write_text("zwei", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_registry_keeps_transfer_previews_open_until_real_evidence(self) -> None:
        self.assertEqual(validate_registry(), ())
        for use_case_id in ("files.preview_copy", "files.preview_move"):
            entry = get_use_case(use_case_id)
            self.assertIsNotNone(entry)
            assert entry is not None
            self.assertEqual(entry.status, STATUS_OPEN)
            self.assertTrue(entry.gui_available)
            self.assertTrue(entry.cli_available)

    def test_shared_execute_copy_preview_is_read_only(self) -> None:
        result = execute(
            "files.preview_copy",
            root=str(self.root),
            selected_relative_paths=("Eingang/eins.txt",),
            target_dir=str(self.target),
        )
        self.assertEqual(result.status, "PASS")
        self.assertIn("Kopieren", result.body)
        self.assertIn("Es wurden keine Dateien verändert", result.body)
        self.assertFalse((self.target / "eins.txt").exists())

    def test_shared_execute_move_preview_preserves_selection_order(self) -> None:
        result = execute(
            "files.preview_move",
            root=str(self.root),
            selected_relative_paths=("Eingang/zwei ä.txt", "Eingang/eins.txt"),
            target_dir=str(self.target),
        )
        self.assertEqual(result.status, "PASS")
        self.assertLess(result.body.index("zwei ä.txt"), result.body.index("eins.txt"))
        self.assertTrue((self.source_dir / "eins.txt").exists())
        self.assertTrue((self.source_dir / "zwei ä.txt").exists())

    def test_external_target_is_blocked_through_same_core(self) -> None:
        outside = Path(self.temp.name) / "Extern"
        outside.mkdir()
        result = execute(
            "files.preview_copy",
            root=str(self.root),
            selected_relative_paths=("Eingang/eins.txt",),
            target_dir=str(outside),
        )
        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("Zielordner blockiert", result.body)

    def test_empty_selection_stays_open(self) -> None:
        result = execute(
            "files.preview_copy",
            root=str(self.root),
            selected_relative_paths=(),
            target_dir=str(self.target),
        )
        self.assertEqual(result.status, "OPEN")
        self.assertIn("Keine Datei ausgewählt", result.body)

    def test_cli_numeric_flow_uses_shared_result(self) -> None:
        answers = iter(
            [
                str(self.root),
                "1",
                "3",
            ]
        )
        output: list[str] = []
        status = run_transfer_preview_flow(
            "files.preview_copy",
            input_fn=lambda _: next(answers),
            output_fn=output.append,
        )
        self.assertEqual(status, "PASS")
        joined = "\n".join(output)
        self.assertIn("Kopieren – Vorschau – PASS", joined)
        self.assertIn("Es wurden keine Dateien verändert", joined)
        self.assertFalse((self.target / "eins.txt").exists())

    def test_target_directory_choices_are_same_root_only(self) -> None:
        outside = Path(self.temp.name) / "Extern"
        outside.mkdir()
        link = self.root / "Extern-Link"
        link.symlink_to(outside, target_is_directory=True)

        result = prepare_target_directories(self.root)
        self.assertEqual(result.status, "PASS")
        self.assertEqual(
            result.directories,
            (".", "Eingang", "Ziel", "Ziel/Unter Ziel"),
        )
        self.assertNotIn("Extern-Link", result.directories)

    def test_standard_cli_is_wired_for_future_ready_transfer_entries(self) -> None:
        source = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "provoware_laientool"
            / "cli_shell.py"
        ).read_text(encoding="utf-8")
        self.assertIn("if use_case_id in TRANSFER_PREVIEW_IDS:", source)
        self.assertIn("run_transfer_preview_flow(", source)

    def test_gui_source_exposes_only_evidence_mode_before_ready(self) -> None:
        source = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "provoware_laientool"
            / "gui_shell.py"
        ).read_text(encoding="utf-8")
        self.assertIn("evidence_mode: bool = False", source)
        self.assertIn("entry.id in TRANSFER_PREVIEW_IDS", source)
        self.assertIn("QAbstractItemView.ExtendedSelection", source)
        self.assertIn("QAbstractItemView.SingleSelection", source)
        self.assertIn("prepare_target_directories", source)
        self.assertNotIn(
            '"3/3 Zielordner innerhalb derselben Wurzel auswählen",\n                root,',
            source,
        )


if __name__ == "__main__":
    unittest.main()
