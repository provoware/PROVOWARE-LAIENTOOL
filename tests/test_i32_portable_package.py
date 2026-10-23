from __future__ import annotations

import hashlib
import re
from fnmatch import fnmatchcase
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.build_portable_package import (
    RUNTIME_PREFIXES,
    RUNTIME_TOP_LEVEL,
    build_package,
    tracked_runtime_files,
)
from scripts.validate_portable_package import validate_archive

ROOT = Path(__file__).resolve().parents[1]


class I32PortablePackageTests(unittest.TestCase):
    def test_desktop_launcher_delegates_to_canonical_start_sh(self) -> None:
        text = (ROOT / "PROVOWARE.desktop").read_text(encoding="utf-8")
        self.assertIn("%k", text)
        self.assertIn("./start.sh --gui", text)
        self.assertIn("Terminal=false", text)
        self.assertNotIn("sudo", text)

    def test_start_sh_prefers_local_wheelhouse_without_index(self) -> None:
        text = (ROOT / "start.sh").read_text(encoding="utf-8")
        self.assertIn('WHEELHOUSE="$ROOT_DIR/wheelhouse"', text)
        self.assertIn("--no-index", text)
        self.assertIn("--find-links", text)
        self.assertIn("Lokales Offline-Wheelhouse", text)

    def test_source_package_is_deterministic_and_structurally_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first_dir = Path(temp) / "a"
            second_dir = Path(temp) / "b"
            first, _, first_manifest = build_package(output_dir=first_dir, commit="a" * 40)
            second, _, second_manifest = build_package(output_dir=second_dir, commit="a" * 40)
            self.assertEqual(hashlib.sha256(first.read_bytes()).hexdigest(), hashlib.sha256(second.read_bytes()).hexdigest())
            self.assertEqual(first_manifest, second_manifest)
            result = validate_archive(first)
            self.assertEqual(result["status"], "PASS", result["failures"])

    def test_package_excludes_development_and_local_runtime_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive, _, _ = build_package(output_dir=Path(temp), commit="b" * 40)
            with zipfile.ZipFile(archive) as handle:
                relative = ["/".join(name.split("/")[1:]) for name in handle.namelist()]
            self.assertFalse(any(name.startswith("tests/") for name in relative))
            self.assertFalse(any(name.startswith(".github/") for name in relative))
            self.assertFalse(any(name.startswith("docs/evidence/") for name in relative))
            self.assertFalse(any("/__pycache__/" in f"/{name}/" for name in relative))
            self.assertNotIn("AGENTS.md", relative)
            self.assertNotIn("todo.txt", relative)

    def test_manifest_hashes_runtime_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive, _, manifest = build_package(output_dir=Path(temp), commit="c" * 40)
            listed = {item["path"]: item for item in manifest["files"]}
            start = (ROOT / "start.sh").read_bytes()
            self.assertEqual(listed["start.sh"]["sha256"], hashlib.sha256(start).hexdigest())
            self.assertFalse(manifest["offline_wheelhouse"])
            self.assertEqual(manifest["wheel_count"], 0)


class PortableWorkflowTriggerTests(unittest.TestCase):
    """Protect the package CI against future source-file trigger gaps."""

    @staticmethod
    def event_paths(event: str) -> tuple[str, ...]:
        workflow = (ROOT / ".github/workflows/portable-package.yml").read_text(
            encoding="utf-8"
        )
        section = re.search(
            rf"(?ms)^  {re.escape(event)}:\n(.*?)(?=^  (?:pull_request|push):|^[a-z][a-z_-]*:|\Z)",
            workflow,
        )
        if section is None:
            raise AssertionError(f"Workflow-Ereignis fehlt: {event}")
        block = re.search(
            r'(?m)^    paths:\n((?:      - "[^"]+"\n)+)',
            section.group(1),
        )
        if block is None:
            raise AssertionError(f"Pfadfilter fehlt: {event}")
        return tuple(re.findall(r'^      - "([^"]+)"$', block.group(1), re.M))

    def test_pull_request_and_main_use_same_unique_paths(self) -> None:
        pull_paths = self.event_paths("pull_request")
        push_paths = self.event_paths("push")
        self.assertEqual(pull_paths, push_paths)
        self.assertEqual(len(pull_paths), len(set(pull_paths)))

    def test_all_packaged_runtime_sources_trigger_package_ci(self) -> None:
        paths = self.event_paths("pull_request")
        for path in sorted(RUNTIME_TOP_LEVEL):
            self.assertIn(path, paths)
        for prefix in RUNTIME_PREFIXES:
            self.assertIn(f"{prefix}**", paths)

        for source in tracked_runtime_files():
            relative = source.relative_to(ROOT).as_posix()
            with self.subTest(source=relative):
                self.assertTrue(
                    any(fnmatchcase(relative, pattern) for pattern in paths),
                    f"Paketdatei löst kein Paket-Gate aus: {relative}",
                )

    def test_new_runtime_files_and_package_contracts_are_covered(self) -> None:
        paths = self.event_paths("pull_request")
        for relative in (
            "src/provoware_laientool/new_module.py",
            "scripts/new_runtime_helper.py",
            "docs/new_user_guide.md",
            "README.md",
            "wheelhouse-lock-linux-x86_64.json",
            "tests/test_i32_portable_package.py",
            "tests/test_i33_wheelhouse_integrity.py",
            "tests/test_i35_package_provenance.py",
            "tests/test_i38_wheelhouse_baseline.py",
            ".github/workflows/portable-package.yml",
        ):
            with self.subTest(relative=relative):
                self.assertTrue(
                    any(fnmatchcase(relative, pattern) for pattern in paths),
                    f"Änderung löst kein Paket-Gate aus: {relative}",
                )


if __name__ == "__main__":
    unittest.main()
