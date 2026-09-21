#!/usr/bin/env python3
"""Verify local wheelhouse consistency before any offline pip installation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .wheelhouse_integrity import EXPECTED_VERSION, validate_wheelhouse_dir
except ImportError:
    from wheelhouse_integrity import EXPECTED_VERSION, validate_wheelhouse_dir


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_package_root(root: Path) -> tuple[str, tuple[str, ...]]:
    root = root.resolve()
    failures: list[str] = []
    wheelhouse = root / "wheelhouse"
    wheels, policy_failures = validate_wheelhouse_dir(wheelhouse)
    failures.extend(policy_failures)

    requirements = root / "requirements-gui.txt"
    if not requirements.is_file():
        failures.append("requirements-gui.txt fehlt.")
    else:
        lines = [
            line.strip()
            for line in requirements.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        if lines != [f"PySide6=={EXPECTED_VERSION}"]:
            failures.append(
                f"requirements-gui.txt muss exakt PySide6=={EXPECTED_VERSION} enthalten."
            )

    manifest_path = root / "PACKAGE_MANIFEST.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            failures.append(f"PACKAGE_MANIFEST.json unlesbar: {exc}")
            manifest = {}

        if manifest:
            if not manifest.get("offline_wheelhouse"):
                failures.append("Manifest markiert das Wheelhouse nicht als offline_wheelhouse.")
            if manifest.get("wheel_count") != len(wheels):
                failures.append("Wheel-Anzahl im Manifest stimmt nicht mit wheelhouse/ überein.")

            if requirements.is_file():
                expected_req_hash = manifest.get("requirements_sha256")
                actual_req_hash = sha256_file(requirements)
                if expected_req_hash != actual_req_hash:
                    failures.append("requirements-gui.txt stimmt nicht mit dem Manifest-Hash überein.")

            listed = manifest.get("files")
            manifest_files = {
                item.get("path"): item
                for item in listed
                if isinstance(item, dict) and isinstance(item.get("path"), str)
            } if isinstance(listed, list) else {}

            expected_paths = {f"wheelhouse/{wheel.name}" for wheel in wheels}
            listed_wheels = {
                path for path in manifest_files if isinstance(path, str) and path.startswith("wheelhouse/")
            }
            if expected_paths != listed_wheels:
                failures.append("Manifest-Wheeldateiliste stimmt nicht exakt mit wheelhouse/ überein.")

            for wheel in wheels:
                rel = f"wheelhouse/{wheel.name}"
                entry = manifest_files.get(rel)
                if not isinstance(entry, dict):
                    failures.append(f"Wheel fehlt im Manifest: {wheel.name}")
                    continue
                if entry.get("size") != wheel.stat().st_size:
                    failures.append(f"Wheel-Größe weicht vom Manifest ab: {wheel.name}")
                if entry.get("sha256") != sha256_file(wheel):
                    failures.append(f"Wheel-SHA-256 weicht vom Manifest ab: {wheel.name}")

    return ("PASS" if not failures else "FAIL", tuple(failures))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_root", type=Path)
    args = parser.parse_args(argv)
    status, failures = verify_package_root(args.package_root)
    print(json.dumps({"status": status, "failures": failures}, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
