"""I48: real starter subprocess tests for lossless invalid-.venv recovery."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReversibleVenvRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copyfile(ROOT / "start.sh", self.root / "start.sh")
        (self.root / "requirements-gui.txt").write_text("PySide6==6.11.2\n", encoding="utf-8")
        fake_bin = self.root / "fake-bin"
        fake_bin.mkdir()
        python3 = fake_bin / "python3"
        python3.write_text(
            "#!/usr/bin/env bash\n"
            "if [[ \"$1\" == -m && \"$2\" == venv ]]; then\n"
            "  mkdir -p -- \"$3/bin\"\n"
            "  cat > \"$3/bin/python\" <<'STUB'\n"
            "#!/usr/bin/env bash\n"
            "if [[ \"${FAKE_PYSIDE_FAIL:-0}\" == 1 ]]; then\n"
            "  if [[ \"$1\" == -m && \"$2\" == pip ]]; then exit 1; fi\n"
            "  code=\"$(cat)\"\n"
            "  if [[ \"$code\" == *importlib.metadata* ]]; then exit 0; fi\n"
            "fi\n"
            "echo 6.11.2\n"
            "STUB\n"
            "  chmod +x \"$3/bin/python\"\n"
            "  [[ \"${FAKE_VENV_FAIL:-0}\" == 1 ]] && exit 1\n"
            "  exit 0\n"
            "fi\n"
            "exec /usr/bin/python3 \"$@\"\n",
            encoding="utf-8",
        )
        python3.chmod(0o755)
        self.env = {
            **os.environ,
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "DISPLAY": "",
            "WAYLAND_DISPLAY": "",
        }

    def run_start(
        self, *args: str, answer: str = "", fail: bool = False,
        pyside_fail: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        env = {
            **self.env,
            "FAKE_VENV_FAIL": "1" if fail else "0",
            "FAKE_PYSIDE_FAIL": "1" if pyside_fail else "0",
        }
        return subprocess.run(
            ["bash", str(self.root / "start.sh"), *args],
            input=answer, text=True, capture_output=True, cwd=self.root,
            env=env, timeout=20, check=False,
        )

    def backups(self) -> list[Path]:
        return sorted(self.root.glob(".venv.backup.*"))

    def test_invalid_directory_is_preserved_and_not_nested(self) -> None:
        old = self.root / ".venv"
        old.mkdir()
        (old / "keep.txt").write_text("private", encoding="utf-8")
        result = self.run_start("--yes", "--setup")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((old / "bin/python").is_file())
        self.assertEqual(len(self.backups()), 1)
        self.assertEqual((self.backups()[0] / "original/keep.txt").read_text(), "private")
        self.assertFalse((old / "original").exists())

    def test_regular_file_is_preserved(self) -> None:
        (self.root / ".venv").write_text("do not erase", encoding="utf-8")
        result = self.run_start("--yes", "--setup")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.backups()[0] / "original").read_text(), "do not erase")

    def test_symlink_is_quarantined_without_touching_target(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "keep.txt").write_text("unchanged", encoding="utf-8")
        (self.root / ".venv").symlink_to(outside, target_is_directory=True)
        result = self.run_start("--yes", "--setup")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / ".venv").is_symlink())
        self.assertTrue((self.backups()[0] / "original").is_symlink())
        self.assertEqual((outside / "keep.txt").read_text(), "unchanged")

    def test_dangling_symlink_is_preserved(self) -> None:
        (self.root / ".venv").symlink_to("missing-target")
        result = self.run_start("--yes", "--setup")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(os.readlink(self.backups()[0] / "original"), "missing-target")

    def test_failed_build_restores_old_directory_and_preserves_partial(self) -> None:
        old = self.root / ".venv"
        old.mkdir()
        (old / "keep.txt").write_text("restore", encoding="utf-8")
        result = self.run_start("--yes", "--setup", fail=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((old / "keep.txt").read_text(), "restore")
        self.assertTrue((self.backups()[0] / "failed-setup/bin/python").exists())

    def test_failed_dependency_install_restores_previous_venv(self) -> None:
        old = self.root / ".venv"
        old.mkdir()
        (old / "keep.txt").write_text("keep", encoding="utf-8")
        result = self.run_start("--yes", "--setup", pyside_fail=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((old / "keep.txt").read_text(), "keep")
        self.assertTrue((self.backups()[0] / "failed-setup/bin/python").exists())

    def test_backup_paths_are_ignored_by_git(self) -> None:
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "--quiet",
             ".venv.backup.example/original/secret.txt"],
            cwd=ROOT, capture_output=True, text=True, timeout=10, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_declined_recovery_does_not_change_anything(self) -> None:
        (self.root / ".venv").write_text("unchanged", encoding="utf-8")
        result = self.run_start("--setup", answer="n\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.root / ".venv").read_text(), "unchanged")
        self.assertFalse(self.backups())

    def test_check_is_read_only_for_invalid_symlink(self) -> None:
        (self.root / ".venv").symlink_to("missing")
        result = self.run_start("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.root / ".venv").is_symlink())
        self.assertFalse(self.backups())

    def test_preexisting_legacy_temp_is_not_deleted(self) -> None:
        old = self.root / ".venv"
        old.mkdir()
        (self.root / ".venv.tmp").mkdir()
        (self.root / ".venv.tmp/keep.txt").write_text("legacy", encoding="utf-8")
        result = self.run_start("--yes", "--setup")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / ".venv.tmp/keep.txt").read_text(), "legacy")


if __name__ == "__main__":
    unittest.main()
