"""Shared GUI/CLI capability registry.

This module is dependency-free and contains only immutable metadata.
Adapters may read it, but business rules stay in the application/domain core.
"""

from __future__ import annotations

from dataclasses import dataclass

STATUS_READY = "READY"
STATUS_OPEN = "OPEN"
STATUS_BLOCKED = "BLOCKED"
VALID_STATUSES = {STATUS_READY, STATUS_OPEN, STATUS_BLOCKED}

SAFETY_READ_ONLY = "read-only"
SAFETY_PREVIEW_REQUIRED = "preview-required"
SAFETY_RECOVERY_REQUIRED = "recovery-required"
SAFETY_EXPLICIT_WRITE_CONFIRMATION = "explicit-write-confirmation"
VALID_SAFETY_CLASSES = {
    SAFETY_READ_ONLY,
    SAFETY_PREVIEW_REQUIRED,
    SAFETY_RECOVERY_REQUIRED,
    SAFETY_EXPLICIT_WRITE_CONFIRMATION,
}


@dataclass(frozen=True, slots=True)
class UseCaseCapability:
    id: str
    label: str
    gui_available: bool
    cli_available: bool
    diagnostic_cli_only: bool
    safety_class: str
    preview_required: bool
    recovery_required: bool
    required_capability: str | None
    status: str


REGISTRY: tuple[UseCaseCapability, ...] = (
    UseCaseCapability(
        id="app.overview",
        label="Übersicht",
        gui_available=True,
        cli_available=True,
        diagnostic_cli_only=False,
        safety_class=SAFETY_READ_ONLY,
        preview_required=False,
        recovery_required=False,
        required_capability=None,
        status=STATUS_READY,
    ),
    UseCaseCapability(
        id="system.preflight",
        label="System prüfen",
        gui_available=True,
        cli_available=True,
        diagnostic_cli_only=False,
        safety_class=SAFETY_READ_ONLY,
        preview_required=False,
        recovery_required=False,
        required_capability=None,
        status=STATUS_READY,
    ),
    UseCaseCapability(
        id="files.preview_trash",
        label="Dateivorschau",
        gui_available=True,
        cli_available=True,
        diagnostic_cli_only=False,
        safety_class=SAFETY_READ_ONLY,
        preview_required=False,
        recovery_required=False,
        required_capability=None,
        status=STATUS_READY,
    ),
    UseCaseCapability(
        id="files.preview_copy",
        label="Kopieren – Vorschau",
        gui_available=True,
        cli_available=True,
        diagnostic_cli_only=False,
        safety_class=SAFETY_PREVIEW_REQUIRED,
        preview_required=True,
        recovery_required=False,
        required_capability=None,
        status=STATUS_OPEN,
    ),
    UseCaseCapability(
        id="files.preview_move",
        label="Verschieben – Vorschau",
        gui_available=True,
        cli_available=True,
        diagnostic_cli_only=False,
        safety_class=SAFETY_PREVIEW_REQUIRED,
        preview_required=True,
        recovery_required=False,
        required_capability=None,
        status=STATUS_OPEN,
    ),
    UseCaseCapability(
        id="diagnostics.export_local",
        label="Diagnose lokal speichern",
        gui_available=False,
        cli_available=False,
        diagnostic_cli_only=False,
        safety_class=SAFETY_EXPLICIT_WRITE_CONFIRMATION,
        preview_required=True,
        recovery_required=False,
        required_capability=None,
        status=STATUS_OPEN,
    ),
    UseCaseCapability(
        id="diagnostics.snapshot",
        label="Diagnose anzeigen",
        gui_available=False,
        cli_available=True,
        diagnostic_cli_only=True,
        safety_class=SAFETY_READ_ONLY,
        preview_required=False,
        recovery_required=False,
        required_capability=None,
        status=STATUS_READY,
    ),
    UseCaseCapability(
        id="app.help",
        label="Hilfe",
        gui_available=True,
        cli_available=True,
        diagnostic_cli_only=False,
        safety_class=SAFETY_READ_ONLY,
        preview_required=False,
        recovery_required=False,
        required_capability=None,
        status=STATUS_READY,
    ),
)


def validate_registry(
    entries: tuple[UseCaseCapability, ...] = REGISTRY,
) -> tuple[str, ...]:
    """Return contract violations without mutating registry state."""
    errors: list[str] = []
    seen_ids: set[str] = set()

    for entry in entries:
        if not entry.id or "." not in entry.id:
            errors.append(f"Ungültige Funktions-ID: {entry.id!r}")
        if entry.id in seen_ids:
            errors.append(f"Doppelte Funktions-ID: {entry.id}")
        seen_ids.add(entry.id)

        if not entry.label.strip():
            errors.append(f"Leerer Anzeigename: {entry.id}")
        if entry.status not in VALID_STATUSES:
            errors.append(f"Ungültiger Status bei {entry.id}: {entry.status}")
        if entry.safety_class not in VALID_SAFETY_CLASSES:
            errors.append(
                f"Ungültige Sicherheitsklasse bei {entry.id}: {entry.safety_class}"
            )
        if entry.gui_available and not entry.cli_available:
            errors.append(
                f"GUI-Fachfunktion ohne CLI-Parität: {entry.id}"
            )
        if entry.diagnostic_cli_only and entry.gui_available:
            errors.append(
                f"diagnostic_cli_only widerspricht GUI-Verfügbarkeit: {entry.id}"
            )
        if entry.preview_required and entry.safety_class == SAFETY_READ_ONLY:
            errors.append(
                f"Read-only-Funktion darf keine Schreib-Preview verlangen: {entry.id}"
            )
        if entry.recovery_required and not entry.preview_required:
            errors.append(
                f"Recovery-Pflicht ohne Preview-Pflicht: {entry.id}"
            )
        if (
            entry.safety_class == SAFETY_EXPLICIT_WRITE_CONFIRMATION
            and not entry.preview_required
        ):
            errors.append(
                f"Expliziter Write ohne Preview-Pflicht: {entry.id}"
            )
        if entry.status == STATUS_READY and not (
            entry.cli_available or entry.gui_available
        ):
            errors.append(
                f"READY-Funktion ohne verfügbaren Adapter: {entry.id}"
            )

    return tuple(errors)


def get_use_case(use_case_id: str) -> UseCaseCapability | None:
    for entry in REGISTRY:
        if entry.id == use_case_id:
            return entry
    return None


def list_use_cases() -> tuple[UseCaseCapability, ...]:
    return REGISTRY
