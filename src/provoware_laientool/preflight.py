"""Read-only runtime, platform and capability preflight.

No package installation, privilege elevation, network access or user-file
mutation is permitted here. The preflight only observes local facts and
selects the safest usable start profile from capabilities already present.
"""

from __future__ import annotations

import importlib.util
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
    session_type: str
    filesystem_encoding: str
    runtime_source: str


@dataclass(frozen=True)
class CapabilityInfo:
    linux: bool
    supported_distro_family: bool
    python_supported: bool
    graphical_session: bool
    pyside6_available: bool
    utf8_filesystem: bool
    home_available: bool
    downloads_available: bool
    project_readable: bool


@dataclass(frozen=True)
class StartPlan:
    profile: str
    gui_possible: bool
    portable_runtime_preferred: bool
    reason: str


@dataclass(frozen=True)
class PreflightResult:
    status: str
    platform: PlatformInfo
    capabilities: CapabilityInfo
    start_plan: StartPlan
    notes: tuple[str, ...]


def parse_os_release(text: str) -> dict[str, str]:
    """Parse /etc/os-release style content without shell execution."""
    result: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def read_os_release(path: Path = Path("/etc/os-release")) -> dict[str, str]:
    try:
        return parse_os_release(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        return {}


def runtime_source(prefix: str | None = None, base_prefix: str | None = None) -> str:
    """Classify the already-running local Python runtime."""
    if getattr(sys, "frozen", False):
        return "bundled"
    active_prefix = prefix if prefix is not None else sys.prefix
    system_prefix = base_prefix if base_prefix is not None else sys.base_prefix
    if active_prefix != system_prefix:
        return "venv"
    return "system"


def discover_downloads_dir(
    home: Path,
    config_text: str | None = None,
) -> Path:
    """Resolve XDG Downloads read-only, falling back to ~/Downloads."""
    text = config_text
    if text is None:
        try:
            text = (home / ".config" / "user-dirs.dirs").read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            text = ""

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("XDG_DOWNLOAD_DIR="):
            continue
        value = line.split("=", 1)[1].strip().strip('"').replace("$HOME", str(home))
        if value:
            return Path(value).expanduser()
    return home / "Downloads"


def collect_platform_info(
    os_release: Mapping[str, str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> PlatformInfo:
    distro = dict(os_release) if os_release is not None else read_os_release()
    env = environ if environ is not None else os.environ
    desktop = env.get("XDG_CURRENT_DESKTOP") or env.get("DESKTOP_SESSION") or ""
    session_type = env.get("XDG_SESSION_TYPE") or ""

    return PlatformInfo(
        system=platform.system(),
        release=platform.release(),
        machine=platform.machine(),
        python=platform.python_version(),
        distro_id=distro.get("ID", ""),
        distro_name=distro.get("PRETTY_NAME", distro.get("NAME", "")),
        distro_version=distro.get("VERSION_ID", ""),
        desktop=desktop,
        session_type=session_type,
        filesystem_encoding=sys.getfilesystemencoding(),
        runtime_source=runtime_source(),
    )


def collect_capabilities(
    info: PlatformInfo,
    *,
    home: Path | None = None,
    downloads: Path | None = None,
    project_root: Path | None = None,
    pyside6_available: bool | None = None,
) -> CapabilityInfo:
    distro = info.distro_id.lower()
    home_path = home if home is not None else Path.home()
    downloads_path = downloads if downloads is not None else discover_downloads_dir(home_path)
    root = project_root if project_root is not None else Path(__file__).resolve().parents[2]
    gui_session = bool(
        info.desktop
        or info.session_type in {"x11", "wayland"}
        or os.environ.get("DISPLAY")
        or os.environ.get("WAYLAND_DISPLAY")
    )
    has_pyside6 = (
        pyside6_available
        if pyside6_available is not None
        else importlib.util.find_spec("PySide6") is not None
    )

    return CapabilityInfo(
        linux=info.system == "Linux",
        supported_distro_family=distro in {"ubuntu", "kubuntu"}
        and info.distro_version.startswith("24.04"),
        python_supported=sys.version_info >= (3, 10),
        graphical_session=gui_session,
        pyside6_available=has_pyside6,
        utf8_filesystem=info.filesystem_encoding.lower().replace("-", "") == "utf8",
        home_available=home_path.is_dir() and os.access(home_path, os.R_OK),
        downloads_available=downloads_path.is_dir() and os.access(downloads_path, os.R_OK),
        project_readable=root.is_dir() and os.access(root, os.R_OK),
    )


def choose_start_plan(info: PlatformInfo, caps: CapabilityInfo) -> StartPlan:
    """Choose the best local profile; never acquire missing capabilities."""
    portable = info.runtime_source == "bundled"
    essential = (
        caps.linux
        and caps.supported_distro_family
        and caps.python_supported
        and caps.utf8_filesystem
        and caps.home_available
        and caps.project_readable
    )
    gui_possible = essential and caps.graphical_session and caps.pyside6_available

    if gui_possible:
        profile = "gui-ready"
        reason = "Alle lokal benötigten GUI-Fähigkeiten sind vorhanden."
    elif essential:
        profile = "preflight-cli"
        reason = (
            "Der sichere Kern ist nutzbar; GUI-Voraussetzungen fehlen oder sind noch nicht "
            "verfügbar. Es wird nichts nachinstalliert."
        )
    else:
        profile = "blocked-readonly"
        reason = (
            "Mindestens eine wesentliche lokale Voraussetzung ist nicht erfüllt. "
            "Der Start bleibt auf Diagnose/Anzeige beschränkt."
        )

    return StartPlan(
        profile=profile,
        gui_possible=gui_possible,
        portable_runtime_preferred=portable,
        reason=reason,
    )


def evaluate(info: PlatformInfo, caps: CapabilityInfo) -> PreflightResult:
    notes: list[str] = []
    if not caps.linux:
        notes.append("Dieses Projekt ist derzeit nur für Linux vorgesehen.")
    if not caps.supported_distro_family:
        notes.append("Ubuntu/Kubuntu 24.04 wurde nicht als freigegebene Baseline erkannt.")
    if not caps.python_supported:
        notes.append("Python 3.10 oder neuer wird vorausgesetzt.")
    if not caps.utf8_filesystem:
        notes.append("Das Dateisystem-Encoding ist nicht als UTF-8 erkannt.")
    if not caps.home_available:
        notes.append("Der persönliche Ordner ist nicht lesbar erreichbar.")
    if not caps.downloads_available:
        notes.append("Der Downloads-Ordner wurde nicht lesbar gefunden; Auswahl per Dialog bleibt später erforderlich.")
    if not caps.graphical_session:
        notes.append("Keine grafische Sitzung erkannt.")
    if not caps.pyside6_available:
        notes.append("PySide6 ist lokal nicht verfügbar; es erfolgt keine automatische Installation.")

    plan = choose_start_plan(info, caps)
    status = "PASS" if plan.profile in {"gui-ready", "preflight-cli"} else "OPEN"
    notes.append(plan.reason)

    return PreflightResult(
        status=status,
        platform=info,
        capabilities=caps,
        start_plan=plan,
        notes=tuple(notes),
    )


def run_preflight() -> PreflightResult:
    info = collect_platform_info()
    return evaluate(info, collect_capabilities(info))


def format_text(result: PreflightResult) -> str:
    p = result.platform
    c = result.capabilities
    lines = [
        "PROVOWARE LAIENTOOL – Read-only Preflight",
        f"Status: {result.status}",
        f"Startprofil: {result.start_plan.profile}",
        f"Runtime: {p.runtime_source}",
        f"System: {p.system} {p.release}",
        f"Distribution: {p.distro_name or 'unbekannt'}",
        f"Version: {p.distro_version or 'unbekannt'}",
        f"Desktop: {p.desktop or 'unbekannt'}",
        f"Sitzung: {p.session_type or 'unbekannt'}",
        f"Architektur: {p.machine or 'unbekannt'}",
        f"Python: {p.python}",
        "Fähigkeiten:",
        f"- Linux: {'ja' if c.linux else 'nein'}",
        f"- Zielsystem-Baseline: {'ja' if c.supported_distro_family else 'nein'}",
        f"- Python geeignet: {'ja' if c.python_supported else 'nein'}",
        f"- GUI-Sitzung: {'ja' if c.graphical_session else 'nein'}",
        f"- PySide6 lokal: {'ja' if c.pyside6_available else 'nein'}",
        f"- UTF-8-Dateisystem: {'ja' if c.utf8_filesystem else 'nein'}",
        f"- Home lesbar: {'ja' if c.home_available else 'nein'}",
        f"- Downloads lesbar: {'ja' if c.downloads_available else 'nein'}",
        f"- Projekt lesbar: {'ja' if c.project_readable else 'nein'}",
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
