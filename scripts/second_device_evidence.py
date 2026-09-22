#!/usr/bin/env python3
"""Read-only second-device evidence runner for B01 portability checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = ROOT / "start.py"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

PLATFORM_KEYS = {
    "system",
    "release",
    "machine",
    "python",
    "distro_id",
    "distro_name",
    "distro_version",
    "desktop",
    "session_type",
    "filesystem_encoding",
    "runtime_source",
}
CAPABILITY_KEYS = {
    "linux",
    "supported_distro_family",
    "python_supported",
    "graphical_session",
    "pyside6_available",
    "utf8_filesystem",
    "home_available",
    "downloads_available",
    "project_readable",
}
START_PLAN_KEYS = {
    "profile",
    "gui_possible",
    "portable_runtime_preferred",
    "reason",
}


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_manifest_commit(root: Path) -> str | None:
    manifest_path = root / "PACKAGE_MANIFEST.json"
    if not manifest_path.is_file():
        return None
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"PACKAGE_MANIFEST.json ist nicht lesbar: {exc}") from exc
    commit = payload.get("commit") if isinstance(payload, dict) else None
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        raise ValueError("PACKAGE_MANIFEST.json enthält keinen gültigen 40-stelligen Commit.")
    return commit


def git_commit(root: Path) -> str | None:
    if not (root / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    commit = result.stdout.strip().lower()
    if result.returncode == 0 and COMMIT_RE.fullmatch(commit):
        return commit
    return None


def source_identity(root: Path = ROOT, start: Path = START) -> dict[str, object]:
    fingerprint = sha256(start)
    try:
        manifest_commit = package_manifest_commit(root)
    except ValueError as exc:
        return {
            "valid": False,
            "kind": "invalid-package-manifest",
            "commit": None,
            "fingerprint_sha256": fingerprint,
            "error": str(exc),
        }
    if manifest_commit is not None:
        return {
            "valid": True,
            "kind": "package-manifest-commit",
            "commit": manifest_commit,
            "fingerprint_sha256": fingerprint,
            "error": None,
        }
    repository_commit = git_commit(root)
    if repository_commit is not None:
        return {
            "valid": True,
            "kind": "git-commit",
            "commit": repository_commit,
            "fingerprint_sha256": fingerprint,
            "error": None,
        }
    return {
        "valid": True,
        "kind": "start.py-sha256",
        "commit": None,
        "fingerprint_sha256": fingerprint,
        "error": None,
    }


def select_keys(value: object, allowed: set[str]) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    return {key: value[key] for key in allowed if key in value}


def redact_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        return {}
    result: dict[str, object] = {}
    if "status" in payload:
        result["status"] = payload["status"]
    result["platform"] = select_keys(payload.get("platform"), PLATFORM_KEYS)
    result["capabilities"] = select_keys(payload.get("capabilities"), CAPABILITY_KEYS)
    result["start_plan"] = select_keys(payload.get("start_plan"), START_PLAN_KEYS)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Erzeugt einen read-only B01-Zweitgeräte-Prüfbericht."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Bericht als JSON ausgeben.",
    )
    args = parser.parse_args()

    text_run = run_command([sys.executable, str(START)])
    json_run = run_command([sys.executable, str(START), "--json"])
    identity = source_identity()

    parsed: object | None = None
    parse_error: str | None = None
    if json_run.stdout.strip():
        try:
            parsed = redact_payload(json.loads(json_run.stdout))
        except json.JSONDecodeError as exc:
            parse_error = f"JSON-Ausgabe konnte nicht gelesen werden: {exc}"

    report = {
        "evidence": "B01-second-device-preflight",
        "repository_start_sha256": identity["fingerprint_sha256"],
        "source_identity": identity,
        "host": {
            "system": platform.system(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "text_exit_code": text_run.returncode,
        "json_exit_code": json_run.returncode,
        "preflight": parsed,
        "parse_error": parse_error,
        "result": (
            "PASS"
            if text_run.returncode in {0, 3}
            and json_run.returncode in {0, 3}
            and parsed is not None
            and identity["valid"] is True
            else "FAIL"
        ),
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("PROVOWARE – Zweitgeräte-Portabilitätsprüfung")
        print("------------------------------------------")
        print(f"Ergebnis: {report['result']}")
        print(f"Text-Preflight Exit-Code: {text_run.returncode}")
        print(f"JSON-Preflight Exit-Code: {json_run.returncode}")
        print(f"Python: {report['host']['python']}")
        print(f"Architektur: {report['host']['machine']}")
        print(f"Herkunft: {identity['kind']}")
        if identity["commit"]:
            print(f"Commit: {identity['commit']}")
        print(f"Start-Fingerprint SHA-256: {identity['fingerprint_sha256']}")
        if identity["error"]:
            print(f"Herkunftsfehler: {identity['error']}")
        if parsed is not None:
            print("Preflight-Daten: sicher redigiert verfügbar")
        if parse_error:
            print(f"Fehler: {parse_error}")
        print()
        print("Nächster Schritt:")
        print("Diesen Bericht vollständig kopieren und als Zweitgeräte-Evidence übernehmen.")

    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
