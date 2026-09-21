#!/usr/bin/env python3
"""Build a deterministic portable PROVOWARE ZIP.

The archive contains only tracked runtime/documentation files plus an optional
local wheelhouse. It never modifies source files and never invokes package
installation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import zipfile

try:
    from .wheelhouse_integrity import validate_wheelhouse_dir
except ImportError:
    from wheelhouse_integrity import validate_wheelhouse_dir

ROOT = Path(__file__).resolve().parents[1]
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
RUNTIME_TOP_LEVEL = {
    "README.md",
    "PROVOWARE.desktop",
    "requirements-gui.txt",
    "start.py",
    "start.sh",
}
RUNTIME_PREFIXES = ("src/", "scripts/", "docs/")
EXCLUDED_PREFIXES = (
    ".github/",
    "tests/",
    "docs/evidence/",
    "build/",
    "dist/",
    ".venv/",
)
EXCLUDED_NAMES = {
    ".gitignore",
    "AGENTS.md",
    "PROVOWARE_TODO_INPUT_POOL0.md",
    "todo.txt",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def current_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def tracked_runtime_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    files: list[Path] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8")
        if rel in EXCLUDED_NAMES:
            continue
        if any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            continue
        if rel in RUNTIME_TOP_LEVEL or rel.startswith(RUNTIME_PREFIXES):
            path = ROOT / rel
            if path.is_file():
                files.append(path)
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def platform_tag() -> str:
    system = platform.system().lower() or "unknown"
    machine = (platform.machine() or "unknown").lower().replace(" ", "_")
    return f"{system}-{machine}"


def archive_mode(relative: str) -> int:
    if relative in {"start.sh", "PROVOWARE.desktop"}:
        return 0o755
    if relative.startswith("scripts/") and relative.endswith(".py"):
        return 0o755
    return 0o644


def zip_info(name: str, mode: int) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (mode & 0xFFFF) << 16
    return info


def build_package(
    *,
    output_dir: Path,
    wheelhouse: Path | None = None,
    commit: str | None = None,
) -> tuple[Path, Path, dict[str, object]]:
    commit = (commit or current_commit()).lower()
    if not COMMIT_RE.fullmatch(commit):
        raise ValueError("Paket-Commit muss exakt ein 40-stelliger Git-SHA-1 in Hex sein.")
    tag = platform_tag()
    package_root = f"PROVOWARE-LAIENTOOL-{commit[:12]}-{tag}"
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"{package_root}.zip"
    checksum = archive.with_suffix(".zip.sha256")

    entries: list[tuple[str, bytes, int]] = []
    manifest_files: list[dict[str, object]] = []

    for path in tracked_runtime_files():
        rel = path.relative_to(ROOT).as_posix()
        data = path.read_bytes()
        entries.append((rel, data, archive_mode(rel)))

    wheel_files: list[Path] = []
    if wheelhouse is not None:
        if not wheelhouse.is_dir():
            raise ValueError(f"Wheelhouse fehlt: {wheelhouse}")
        wheel_files, wheel_failures = validate_wheelhouse_dir(wheelhouse)
        if wheel_failures:
            raise ValueError("Ungültiges Wheelhouse: " + " | ".join(wheel_failures))
        wheel_files = list(wheel_files)
        for path in wheel_files:
            rel = f"wheelhouse/{path.name}"
            entries.append((rel, path.read_bytes(), 0o644))

    for rel, data, mode in sorted(entries, key=lambda item: item[0]):
        manifest_files.append(
            {
                "path": rel,
                "size": len(data),
                "sha256": sha256_bytes(data),
                "mode": oct(mode),
            }
        )

    requirements_data = (ROOT / "requirements-gui.txt").read_bytes()
    manifest: dict[str, object] = {
        "schema_version": "1",
        "product": "PROVOWARE-LAIENTOOL",
        "commit": commit,
        "platform_tag": tag,
        "python_supported": ">=3.10,<3.15",
        "requirements_sha256": sha256_bytes(requirements_data),
        "offline_wheelhouse": bool(wheel_files),
        "wheel_count": len(wheel_files),
        "files": manifest_files,
    }
    manifest_data = (
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

    with zipfile.ZipFile(
        archive,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as handle:
        for rel, data, mode in sorted(entries, key=lambda item: item[0]):
            handle.writestr(zip_info(f"{package_root}/{rel}", mode), data)
        handle.writestr(
            zip_info(f"{package_root}/PACKAGE_MANIFEST.json", 0o644),
            manifest_data,
        )

    archive_hash = sha256_bytes(archive.read_bytes())
    checksum.write_text(f"{archive_hash}  {archive.name}\n", encoding="utf-8")
    return archive, checksum, manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--wheelhouse", type=Path)
    args = parser.parse_args(argv)

    archive, checksum, manifest = build_package(
        output_dir=args.output_dir,
        wheelhouse=args.wheelhouse,
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "archive": str(archive),
                "checksum": str(checksum),
                "commit": manifest["commit"],
                "platform_tag": manifest["platform_tag"],
                "offline_wheelhouse": manifest["offline_wheelhouse"],
                "wheel_count": manifest["wheel_count"],
                "archive_size_bytes": archive.stat().st_size,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
