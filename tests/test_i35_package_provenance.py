from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.build_portable_package import build_package
from scripts.validate_portable_package import (
    checksum_failures,
    provenance_failures,
    validate_archive,
)


class I35PackageProvenanceTests(unittest.TestCase):
    def test_builder_rejects_non_commit_identifier(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                build_package(output_dir=Path(temp), commit="not-a-git-sha")

    def test_valid_archive_checksum_and_name_are_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive, checksum, _ = build_package(
                output_dir=Path(temp),
                commit="a" * 40,
            )
            result = validate_archive(archive, checksum=checksum)
            self.assertEqual(result["status"], "PASS", result["failures"])

    def test_renamed_archive_is_rejected_even_when_bytes_are_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive, _, _ = build_package(
                output_dir=root,
                commit="b" * 40,
            )
            renamed = root / "PROVOWARE-LAIENTOOL-renamed.zip"
            shutil.copyfile(archive, renamed)
            result = validate_archive(renamed)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(
                any("ZIP-Dateiname" in item for item in result["failures"])
            )

    def test_checksum_sidecar_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive, checksum, _ = build_package(
                output_dir=Path(temp),
                commit="c" * 40,
            )
            checksum.write_text("0" * 64 + f"  {archive.name}\n", encoding="utf-8")
            self.assertTrue(checksum_failures(archive, checksum))
            result = validate_archive(archive, checksum=checksum)
            self.assertEqual(result["status"], "FAIL")

    def test_manifest_commit_root_binding_rejects_mismatch(self) -> None:
        archive = Path("PROVOWARE-LAIENTOOL-" + "d" * 12 + "-linux-x86_64.zip")
        manifest = {
            "product": "PROVOWARE-LAIENTOOL",
            "commit": "e" * 40,
            "platform_tag": "linux-x86_64",
        }
        failures = provenance_failures(
            archive,
            {"PROVOWARE-LAIENTOOL-" + "d" * 12 + "-linux-x86_64"},
            manifest,
            require_wheelhouse=True,
        )
        self.assertTrue(any("Paketwurzel" in item for item in failures))
        self.assertTrue(any("ZIP-Dateiname" in item for item in failures))

    def test_offline_wheelhouse_platform_is_linux_x86_64_only(self) -> None:
        archive = Path("PROVOWARE-LAIENTOOL-" + "f" * 12 + "-linux-aarch64.zip")
        manifest = {
            "product": "PROVOWARE-LAIENTOOL",
            "commit": "f" * 40,
            "platform_tag": "linux-aarch64",
        }
        failures = provenance_failures(
            archive,
            {"PROVOWARE-LAIENTOOL-" + "f" * 12 + "-linux-aarch64"},
            manifest,
            require_wheelhouse=True,
        )
        self.assertTrue(any("linux-x86_64" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
