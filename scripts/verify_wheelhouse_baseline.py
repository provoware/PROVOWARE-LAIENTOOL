#!/usr/bin/env python3
"""Verify downloaded offline wheels against the committed I38 baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = ROOT / "wheelhouse-lock-linux-x86_64.json"
DEFAULT_REQUIREMENTS = ROOT / "requirements-gui.txt"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_baseline(
    *,
    wheelhouse: Path,
    baseline_path: Path = DEFAULT_BASELINE,
    requirements_path: Path = DEFAULT_REQUIREMENTS,
) -> tuple[str, tuple[str, ...]]:
    failures: list[str] = []

    if not baseline_path.is_file():
        return "FAIL", (f"Wheelhouse-Baseline fehlt: {baseline_path}",)
    if not wheelhouse.is_dir():
        return "FAIL", (f"Wheelhouse fehlt: {wheelhouse}",)
    if not requirements_path.is_file():
        return "FAIL", (f"Requirements-Datei fehlt: {requirements_path}",)

    try:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return "FAIL", (f"Wheelhouse-Baseline unlesbar: {exc}",)

    if baseline.get("schema_version") != "1":
        failures.append("Unbekannte Wheelhouse-Baseline-Schemaversion.")
    if baseline.get("platform_tag") != "linux-x86_64":
        failures.append("Wheelhouse-Baseline muss linux-x86_64 binden.")

    expected_req_hash = baseline.get("requirements_sha256")
    actual_req_hash = sha256_file(requirements_path)
    if expected_req_hash != actual_req_hash:
        failures.append("requirements-gui.txt weicht von der festgeschriebenen Baseline ab.")

    items = baseline.get("wheels")
    if not isinstance(items, list) or not items:
        failures.append("Wheelhouse-Baseline enthält keine Wheel-Liste.")
        items = []

    expected: dict[str, tuple[int, str]] = {}
    for item in items:
        if not isinstance(item, dict):
            failures.append("Ungültiger Wheel-Baseline-Eintrag.")
            continue
        filename = item.get("filename")
        size = item.get("size")
        digest = item.get("sha256")
        if not isinstance(filename, str) or Path(filename).name != filename:
            failures.append(f"Ungültiger Wheel-Dateiname in Baseline: {filename!r}")
            continue
        if not isinstance(size, int) or size <= 0:
            failures.append(f"Ungültige Wheel-Größe in Baseline: {filename}")
            continue
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(ch not in "0123456789abcdef" for ch in digest.lower())
        ):
            failures.append(f"Ungültiger Wheel-SHA-256 in Baseline: {filename}")
            continue
        if filename in expected:
            failures.append(f"Doppelter Wheel-Baseline-Eintrag: {filename}")
            continue
        expected[filename] = (size, digest.lower())

    actual = {
        path.name: path
        for path in wheelhouse.iterdir()
        if path.is_file() and path.suffix == ".whl"
    }
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        if missing:
            failures.append(f"Festgeschriebene Wheels fehlen: {missing}")
        if extra:
            failures.append(f"Nicht festgeschriebene Wheels vorhanden: {extra}")

    for filename, path in sorted(actual.items()):
        contract = expected.get(filename)
        if contract is None:
            continue
        expected_size, expected_digest = contract
        if path.stat().st_size != expected_size:
            failures.append(f"Wheel-Größe weicht von Baseline ab: {filename}")
        if sha256_file(path) != expected_digest:
            failures.append(f"Wheel-SHA-256 weicht von Baseline ab: {filename}")

    return ("PASS" if not failures else "FAIL", tuple(failures))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--requirements", type=Path, default=DEFAULT_REQUIREMENTS)
    args = parser.parse_args(argv)

    status, failures = verify_baseline(
        wheelhouse=args.wheelhouse,
        baseline_path=args.baseline,
        requirements_path=args.requirements,
    )
    print(
        json.dumps(
            {"status": status, "failures": failures},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
