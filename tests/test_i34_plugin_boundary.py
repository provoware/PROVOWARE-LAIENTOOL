from __future__ import annotations

import unittest

from provoware_laientool.plugin_contract import (
    PLUGIN_API_VERSION,
    PluginManifest,
    approved_plugin_use_cases,
    validate_plugin_manifest,
)
from scripts.plugin_boundary_guard import analyze_source


class I34PluginBoundaryTests(unittest.TestCase):
    def manifest(self, **changes) -> PluginManifest:
        data = {
            "plugin_id": "demo.readonly",
            "name": "Demo Read-only",
            "version": "1.0.0",
            "api_version": PLUGIN_API_VERSION,
            "requested_use_cases": ("system.preflight",),
        }
        data.update(changes)
        return PluginManifest(**data)

    def test_only_ready_read_only_use_cases_are_approved(self) -> None:
        approved = approved_plugin_use_cases()
        self.assertIn("system.preflight", approved)
        self.assertIn("app.help", approved)
        self.assertNotIn("files.preview_copy", approved)
        self.assertNotIn("diagnostics.export_local", approved)

    def test_data_only_disabled_manifest_passes(self) -> None:
        result = validate_plugin_manifest(self.manifest())
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.approved_use_cases, ("system.preflight",))

    def test_open_use_case_is_blocked(self) -> None:
        result = validate_plugin_manifest(
            self.manifest(requested_use_cases=("files.preview_copy",))
        )
        self.assertEqual(result.status, "BLOCKED")
        self.assertTrue(any("nicht READY" in item for item in result.errors))

    def test_write_use_case_is_blocked(self) -> None:
        result = validate_plugin_manifest(
            self.manifest(requested_use_cases=("diagnostics.export_local",))
        )
        self.assertEqual(result.status, "BLOCKED")

    def test_unknown_and_duplicate_capabilities_are_blocked(self) -> None:
        result = validate_plugin_manifest(
            self.manifest(
                requested_use_cases=(
                    "system.preflight",
                    "system.preflight",
                    "unknown.capability",
                )
            )
        )
        self.assertEqual(result.status, "BLOCKED")
        self.assertTrue(any("Doppelte" in item for item in result.errors))
        self.assertTrue(any("Unbekannter" in item for item in result.errors))

    def test_auto_install_auto_enable_network_and_entrypoint_are_blocked(self) -> None:
        result = validate_plugin_manifest(
            self.manifest(
                auto_install=True,
                auto_enable=True,
                network_required=True,
                entrypoint="pkg.module:main",
            )
        )
        self.assertEqual(result.status, "BLOCKED")
        joined = "\n".join(result.errors)
        self.assertIn("Auto-Install", joined)
        self.assertIn("Auto-Aktivierung", joined)
        self.assertIn("Netzwerkbedarf", joined)
        self.assertIn("Entry-Points", joined)

    def test_dynamic_loading_markers_are_guarded(self) -> None:
        samples = (
            "import importlib\nimportlib.import_module('x')\n",
            "from importlib import util\nutil.spec_from_file_location('x','y')\n",
            "__import__('x')\n",
            "import requests\n",
            "entry_points()\n",
        )
        for source in samples:
            self.assertTrue(analyze_source(source))

    def test_preflight_importlib_find_spec_is_allowed(self) -> None:
        source = (
            "import importlib.util\n"
            "available = importlib.util.find_spec('PySide6') is not None\n"
        )
        self.assertEqual(analyze_source(source), ())

    def test_normal_static_import_is_allowed(self) -> None:
        self.assertEqual(analyze_source("from pathlib import Path\n"), ())


if __name__ == "__main__":
    unittest.main()
