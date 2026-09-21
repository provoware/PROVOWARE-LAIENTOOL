"""Read-only runtime and platform preflight.

This module must not install packages, elevate privileges, access the network,
or mutate user files. It only inspects local runtime/platform facts.
"""

from __future__ import annotations

import json
import os
import platform
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class PlatformInfo:
    system: str
    release: str
    machine: str
    python: str
    distro_id: str
    distro_name: str
    distro_version: str
    desktop: str


@dataclass(frozen=True)
class PreflightResult:
    status: str
    supported_family: bool
    platform: PlatformInfo
    notes: tuple[str, ...]


def parse_os_release(text: str) -> dict[str, str]:
    """Parse /etc/os-release style content without shell execution."""
    result: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        result[key.strip()] = value
    return result


def read_os_release(path: Path = Path("/etc/os-release")) -> dict[str, str]:
    """Read distro metadata; failure is reported as an empty mapping."""
    try:
        return parse_os_release(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        return {}


def collect_platform_info(
    os_release: Mapping[str, str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> PlatformInfo:
    """Collect facts only; no writes, subprocesses, network, or elevation."""
    distro = dict(os_release) if os_release is not None else read_os_release()
    env = environ if environ is not None else os.environ
    desktop = env.get("XDG_CURRENT_DESKTOP") or env.get("DESKTOP_SESSION") or ""

    return PlatformInfo(
        system=platform.system(),
        release=platform.release(),
        machine=platform.machine(),
        python=platform.python_version(),
        distro_id=distro.get("ID", ""),
        distro_name=distro.get("PRETTY_NAME", distro.get("NAME", "")),
        distro_version=distro.get("VERSION_ID", ""),
        desktop=desktop,
    )


def evaluate(info: PlatformInfo) -> PreflightResult:
    """Evaluate the initial B01-A support family conservatively."""
    distro = info.distro_id.lower()
    version = info.distro_version
    supported_family = distro in {"ubuntu", "kubuntu"} and version.startswith("24.04")

    notes: list[str] = []
    if info.system != "Linux":
        notes.append("Dieses Projekt ist derzeit nur für Linux vorgesehen.")
    if distro not in {"ubuntu", "kubuntu"}:
        notes.append("Ubuntu/Kubuntu wurde nicht eindeutig erkannt.")
    if version and not version.startswith("24.04"):
        notes.append("Diese Betriebssystemversion ist noch nicht als B01-Baseline freigegeben.")
    if sys.version_info < (3, 10):
        notes.append("Python 3.10 oder neuer wird für die weitere Entwicklung vorausgesetzt.")

    if supported_family and sys.version_info >= (3, 10):
        status = "PASS"
        notes.append("Read-only Preflight erfolgreich; es wurden keine Änderungen vorgenommen.")
    else:
        status = "OPEN"
        notes.append("Preflight bleibt read-only; fehlende Voraussetzungen werden nicht automatisch installiert.")

    return PreflightResult(
        status=status,
        supported_family=supported_family,
        platform=info,
        notes=tuple(notes),
    )


def run_preflight() -> PreflightResult:
    return evaluate(collect_platform_info())


def format_text(result: PreflightResult) -> str:
    p = result.platform
    lines = [
        "PROVOWARE LAIENTOOL – Read-only Preflight",
        f"Status: {result.status}",
        f"System: {p.system} {p.release}",
        f"Distribution: {p.distro_name or 'unbekannt'}",
        f"Distribution-ID: {p.distro_id or 'unbekannt'}",
        f"Version: {p.distro_version or 'unbekannt'}",
        f"Desktop: {p.desktop or 'unbekannt'}",
        f"Architektur: {p.machine or 'unbekannt'}",
        f"Python: {p.python}",
        "Hinweise:",
    ]
    lines.extend(f"- {note}" for note in result.notes)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    result = run_preflight()
    if args == ["--json"]:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    elif args:
        print("Unbekannte Option. Erlaubt: --json", file=sys.stderr)
        return 2
    else:
        print(format_text(result))
    return 0 if result.status == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
