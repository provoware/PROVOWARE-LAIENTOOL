from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.verify_wheelhouse_lock import verify_wheelhouse

ROOT = Path(__file__).resolve().parents[1]


class I33WheelhouseLockTests(unittest.TestCase):
    def make_fixture(self, root: Path) -> tuple[Path, Path, Path]:
        wheelhouse = root / "wheelhouse"
        wheelhouse.mkdir()
        wheel = wheelhouse / "demo-1.0-py3-none-any.whl"
        wheel.write_bytes(b"known-wheel")
        requirements = root / "requirements.txt"
        requirements.write_text("demo==1.0\n", encoding="utf-8")
        lock = root / "lock.json"
        lock.write_text(
            json.dumps(
                {
                    "schema_version": "1",
                    "platform_tag": "test",
                    "requirements_sha256": hashlib.sha256(
                        requirements.read_bytes()
                    ).hexdigest(),
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
        return wheelhouse, requirements, lock

    def test_exact_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            wheelhouse, requirements, lock = self.make_fixture(Path(temp))
            result = verify_wheelhouse(
                wheelhouse=wheelhouse,
                lock_path=lock,
                requirements_path=requirements,
            )
            self.assertEqual(result["status"], "PASS", result["failures"])

    def test_tampered_wheel_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            wheelhouse, requirements, lock = self.make_fixture(Path(temp))
            next(wheelhouse.glob("*.whl")).write_bytes(b"tampered")
            result = verify_wheelhouse(
                wheelhouse=wheelhouse,
                lock_path=lock,
                requirements_path=requirements,
            )
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("SHA-256" in item or "Größe" in item for item in result["failures"]))

    def test_extra_wheel_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            wheelhouse, requirements, lock = self.make_fixture(Path(temp))
            (wheelhouse / "extra-1.0.whl").write_bytes(b"extra")
            result = verify_wheelhouse(
                wheelhouse=wheelhouse,
                lock_path=lock,
                requirements_path=requirements,
            )
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("nicht gesperrte" in item for item in result["failures"]))

    def test_missing_wheel_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            wheelhouse, requirements, lock = self.make_fixture(Path(temp))
            next(wheelhouse.glob("*.whl")).unlink()
            result = verify_wheelhouse(
                wheelhouse=wheelhouse,
                lock_path=lock,
                requirements_path=requirements,
            )
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("fehlen gesperrte" in item for item in result["failures"]))

    def test_requirements_drift_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            wheelhouse, requirements, lock = self.make_fixture(Path(temp))
            requirements.write_text("demo==2.0\n", encoding="utf-8")
            result = verify_wheelhouse(
                wheelhouse=wheelhouse,
                lock_path=lock,
                requirements_path=requirements,
            )
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("requirements-gui" in item for item in result["failures"]))

    def test_committed_linux_lock_matches_pinned_requirement_contract(self) -> None:
        lock_path = ROOT / "wheelhouse-lock-linux-x86_64.json"
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], "1")
        self.assertEqual(data["platform_tag"], "linux-x86_64")
        self.assertEqual(len(data["wheels"]), 4)
        self.assertEqual(
            data["requirements_sha256"],
            hashlib.sha256((ROOT / "requirements-gui.txt").read_bytes()).hexdigest(),
        )
        names = {item["filename"] for item in data["wheels"]}
        self.assertEqual(
            names,
            {
                "pyside6-6.11.2-cp310-abi3-manylinux_2_34_x86_64.whl",
                "pyside6_addons-6.11.2-cp310-abi3-manylinux_2_34_x86_64.whl",
                "pyside6_essentials-6.11.2-cp310-abi3-manylinux_2_34_x86_64.whl",
                "shiboken6-6.11.2-cp310-abi3-manylinux_2_34_x86_64.whl",
            },
        )


if __name__ == "__main__":
    unittest.main()
