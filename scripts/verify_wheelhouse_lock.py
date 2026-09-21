#!/usr/bin/env python3
"""Verify an offline wheelhouse against a committed exact-file lock."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_wheelhouse(
    *,
    wheelhouse: Path,
    lock_path: Path,
    requirements_path: Path | None = None,
) -> dict[str, object]:
    failures: list[str] = []

    if not lock_path.is_file():
        return {"status": "FAIL", "failures": [f"Wheelhouse-Lock fehlt: {lock_path}"]}
    if not wheelhouse.is_dir():
        return {"status": "FAIL", "failures": [f"Wheelhouse fehlt: {wheelhouse}"]}

    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "failures": [f"Wheelhouse-Lock unlesbar: {exc}"]}

    if lock.get("schema_version") != "1":
        failures.append("Unbekannte Wheelhouse-Lock-Schemaversion.")

    wheels = lock.get("wheels")
    if not isinstance(wheels, list) or not wheels:
        failures.append("Wheelhouse-Lock enthält keine Wheel-Liste.")
        wheels = []

    expected: dict[str, dict[str, object]] = {}
    for item in wheels:
        if not isinstance(item, dict):
            failures.append("Ungültiger Wheel-Lock-Eintrag.")
            continue
        filename = item.get("filename")
        sha256 = item.get("sha256")
        size = item.get("size")
        if not isinstance(filename, str) or Path(filename).name != filename:
            failures.append(f"Ungültiger Wheel-Dateiname im Lock: {filename!r}")
            continue
        if (
            not isinstance(sha256, str)
            or len(sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in sha256.lower())
        ):
            failures.append(f"Ungültiger SHA-256 im Lock: {filename}")
            continue
        if not isinstance(size, int) or size <= 0:
            failures.append(f"Ungültige Größe im Lock: {filename}")
            continue
        if filename in expected:
            failures.append(f"Doppelter Wheel-Lock-Eintrag: {filename}")
            continue
        expected[filename] = item

    actual_paths = sorted(wheelhouse.glob("*.whl"), key=lambda path: path.name)
    actual_names = {path.name for path in actual_paths}
    expected_names = set(expected)

    missing = sorted(expected_names - actual_names)
    extra = sorted(actual_names - expected_names)
    if missing:
        failures.append(f"Wheelhouse fehlen gesperrte Dateien: {missing}")
    if extra:
        failures.append(f"Wheelhouse enthält nicht gesperrte Dateien: {extra}")

    for path in actual_paths:
        item = expected.get(path.name)
        if item is None:
            continue
        if path.stat().st_size != item["size"]:
            failures.append(f"Wheel-Größe weicht vom Lock ab: {path.name}")
        digest = sha256_file(path)
        if digest != item["sha256"]:
            failures.append(f"Wheel-SHA-256 weicht vom Lock ab: {path.name}")

    if requirements_path is not None:
        if not requirements_path.is_file():
            failures.append(f"Requirements-Datei fehlt: {requirements_path}")
        else:
            requirements_digest = sha256_file(requirements_path)
            if requirements_digest != lock.get("requirements_sha256"):
                failures.append(
                    "requirements-gui.txt stimmt nicht mit dem Wheelhouse-Lock überein."
                )

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "platform_tag": lock.get("platform_tag"),
        "wheel_count": len(expected),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--requirements", type=Path)
    args = parser.parse_args(argv)

    result = verify_wheelhouse(
        wheelhouse=args.wheelhouse,
        lock_path=args.lock,
        requirements_path=args.requirements,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
