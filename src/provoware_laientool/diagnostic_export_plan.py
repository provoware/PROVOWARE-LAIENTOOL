"""Read-only diagnostic export preflight.

I26 prepares and validates export payloads/plans only. It never creates,
modifies, renames or deletes filesystem objects.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .diagnostics import (
    DiagnosticReport,
    diagnostic_to_json,
    format_diagnostic_text,
    redact_text,
)

FORMAT_JSON = "json"
FORMAT_TEXT = "text"
VALID_FORMATS = {FORMAT_JSON, FORMAT_TEXT}


@dataclass(frozen=True, slots=True)
class ExportPlan:
    target_dir: str
    filename: str
    final_path: str
    export_format: str
    payload_size_bytes: int
    payload_sha256: str
    overwrite_allowed: bool = False
    write_enabled: bool = False


@dataclass(frozen=True, slots=True)
class ExportPreparation:
    status: str
    errors: tuple[str, ...]
    payload: bytes | None
    plan: ExportPlan | None


def _serialize(report: DiagnosticReport, export_format: str) -> bytes:
    if export_format == FORMAT_JSON:
        text = diagnostic_to_json(report)
    elif export_format == FORMAT_TEXT:
        text = format_diagnostic_text(report)
    else:
        raise ValueError(f"Unbekanntes Exportformat: {export_format}")
    return text.encode("utf-8")


def _filename_error(filename: str, export_format: str) -> str | None:
    if not filename or filename in {".", ".."}:
        return "Export-Dateiname fehlt oder ist ungültig."
    if Path(filename).name != filename or "/" in filename or "\\" in filename:
        return "Export-Dateiname darf keinen Pfad enthalten."
    expected_suffix = ".json" if export_format == FORMAT_JSON else ".txt"
    if not filename.lower().endswith(expected_suffix):
        return f"Export-Dateiname muss auf {expected_suffix} enden."
    return None


def prepare_diagnostic_export(
    report: DiagnosticReport,
    *,
    target_dir: Path,
    export_format: str,
    filename: str,
) -> ExportPreparation:
    """Build a deterministic no-write export payload and immutable plan."""
    errors: list[str] = []

    if export_format not in VALID_FORMATS:
        errors.append(f"Unbekanntes Exportformat: {export_format}")

    if not report.redaction_applied:
        errors.append("Diagnosebericht ist nicht als redigiert markiert.")

    if report.write_paths_enabled:
        errors.append("Diagnosebericht enthält eine unzulässige Schreibfreigabe.")

    if target_dir.is_symlink():
        errors.append("Zielordner ist eine Verknüpfung (Symlink).")
    elif not target_dir.exists():
        errors.append("Zielordner existiert nicht.")
    elif not target_dir.is_dir():
        errors.append("Gewähltes Ziel ist kein Ordner.")

    if export_format in VALID_FORMATS:
        filename_error = _filename_error(filename, export_format)
        if filename_error:
            errors.append(filename_error)

    if errors:
        return ExportPreparation("BLOCKED", tuple(errors), None, None)

    try:
        resolved_dir = target_dir.resolve(strict=True)
    except OSError as exc:
        return ExportPreparation(
            "BLOCKED",
            (f"Zielordner konnte nicht sicher aufgelöst werden: {exc}",),
            None,
            None,
        )

    final_path = resolved_dir / filename
    if final_path.is_symlink():
        errors.append("Zieldatei ist bereits eine Verknüpfung (Symlink).")
    elif final_path.exists():
        errors.append("Zieldatei existiert bereits; Overwrite ist verboten.")

    if errors:
        return ExportPreparation("BLOCKED", tuple(errors), None, None)

    payload = _serialize(report, export_format)
    try:
        payload_text = payload.decode("utf-8")
    except UnicodeDecodeError:
        return ExportPreparation(
            "BLOCKED",
            ("Export-Payload ist nicht gültiges UTF-8.",),
            None,
            None,
        )

    if redact_text(payload_text) != payload_text:
        return ExportPreparation(
            "BLOCKED",
            ("Export-Payload enthält noch redigierbare sensible Inhalte.",),
            None,
            None,
        )

    digest = hashlib.sha256(payload).hexdigest()
    plan = ExportPlan(
        target_dir=str(resolved_dir),
        filename=filename,
        final_path=str(final_path),
        export_format=export_format,
        payload_size_bytes=len(payload),
        payload_sha256=digest,
        overwrite_allowed=False,
        write_enabled=False,
    )
    return ExportPreparation("PASS", (), payload, plan)
