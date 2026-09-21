from __future__ import annotations

import unittest
from unittest.mock import patch

from provoware_laientool.application_core import available_actions, execute
from provoware_laientool.capability_registry import (
    REGISTRY,
    validate_registry,
)
from provoware_laientool.cli_shell import menu_entries, render_menu
from provoware_laientool.ui_themes import THEMES, get_theme, stylesheet


class ApplicationCoreTests(unittest.TestCase):
    def test_ready_actions_are_registry_driven(self) -> None:
        expected = tuple(entry.id for entry in REGISTRY if entry.status == "READY")
        self.assertEqual(available_actions(), expected)

    def test_unknown_action_is_safe_open(self) -> None:
        result = execute("unknown.action")
        self.assertEqual(result.status, "OPEN")
        self.assertIn("keine Datei verändert", result.body)

    def test_overview_is_read_only_clear(self) -> None:
        result = execute("app.overview")
        self.assertEqual(result.status, "PASS")
        self.assertIn("Sicherer Lese-Modus", result.body)
        self.assertIn("verändert keine Dateien", result.body)


class AdapterParityTests(unittest.TestCase):
    def test_every_gui_ready_function_has_cli_path(self) -> None:
        cli_ids = {use_case_id for _, use_case_id, _ in menu_entries()}
        for entry in REGISTRY:
            if entry.gui_available and entry.status == "READY":
                self.assertIn(entry.id, cli_ids)

    def test_numeric_menu_has_zero_exit_and_registry_labels(self) -> None:
        rendered = render_menu()
        self.assertIn("0  Beenden", rendered)
        for _, _, label in menu_entries():
            self.assertIn(label, rendered)

    def test_registry_contract_remains_green(self) -> None:
        self.assertEqual(validate_registry(), ())


class ThemeTests(unittest.TestCase):
    def test_exactly_four_theme_families_exist(self) -> None:
        self.assertEqual(len(THEMES), 4)
        self.assertEqual(len({theme.id for theme in THEMES}), 4)

    def test_scale_is_clamped_to_supported_range(self) -> None:
        theme = get_theme("purple-neon")
        low = stylesheet(theme, 50)
        normal = stylesheet(theme, 100)
        high = stylesheet(theme, 300)
        maxed = stylesheet(theme, 200)
        self.assertEqual(low, normal)
        self.assertEqual(high, maxed)


if __name__ == "__main__":
    unittest.main()
