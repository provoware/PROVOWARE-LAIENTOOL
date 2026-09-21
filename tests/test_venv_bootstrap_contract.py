from __future__ import annotations

import unittest
from pathlib import Path

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
            "--diagnostics",
            "--diagnostics-json",
            "--second-device-evidence",
            "--second-device-evidence-json",
        ):
            self.assertIn(option, text)

    def test_diagnostics_route_through_start_sh(self) -> None:
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertIn(
            'exec "$VENV_PYTHON" "$ROOT_DIR/scripts/diagnostic_snapshot.py"',
            text,
        )
        self.assertIn(
            'exec "$VENV_PYTHON" "$ROOT_DIR/scripts/diagnostic_snapshot.py" --json',
            text,
        )

    def test_second_device_evidence_routes_through_start_sh(self) -> None:
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertIn(
            'exec "$VENV_PYTHON" "$ROOT_DIR/scripts/second_device_evidence.py"',
            text,
        )
        self.assertIn(
            'exec "$VENV_PYTHON" "$ROOT_DIR/scripts/second_device_evidence.py" --json',
            text,
        )

    def test_check_mode_does_not_create_or_install(self) -> None:
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertIn('if [[ "$ACTION" == "--check" ]]', text)
        self.assertIn('Nichts verändert.', text)


if __name__ == "__main__":
    unittest.main()
