from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from provoware_laientool.preflight import (
    PlatformInfo,
    collect_platform_info,
    evaluate,
    parse_os_release,
    read_os_release,
)


class OsReleaseTests(unittest.TestCase):
    def test_parse_os_release_handles_quotes_and_comments(self) -> None:
        parsed = parse_os_release(
            '# comment\nID=ubuntu\nVERSION_ID="24.04"\nPRETTY_NAME="Ubuntu 24.04 LTS"\n'
        )
        self.assertEqual(parsed["ID"], "ubuntu")
        self.assertEqual(parsed["VERSION_ID"], "24.04")
        self.assertEqual(parsed["PRETTY_NAME"], "Ubuntu 24.04 LTS")

    def test_read_missing_os_release_is_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "does-not-exist"
            self.assertEqual(read_os_release(missing), {})

    def test_collect_accepts_injected_facts(self) -> None:
        info = collect_platform_info(
            {"ID": "kubuntu", "VERSION_ID": "24.04", "PRETTY_NAME": "Kubuntu 24.04 LTS"},
            {"XDG_CURRENT_DESKTOP": "KDE"},
        )
        self.assertEqual(info.distro_id, "kubuntu")
        self.assertEqual(info.distro_version, "24.04")
        self.assertEqual(info.desktop, "KDE")


class EvaluationTests(unittest.TestCase):
    def make_info(self, distro: str, version: str) -> PlatformInfo:
        return PlatformInfo(
            system="Linux",
            release="6.8.0",
            machine="x86_64",
            python="3.12.3",
            distro_id=distro,
            distro_name=f"{distro} {version}",
            distro_version=version,
            desktop="KDE",
        )

    def test_ubuntu_2404_family_is_supported(self) -> None:
        result = evaluate(self.make_info("ubuntu", "24.04"))
        self.assertTrue(result.supported_family)

    def test_kubuntu_2404_family_is_supported(self) -> None:
        result = evaluate(self.make_info("kubuntu", "24.04.4"))
        self.assertTrue(result.supported_family)

    def test_other_version_stays_open(self) -> None:
        result = evaluate(self.make_info("ubuntu", "26.04"))
        self.assertFalse(result.supported_family)
        self.assertEqual(result.status, "OPEN")

    def test_unknown_distribution_stays_open(self) -> None:
        result = evaluate(self.make_info("debian", "13"))
        self.assertFalse(result.supported_family)
        self.assertEqual(result.status, "OPEN")


if __name__ == "__main__":
    unittest.main()
