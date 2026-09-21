#!/usr/bin/env python3
"""Validate a portable PROVOWARE ZIP without trusting archive paths."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

try:
    from .verify_wheelhouse_lock import verify_wheelhouse
except ImportError:
    from verify_wheelhouse_lock import verify_wheelhouse

REQUIRED = {
    "README.md",
    "PROVOWARE.desktop",
    "PACKAGE_MANIFEST.json",
    "requirements-gui.txt",
    "wheelhouse-lock-linux-x86_64.json",
    "start.py",
    "start.sh",
}
FORBIDDEN_PARTS = {".git", ".github", ".venv", "__pycache__", "tests", "dist", "build"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def member_relative(name: str) -> tuple[str, str]:
    normalized = name.replace("\\", "/")
    parts = [part for part in normalized.split("/") if part]
    if len(parts) < 2:
        raise ValueError(f"Archivpfad ohne Paketwurzel: {name}")
    if normalized.startswith("/") or any(part in {"..", "."} for part in parts):
        raise ValueError(f"Unsicherer Archivpfad: {name}")
    return parts[0], "/".join(parts[1:])


def restore_modes(root: Path, handle: zipfile.ZipFile) -> None:
    for info in handle.infolist():
        if info.is_dir():
            continue
        package_root, rel = member_relative(info.filename)
        mode = (info.external_attr >> 16) & 0o777
        if mode:
            os.chmod(root / package_root / rel, mode)


def validate_archive(archive: Path, *, require_wheelhouse: bool = False) -> dict[str, object]:
    failures: list[str] = []
    if not archive.is_file():
        return {"status": "FAIL", "failures": [f"Archiv fehlt: {archive}"]}

    with zipfile.ZipFile(archive) as handle:
        infos = handle.infolist()
        names = [info.filename for info in infos if not info.is_dir()]
        if len(names) != len(set(names)):
            failures.append("Archiv enthält doppelte Dateinamen.")

        roots: set[str] = set()
        relative_names: set[str] = set()
        for name in names:
            try:
                root, rel = member_relative(name)
            except ValueError as exc:
                failures.append(str(exc))
                continue
            roots.add(root)
            relative_names.add(rel)
            parts = set(Path(rel).parts)
            if parts & FORBIDDEN_PARTS:
                failures.append(f"Verbotener Paketinhalt: {rel}")

        if len(roots) != 1:
            failures.append(f"Erwartet genau eine Paketwurzel, gefunden: {sorted(roots)}")

        missing = sorted(REQUIRED - relative_names)
        if missing:
            failures.append(f"Pflichtdateien fehlen: {missing}")

        manifest_name = next(
            (name for name in names if name.endswith("/PACKAGE_MANIFEST.json")),
            None,
        )
        manifest: dict[str, object] = {}
        if manifest_name is None:
            failures.append("PACKAGE_MANIFEST.json fehlt.")
        else:
            try:
                manifest = json.loads(handle.read(manifest_name).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                failures.append(f"Manifest unlesbar: {exc}")

        if manifest:
            listed = manifest.get("files")
            if not isinstance(listed, list):
                failures.append("Manifest files ist keine Liste.")
            else:
                expected = relative_names - {"PACKAGE_MANIFEST.json"}
                manifest_paths = {
                    item.get("path")
                    for item in listed
                    if isinstance(item, dict) and isinstance(item.get("path"), str)
                }
                if expected != manifest_paths:
                    failures.append("Manifest-Dateiliste stimmt nicht exakt mit dem Archiv überein.")
                root = next(iter(roots), "")
                for item in listed:
                    if not isinstance(item, dict):
                        failures.append("Ungültiger Manifest-Dateieintrag.")
                        continue
                    rel = item.get("path")
                    if not isinstance(rel, str):
                        failures.append("Manifest-Dateipfad fehlt.")
                        continue
                    full_name = f"{root}/{rel}"
                    try:
                        data = handle.read(full_name)
                    except KeyError:
                        failures.append(f"Manifest referenziert fehlende Datei: {rel}")
                        continue
                    if item.get("size") != len(data):
                        failures.append(f"Größe stimmt nicht: {rel}")
                    if item.get("sha256") != sha256_bytes(data):
                        failures.append(f"SHA-256 stimmt nicht: {rel}")

            wheel_names = sorted(
                rel for rel in relative_names if rel.startswith("wheelhouse/") and rel.endswith(".whl")
            )
            if bool(manifest.get("offline_wheelhouse")) != bool(wheel_names):
                failures.append("Wheelhouse-Flag und Archivinhalt widersprechen sich.")
            if manifest.get("wheel_count") != len(wheel_names):
                failures.append("Wheel-Anzahl im Manifest stimmt nicht.")
            if require_wheelhouse and len(wheel_names) < 4:
                failures.append(
                    f"Offline-Paket benötigt vollständiges PySide6-Wheelhouse; gefunden: {len(wheel_names)} Wheels."
                )

        start_info = next((info for info in infos if info.filename.endswith("/start.sh")), None)
        desktop_info = next((info for info in infos if info.filename.endswith("/PROVOWARE.desktop")), None)
        for label, info in (("start.sh", start_info), ("PROVOWARE.desktop", desktop_info)):
            if info is None:
                continue
            mode = (info.external_attr >> 16) & 0o777
            if mode & 0o111 == 0:
                failures.append(f"{label} ist im ZIP nicht ausführbar markiert.")

        if desktop_info is not None:
            text = handle.read(desktop_info.filename).decode("utf-8", errors="replace")
            for marker in ("Type=Application", "%k", "./start.sh --gui", "Terminal=false"):
                if marker not in text:
                    failures.append(f"Desktop-Launcher-Vertrag fehlt: {marker}")

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "archive": str(archive),
        "archive_sha256": sha256_bytes(archive.read_bytes()),
    }


def runtime_check(archive: Path, *, require_wheelhouse: bool) -> dict[str, object]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="PROVOWARE Fremdpfad ä ") as temp:
        extract_root = Path(temp)
        with zipfile.ZipFile(archive) as handle:
            handle.extractall(extract_root)
            restore_modes(extract_root, handle)

        roots = [path for path in extract_root.iterdir() if path.is_dir()]
        if len(roots) != 1:
            return {"status": "FAIL", "failures": ["Extraktion hat keine eindeutige Paketwurzel."]}
        package = roots[0]

        preflight = subprocess.run(
            [sys.executable, "start.py", "--json"],
            cwd=package,
            text=True,
            capture_output=True,
            timeout=120,
            check=False,
        )
        if preflight.returncode not in {0, 3}:
            failures.append(
                f"Fremdpfad-Preflight Exit {preflight.returncode}: {preflight.stderr[-500:]}"
            )

        if require_wheelhouse:
            wheel_check = verify_wheelhouse(
                wheelhouse=package / "wheelhouse",
                lock_path=package / "wheelhouse-lock-linux-x86_64.json",
                requirements_path=package / "requirements-gui.txt",
            )
            if wheel_check["status"] != "PASS":
                failures.extend(
                    f"Extrahiertes Wheelhouse: {item}"
                    for item in wheel_check["failures"]
                )

            env = os.environ.copy()
            env.update(
                {
                    "PIP_NO_INDEX": "1",
                    "PIP_DISABLE_PIP_VERSION_CHECK": "1",
                    "PIP_INDEX_URL": "http://127.0.0.1:9/blocked",
                }
            )
            setup = subprocess.run(
                ["./start.sh", "--yes", "--setup"],
                cwd=package,
                env=env,
                text=True,
                capture_output=True,
                timeout=300,
                check=False,
            )
            if setup.returncode != 0:
                failures.append(
                    f"Offline-Setup Exit {setup.returncode}: {(setup.stdout + setup.stderr)[-1200:]}"
                )
            else:
                check = subprocess.run(
                    ["./start.sh", "--check"],
                    cwd=package,
                    env=env,
                    text=True,
                    capture_output=True,
                    timeout=120,
                    check=False,
                )
                if check.returncode != 0:
                    failures.append(
                        f"Offline-Check Exit {check.returncode}: {(check.stdout + check.stderr)[-1200:]}"
                    )

    return {"status": "PASS" if not failures else "FAIL", "failures": failures}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--require-wheelhouse", action="store_true")
    parser.add_argument("--runtime-check", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)

    structural = validate_archive(args.archive, require_wheelhouse=args.require_wheelhouse)
    runtime = {"status": "SKIPPED", "failures": []}
    if structural["status"] == "PASS" and args.runtime_check:
        runtime = runtime_check(args.archive, require_wheelhouse=args.require_wheelhouse)

    result = {
        "schema_version": "1",
        "structural": structural,
        "runtime": runtime,
        "status": "PASS"
        if structural["status"] == "PASS" and runtime["status"] in {"PASS", "SKIPPED"}
        else "FAIL",
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    print(rendered)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
