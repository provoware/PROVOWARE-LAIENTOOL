from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, replace

from provoware_laientool.capability_registry import (
    REGISTRY,
    SAFETY_READ_ONLY,
    STATUS_READY,
    UseCaseCapability,
    get_use_case,
    list_use_cases,
    validate_registry,
)


class CapabilityRegistryTests(unittest.TestCase):
    def test_default_registry_contract_is_green(self) -> None:
        self.assertEqual(validate_registry(), ())

    def test_registry_is_immutable_tuple(self) -> None:
        self.assertIsInstance(REGISTRY, tuple)
        with self.assertRaises(FrozenInstanceError):
            REGISTRY[0].label = "Geändert"  # type: ignore[misc]

    def test_preflight_is_ready_read_only_in_gui_and_cli(self) -> None:
        entry = get_use_case("system.preflight")
        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry.status, STATUS_READY)
        self.assertEqual(entry.safety_class, SAFETY_READ_ONLY)
        self.assertTrue(entry.cli_available)
        self.assertTrue(entry.gui_available)
        self.assertFalse(entry.diagnostic_cli_only)

    def test_gui_without_cli_is_rejected(self) -> None:
        invalid = replace(
            REGISTRY[0],
            id="files.search",
            gui_available=True,
            cli_available=False,
            diagnostic_cli_only=False,
        )
        self.assertIn(
            "GUI-Fachfunktion ohne CLI-Parität: files.search",
            validate_registry((invalid,)),
        )

    def test_duplicate_ids_are_rejected(self) -> None:
        duplicate = replace(REGISTRY[0])
        errors = validate_registry((REGISTRY[0], duplicate))
        self.assertIn(f"Doppelte Funktions-ID: {REGISTRY[0].id}", errors)

    def test_recovery_without_preview_is_rejected(self) -> None:
        invalid = UseCaseCapability(
            id="files.organize",
            label="Dateien organisieren",
            gui_available=False,
            cli_available=False,
            diagnostic_cli_only=False,
            safety_class="recovery-required",
            preview_required=False,
            recovery_required=True,
            required_capability=None,
            status="OPEN",
        )
        self.assertIn(
            "Recovery-Pflicht ohne Preview-Pflicht: files.organize",
            validate_registry((invalid,)),
        )

    def test_list_use_cases_returns_registry(self) -> None:
        self.assertIs(list_use_cases(), REGISTRY)


if __name__ == "__main__":
    unittest.main()
