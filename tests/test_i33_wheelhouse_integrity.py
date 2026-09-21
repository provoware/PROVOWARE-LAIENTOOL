from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from scripts.build_portable_package import build_package
from scripts.verify_wheelhouse_integrity import verify_package_root
from scripts.wheelhouse_integrity import validate_wheel_names

GOOD_NAMES = (
    "PySide6-6.11.2-cp39-abi3-manylinux_2_34_x86_64.whl",
    "PySide6_Addons-6.11.2-cp39-abi3-manylinux_2_34_x86_64.whl",
    "PySide6_Essentials-6.11.2-cp39-abi3-manylinux_2_34_x86_64.whl",
    "shiboken6-6.11.2-cp39-abi3-manylinux_2_34_x86_64.whl",
)


class I33WheelhouseIntegrityTests(unittest.TestCase):
    def make_wheelhouse(self, root: Path, names=GOOD_NAMES) -> Path:
        wheelhouse = root / "wheelhouse"
        wheelhouse.mkdir()
        for index, name in enumerate(names):
            (wheelhouse / name).write_bytes(f"fake-wheel-{index}".encode())
        return wheelhouse

    def test_exact_expected_wheel_set_passes_policy(self) -> None:
        self.assertEqual(validate_wheel_names(GOOD_NAMES), ())

    def test_extra_wheel_is_rejected(self) -> None:
        failures = validate_wheel_names(GOOD_NAMES + (
            "evilpkg-1.0-cp39-abi3-manylinux_2_34_x86_64.whl",
        ))
        self.assertTrue(any("Unerwartete Wheels" in item for item in failures))

    def test_wrong_version_is_rejected(self) -> None:
        bad = list(GOOD_NAMES)
        bad[0] = "PySide6-6.11.1-cp39-abi3-manylinux_2_34_x86_64.whl"
        failures = validate_wheel_names(tuple(bad))
        self.assertTrue(any("Wheel-Version falsch" in item for item in failures))

    def test_wrong_platform_is_rejected(self) -> None:
        bad = list(GOOD_NAMES)
        bad[3] = "shiboken6-6.11.2-cp39-abi3-macosx_14_0_arm64.whl"
        failures = validate_wheel_names(tuple(bad))
        self.assertTrue(any("nicht Linux-x86_64" in item for item in failures))

    def test_builder_rejects_incomplete_wheelhouse(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wheelhouse = self.make_wheelhouse(root, GOOD_NAMES[:3])
            with self.assertRaises(ValueError):
                build_package(
                    output_dir=root / "dist",
                    wheelhouse=wheelhouse,
                    commit="d" * 40,
                )

    def test_manifest_detects_tampered_wheel_before_install(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wheelhouse = self.make_wheelhouse(root)
            archive, _, _ = build_package(
                output_dir=root / "dist",
                wheelhouse=wheelhouse,
                commit="e" * 40,
            )
            extract = root / "extract"
            with zipfile.ZipFile(archive) as handle:
                handle.extractall(extract)
            package = next(path for path in extract.iterdir() if path.is_dir())
            status, failures = verify_package_root(package)
            self.assertEqual(status, "PASS", failures)

            wheel = next((package / "wheelhouse").glob("PySide6-*.whl"))
            wheel.write_bytes(wheel.read_bytes() + b"tamper")
            status, failures = verify_package_root(package)
            self.assertEqual(status, "FAIL")
            self.assertTrue(any("SHA-256" in item or "Größe" in item for item in failures))

    def test_start_sh_verifies_before_no_index_install(self) -> None:
        text = (Path(__file__).resolve().parents[1] / "start.sh").read_text(encoding="utf-8")
        verify_pos = text.index("verify_wheelhouse_integrity.py")
        pip_pos = text.index("--no-index")
        self.assertLess(verify_pos, pip_pos)
        self.assertIn("Nichts installiert", text)


if __name__ == "__main__":
    unittest.main()
