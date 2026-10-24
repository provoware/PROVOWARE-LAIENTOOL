from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from provoware_laientool.preflight import PYTHON_MAX_EXCLUSIVE, PYTHON_MIN

ROOT = Path(__file__).resolve().parents[1]


class VenvBootstrapContractTests(unittest.TestCase):
    def test_gui_dependency_is_pinned(self) -> None:
        requirements = (ROOT / "requirements-gui.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(requirements, ["PySide6==6.11.2"])

    def test_start_script_is_fail_fast_and_venv_first(self) -> None:
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertIn("set -euo pipefail", text)
        self.assertIn('VENV_DIR="$ROOT_DIR/.venv"', text)
        self.assertIn('EXPECTED_PYSIDE6="6.11.2"', text)
        self.assertIn('python3', text)
        self.assertIn('-m venv', text)
        self.assertIn('requirements-gui.txt', text)
        self.assertIn('validate_venv', text)
        self.assertIn('validate_gui_runtime', text)


    def test_python_bounds_match_starter_and_portable_manifest(self) -> None:
        starter = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertIn(
            f"ok = {PYTHON_MIN} <= sys.version_info[:2] < {PYTHON_MAX_EXCLUSIVE}",
            starter,
        )
        package = (ROOT / "scripts" / "build_portable_package.py").read_text(
            encoding="utf-8"
        )
        lower = ".".join(map(str, PYTHON_MIN))
        upper = ".".join(map(str, PYTHON_MAX_EXCLUSIVE))
        self.assertIn(f'"python_supported": ">={lower},<{upper}"', package)

    def test_start_script_prefers_local_offline_wheelhouse(self) -> None:
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertIn('WHEELHOUSE="$ROOT_DIR/wheelhouse"', text)
        self.assertIn("--no-index", text)
        self.assertIn("--find-links", text)
        self.assertIn("Lokales Offline-Wheelhouse erkannt", text)

    def test_start_script_never_escalates_privileges(self) -> None:
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertNotIn("sudo ", text)
        self.assertNotIn("apt install", text)
        self.assertNotIn("chmod 777", text)

    def test_i17_uses_venv_python(self) -> None:
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertIn(
            'exec "$VENV_PYTHON" "$ROOT_DIR/scripts/i17_auto_evidence.py"',
            text,
        )

    def test_start_sh_remains_canonical_user_entrypoint(self) -> None:
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        for option in (
            "--gui",
            "--menu",
            "--preflight",
            "--json",
            "--i17",
            "--i17-auto",
            "--i17-offscreen",
            "--i31-evidence",
            "--i31-offscreen",
            "--i31-cli-evidence",
            "--diagnostics",
            "--diagnostics-json",
            "--second-device-evidence",
            "--second-device-evidence-json",
        ):
            self.assertIn(option, text)

    def test_i25_evidence_routes_through_start_sh(self) -> None:
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertIn(
            'exec "$VENV_PYTHON" "$ROOT_DIR/scripts/i25_auto_evidence.py"',
            text,
        )
        self.assertIn(
            'exec "$VENV_PYTHON" "$ROOT_DIR/scripts/i25_auto_evidence.py" --offscreen --auto-only',
            text,
        )

    def test_i31_evidence_routes_through_start_sh(self) -> None:
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertIn(
            'exec "$VENV_PYTHON" "$ROOT_DIR/scripts/i31_auto_evidence.py"',
            text,
        )
        self.assertIn(
            'exec "$VENV_PYTHON" "$ROOT_DIR/scripts/i31_auto_evidence.py" --offscreen --auto-only',
            text,
        )
        self.assertIn(
            'exec "$VENV_PYTHON" "$ROOT_DIR/scripts/i31_auto_evidence.py" --cli-demo',
            text,
        )

    def test_diagnostics_route_through_start_sh(self) -> None:
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertIn(
            'exec "$BASE_PYTHON" "$ROOT_DIR/scripts/diagnostic_snapshot.py"',
            text,
        )
        self.assertIn(
            'exec "$BASE_PYTHON" "$ROOT_DIR/scripts/diagnostic_snapshot.py" --json',
            text,
        )

    def test_second_device_evidence_routes_through_start_sh(self) -> None:
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertIn(
            'exec "$BASE_PYTHON" "$ROOT_DIR/scripts/second_device_evidence.py"',
            text,
        )
        self.assertIn(
            'exec "$BASE_PYTHON" "$ROOT_DIR/scripts/second_device_evidence.py" --json',
            text,
        )

    def test_check_mode_does_not_create_or_install(self) -> None:
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertIn('if [[ "$ACTION" == "--check" ]]', text)
        self.assertIn('Nichts verändert.', text)


    def test_core_only_modes_without_venv_and_gui_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(ROOT / "start.sh", root / "start.sh")
            (root / "scripts").mkdir()
            stub = (
                "import sys\n"
                "print('ENTRY:' + __file__.rsplit('/', 1)[-1] + '|' + '|'.join(sys.argv[1:]))\n"
            )
            (root / "start.py").write_text(stub, encoding="utf-8")
            for name in ("diagnostic_snapshot.py", "second_device_evidence.py"):
                (root / "scripts" / name).write_text(stub, encoding="utf-8")

            modes = (
                ("--preflight", "start.py", ""),
                ("--json", "start.py", "--json"),
                ("--diagnostics", "diagnostic_snapshot.py", ""),
                ("--diagnostics-json", "diagnostic_snapshot.py", "--json"),
                ("--second-device-evidence", "second_device_evidence.py", ""),
                ("--second-device-evidence-json", "second_device_evidence.py", "--json"),
            )
            for option, entry, argument in modes:
                with self.subTest(option=option):
                    result = subprocess.run(
                        ["bash", str(root / "start.sh"), option],
                        cwd=root, input="", capture_output=True,
                        text=True, check=False, timeout=10,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(
                        result.stdout.strip().splitlines()[-1],
                        f"ENTRY:{entry}|{argument}",
                    )
                    self.assertFalse((root / ".venv").exists())
                    self.assertFalse((root / ".venv.tmp").exists())

    def test_gui_mode_still_requires_gui_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(ROOT / "start.sh", root / "start.sh")
            result = subprocess.run(
                ["bash", str(root / "start.sh"), "--gui"],
                cwd=root, input="", capture_output=True,
                text=True, check=False, timeout=10,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requirements-gui.txt fehlt", result.stderr)
            self.assertFalse((root / ".venv").exists())

if __name__ == "__main__":
    unittest.main()
