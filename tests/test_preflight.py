from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from provoware_laientool.preflight import (
    CapabilityInfo,
    PlatformInfo,
    choose_start_plan,
    collect_capabilities,
    collect_platform_info,
    discover_downloads_dir,
    evaluate,
    parse_os_release,
    read_os_release,
    runtime_source,
)


def info(**changes: str) -> PlatformInfo:
    values = dict(
        system="Linux",
        release="6.8.0",
        machine="x86_64",
        python="3.12.3",
        distro_id="ubuntu",
        distro_name="Ubuntu 24.04 LTS",
        distro_version="24.04",
        desktop="KDE",
        session_type="x11",
        filesystem_encoding="utf-8",
        runtime_source="system",
    )
    values.update(changes)
    return PlatformInfo(**values)


def caps(**changes: bool) -> CapabilityInfo:
    values = dict(
        linux=True,
        supported_distro_family=True,
        python_supported=True,
        graphical_session=True,
        pyside6_available=True,
        utf8_filesystem=True,
        home_available=True,
        downloads_available=True,
        project_readable=True,
    )
    values.update(changes)
    return CapabilityInfo(**values)


class OsReleaseTests(unittest.TestCase):
    def test_parse_os_release_handles_quotes_and_comments(self) -> None:
        parsed = parse_os_release(
            '# comment\nID=ubuntu\nVERSION_ID="24.04"\nPRETTY_NAME="Ubuntu 24.04 LTS"\n'
        )
        self.assertEqual(parsed["ID"], "ubuntu")
        self.assertEqual(parsed["VERSION_ID"], "24.04")

    def test_read_missing_os_release_is_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(read_os_release(Path(temp) / "missing"), {})

    def test_collect_accepts_injected_facts(self) -> None:
        value = collect_platform_info(
            {"ID": "kubuntu", "VERSION_ID": "24.04", "PRETTY_NAME": "Kubuntu 24.04 LTS"},
            {"XDG_CURRENT_DESKTOP": "KDE", "XDG_SESSION_TYPE": "x11"},
        )
        self.assertEqual(value.distro_id, "kubuntu")
        self.assertEqual(value.desktop, "KDE")

    def test_runtime_source_detects_venv(self) -> None:
        self.assertEqual(runtime_source("/tmp/venv", "/usr"), "venv")


class PortableDiscoveryTests(unittest.TestCase):
    def test_xdg_downloads_is_resolved_read_only(self) -> None:
        home = Path("/home/test user")
        result = discover_downloads_dir(
            home,
            'XDG_DOWNLOAD_DIR="$HOME/My Downloads"\n',
        )
        self.assertEqual(result, home / "My Downloads")

    def test_downloads_falls_back_to_home_downloads(self) -> None:
        home = Path("/home/test")
        self.assertEqual(discover_downloads_dir(home, ""), home / "Downloads")


class CapabilityTests(unittest.TestCase):
    def test_capabilities_use_injected_paths_and_gui_fact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            value = collect_capabilities(
                info(),
                home=root,
                downloads=root,
                project_root=root,
                pyside6_available=True,
            )
        self.assertTrue(value.home_available)
        self.assertTrue(value.downloads_available)
        self.assertTrue(value.project_readable)
        self.assertTrue(value.pyside6_available)


class PlanTests(unittest.TestCase):
    def test_gui_ready_when_everything_is_present(self) -> None:
        plan = choose_start_plan(info(), caps())
        self.assertEqual(plan.profile, "gui-ready")
        self.assertTrue(plan.gui_possible)

    def test_cli_fallback_when_gui_dependency_is_missing(self) -> None:
        plan = choose_start_plan(info(), caps(pyside6_available=False))
        self.assertEqual(plan.profile, "preflight-cli")
        self.assertFalse(plan.gui_possible)

    def test_blocked_when_core_capability_is_missing(self) -> None:
        plan = choose_start_plan(info(), caps(home_available=False))
        self.assertEqual(plan.profile, "blocked-readonly")

    def test_bundled_runtime_is_preferred_for_portability(self) -> None:
        plan = choose_start_plan(info(runtime_source="bundled"), caps())
        self.assertTrue(plan.portable_runtime_preferred)

    def test_other_distribution_stays_open(self) -> None:
        result = evaluate(
            info(distro_id="debian", distro_version="13"),
            caps(supported_distro_family=False),
        )
        self.assertEqual(result.status, "OPEN")


if __name__ == "__main__":
    unittest.main()
