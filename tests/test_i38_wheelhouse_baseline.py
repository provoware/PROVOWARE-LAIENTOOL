from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.verify_wheelhouse_baseline import verify_baseline


class I38WheelhouseBaselineTests(unittest.TestCase):
    def make_fixture(self, root: Path) -> tuple[Path, Path, Path]:
        requirements = root / "requirements-gui.txt"
        requirements.write_text("PySide6==6.11.2\n", encoding="utf-8")

        wheelhouse = root / "wheelhouse"
        wheelhouse.mkdir()
        wheel = wheelhouse / "pyside6-6.11.2-cp310-abi3-manylinux_2_34_x86_64.whl"
        wheel.write_bytes(b"known-wheel")

        baseline = root / "baseline.json"
        baseline.write_text(
            json.dumps(
                {
                    "schema_version": "1",
                    "platform_tag": "linux-x86_64",
                    "requirements_sha256": hashlib.sha256(requirements.read_bytes()).hexdigest(),
                    "wheels": [
                        {
                            "filename": wheel.name,
                            "size": wheel.stat().st_size,
                            "sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return wheelhouse, baseline, requirements

    def test_exact_precommitted_baseline_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            wheelhouse, baseline, requirements = self.make_fixture(Path(temp))
            status, failures = verify_baseline(
                wheelhouse=wheelhouse,
                baseline_path=baseline,
                requirements_path=requirements,
            )
            self.assertEqual(status, "PASS", failures)

    def test_changed_wheel_hash_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            wheelhouse, baseline, requirements = self.make_fixture(Path(temp))
            wheel = next(wheelhouse.glob("*.whl"))
            wheel.write_bytes(wheel.read_bytes() + b"tamper")
            status, failures = verify_baseline(
                wheelhouse=wheelhouse,
                baseline_path=baseline,
                requirements_path=requirements,
            )
            self.assertEqual(status, "FAIL")
            self.assertTrue(any("Größe" in item or "SHA-256" in item for item in failures))

    def test_extra_wheel_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            wheelhouse, baseline, requirements = self.make_fixture(Path(temp))
            (wheelhouse / "extra-1.0-py3-none-any.whl").write_bytes(b"extra")
            status, failures = verify_baseline(
                wheelhouse=wheelhouse,
                baseline_path=baseline,
                requirements_path=requirements,
            )
            self.assertEqual(status, "FAIL")
            self.assertTrue(any("Nicht festgeschriebene Wheels" in item for item in failures))

    def test_changed_requirements_hash_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            wheelhouse, baseline, requirements = self.make_fixture(Path(temp))
            requirements.write_text("PySide6==6.11.1\n", encoding="utf-8")
            status, failures = verify_baseline(
                wheelhouse=wheelhouse,
                baseline_path=baseline,
                requirements_path=requirements,
            )
            self.assertEqual(status, "FAIL")
            self.assertTrue(any("requirements-gui.txt" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
