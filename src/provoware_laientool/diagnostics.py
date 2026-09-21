"""Read-only, redacted diagnostic report model for I20 observability."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .preflight import PreflightResult, run_preflight
from .recovery_contract import JournalSnapshot, crash_guidance

STATUS_FACT = "FACT"
STATUS_WARNING = "WARNING"
STATUS_OPEN = "OPEN"
VALID_ENTRY_STATUSES = {STATUS_FACT, STATUS_WARNING, STATUS_OPEN}

_HOME_PATTERN = re.compile(r"(?<![A-Za-z0-9_])/home/[^/\s]+")
_EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_GITHUB_TOKEN_PATTERN = re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")
_OPENAI_TOKEN_PATTERN = re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")
_BEARER_PATTERN = re.compile(r"(?i)(\bBearer\s+)[A-Za-z0-9._~+/=-]{12,}")


@dataclass(frozen=True, slots=True)
class DiagnosticEntry:
    category: str
    key: str
    value: str
    status: str = STATUS_FACT


@dataclass(frozen=True, slots=True)
class DiagnosticReport:
    schema_version: str
    collection_status: str
    health_status: str
    entries: tuple[DiagnosticEntry, ...]
    warnings: tuple[str, ...]
    redaction_applied: bool
    write_paths_enabled: bool = False


def redact_text(value: str, *, home: Path | None = None) -> str:
    """Redact common path/identity/token material without writing anything."""
    text = value
    if home is not None:
        home_text = str(home)
        if home_text:
            text = text.replace(home_text, "$HOME")
    text = _HOME_PATTERN.sub("$HOME", text)
    text = _EMAIL_PATTERN.sub("<EMAIL>", text)
    text = _GITHUB_TOKEN_PATTERN.sub("<TOKEN>", text)
    text = _OPENAI_TOKEN_PATTERN.sub("<TOKEN>", text)
    text = _BEARER_PATTERN.sub(r"\1<TOKEN>", text)
    return text


def _bool(value: bool) -> str:
    return "ja" if value else "nein"


def _preflight_entries(result: PreflightResult) -> tuple[DiagnosticEntry, ...]:
    p = result.platform
    c = result.capabilities
    facts = (
        ("system", p.system),
        ("release", p.release),
        ("machine", p.machine),
        ("python", p.python),
        ("distro_id", p.distro_id),
        ("distro_name", p.distro_name),
        ("distro_version", p.distro_version),
        ("desktop", p.desktop),
        ("session_type", p.session_type),
        ("filesystem_encoding", p.filesystem_encoding),
        ("runtime_source", p.runtime_source),
    )
    caps = (
        ("linux", c.linux),
        ("supported_distro_family", c.supported_distro_family),
        ("python_supported", c.python_supported),
        ("graphical_session", c.graphical_session),
        ("pyside6_available", c.pyside6_available),
        ("utf8_filesystem", c.utf8_filesystem),
        ("home_available", c.home_available),
        ("downloads_available", c.downloads_available),
        ("project_readable", c.project_readable),
    )
    entries = [
        DiagnosticEntry("platform", key, redact_text(value))
        for key, value in facts
    ]
    entries.extend(
        DiagnosticEntry("capability", key, _bool(value))
        for key, value in caps
    )
    entries.append(
        DiagnosticEntry("start", "profile", result.start_plan.profile)
    )
    return tuple(entries)


def _recovery_entries(snapshot: JournalSnapshot | None) -> tuple[DiagnosticEntry, ...]:
    if snapshot is None:
        return (
            DiagnosticEntry(
                "recovery",
                "snapshot",
                "kein Recovery-Snapshot übergeben",
                STATUS_OPEN,
            ),
        )

    guidance = crash_guidance(snapshot.state)
    entries = [
        DiagnosticEntry("recovery", "state", snapshot.state),
        DiagnosticEntry("recovery", "attempt", str(snapshot.attempt)),
        DiagnosticEntry("recovery", "effect_known", _bool(guidance.effect_known)),
        DiagnosticEntry(
            "recovery",
            "automatic_retry",
            _bool(guidance.may_retry_automatically),
        ),
        DiagnosticEntry(
            "recovery",
            "guidance",
            redact_text(guidance.action),
            STATUS_WARNING if not guidance.effect_known else STATUS_FACT,
        ),
    ]
    if snapshot.last_error:
        entries.append(
            DiagnosticEntry(
                "recovery",
                "last_error",
                redact_text(snapshot.last_error),
                STATUS_WARNING,
            )
        )
    return tuple(entries)


def build_diagnostic_report(
    *,
    preflight: PreflightResult | None = None,
    recovery: JournalSnapshot | None = None,
    extra_messages: tuple[str, ...] = (),
    home: Path | None = None,
) -> DiagnosticReport:
    """Build a deterministic in-memory report; no export or persistence."""
    result = preflight if preflight is not None else run_preflight()
    entries = list(_preflight_entries(result))
    entries.extend(_recovery_entries(recovery))
    entries.extend(
        DiagnosticEntry(
            "message",
            f"extra_{index:02d}",
            redact_text(message, home=home),
            STATUS_WARNING,
        )
        for index, message in enumerate(extra_messages, start=1)
    )

    warnings = tuple(
        redact_text(note, home=home)
        for note in result.notes
        if note.strip()
    )

    health_status = "PASS" if result.status == "PASS" else "OPEN"
    if recovery is not None and recovery.state == "failed":
        health_status = "OPEN"

    return DiagnosticReport(
        schema_version="1",
        collection_status="PASS",
        health_status=health_status,
        entries=tuple(entries),
        warnings=warnings,
        redaction_applied=True,
        write_paths_enabled=False,
    )


def format_diagnostic_text(report: DiagnosticReport) -> str:
    lines = [
        "PROVOWARE – Diagnosebericht",
        "==========================",
        f"Sammlung: {report.collection_status}",
        f"Gesundheitsstatus: {report.health_status}",
        "Schreibpfade: GESPERRT",
        "",
    ]
    current_category: str | None = None
    for entry in report.entries:
        if entry.category != current_category:
            current_category = entry.category
            lines.extend([f"[{current_category}]", ""])
        lines.append(f"{entry.status} {entry.key}: {entry.value}")
    if report.warnings:
        lines.extend(["", "[Hinweise]"])
        lines.extend(f"- {warning}" for warning in report.warnings)
    return "\n".join(lines)


def diagnostic_to_json(report: DiagnosticReport) -> str:
    return json.dumps(asdict(report), ensure_ascii=False, indent=2, sort_keys=True)
