"""Shared I31 adapters for the gated diagnostic-export evidence mode.

The normal product shell does not expose this OPEN use case. GUI and CLI test
modes both use this module and therefore the same I26 → I30 → I28 path.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .diagnostic_export import (
    BLOCKED_NOT_AUTHORIZED,
    BLOCKED_PAYLOAD_INVALID,
    BLOCKED_TARGET_EXISTS,
    BLOCKED_TARGET_UNSAFE,
    PASS,
    WRITE_COMMIT_RACE,
    WRITE_IO_ERROR,
    WRITE_NO_SPACE,
    WRITE_PARTIAL_REMAINS,
    WRITE_PERMISSION_ERROR,
    WRITE_VERIFY_FAILED,
)
from .diagnostic_export_authorization import (
    AUTHORIZED,
    CANCELLED,
    CONFIRMED_STAGE_1,
    AuthorizationExecution,
    DiagnosticExportAuthorizationSession,
)
from .diagnostic_export_plan import (
    FORMAT_JSON,
    FORMAT_TEXT,
    ExportPreparation,
    prepare_diagnostic_export,
)
from .diagnostics import DiagnosticReport

FORMAT_LABELS = {
    FORMAT_TEXT: "Klartext",
    FORMAT_JSON: "JSON",
}


@dataclass(frozen=True, slots=True)
class AdapterResult:
    status: str
    title: str
    body: str
    final_path: str | None = None


def default_filename(export_format: str) -> str:
    suffix = "txt" if export_format == FORMAT_TEXT else "json"
    return f"PROVOWARE-Diagnose-I31.{suffix}"


def format_preparation(preparation: ExportPreparation) -> AdapterResult:
    if preparation.status != PASS or preparation.plan is None:
        detail = preparation.errors[0] if preparation.errors else "Exportvorschau konnte nicht erstellt werden."
        return AdapterResult(
            preparation.status,
            "Diagnoseexport nicht bereit",
            (
                f"Was ist passiert? {detail}\n"
                "Was bedeutet das? Es wird keine Diagnosedatei erstellt.\n"
                "Was kann ich jetzt tun? Prüfe Ziel, Dateiname und Diagnosezustand und starte die Vorschau neu."
            ),
        )
    plan = preparation.plan
    return AdapterResult(
        PASS,
        "Diagnoseexport – Vorschau",
        (
            "Es wurde noch nichts geschrieben.\n\n"
            f"Format: {FORMAT_LABELS.get(plan.export_format, plan.export_format)}\n"
            f"Zielordner: {plan.target_dir}\n"
            f"Dateiname: {plan.filename}\n"
            f"Größe: {plan.payload_size_bytes} Byte\n"
            f"SHA-256: {plan.payload_sha256}\n"
            "Overwrite: NEIN\n"
            "Upload/Netzwerk: NEIN\n\n"
            "Nächster Schritt: erste ausdrückliche Bestätigung."
        ),
        final_path=plan.final_path,
    )


def format_execution(execution: AuthorizationExecution) -> AdapterResult:
    result = execution.writer_result
    final_path = result.final_path if result is not None else None
    status = execution.status
    if status == PASS and result is not None:
        return AdapterResult(
            PASS,
            "Diagnosedatei erstellt",
            (
                "Was ist passiert? Genau eine neue Diagnosedatei wurde erstellt.\n"
                "Was bedeutet das? Bestehende Dateien wurden nicht überschrieben und es wurden keine Daten hochgeladen.\n"
                f"Was kann ich jetzt tun? Die Datei liegt unter: {result.final_path}\n"
                f"Größe: {result.bytes_written} Byte"
            ),
            final_path=result.final_path,
        )

    messages = {
        BLOCKED_TARGET_EXISTS: (
            "Der Dateiname ist bereits vorhanden.",
            "PROVOWARE überschreibt die bestehende Datei nicht.",
            "Wähle einen anderen Dateinamen oder einen anderen Zielordner.",
        ),
        WRITE_NO_SPACE: (
            "Der Datenträger hat nicht genug freien Speicher.",
            "Der Export wurde nicht erfolgreich abgeschlossen.",
            "Schaffe Speicherplatz oder wähle einen anderen Test-Zielordner.",
        ),
        WRITE_PERMISSION_ERROR: (
            "Der Zielordner erlaubt das Erstellen der Datei nicht.",
            "Es wurde kein erfolgreicher Export veröffentlicht.",
            "Prüfe die Zugriffsrechte oder wähle einen anderen Test-Zielordner.",
        ),
        WRITE_PARTIAL_REMAINS: (
            "Der Schreibvorgang wurde nicht vollständig aufgeräumt.",
            "Eine Partial-Datei kann zurückgeblieben sein; der Ergebnisstatus muss geprüft werden.",
            "Lösche nichts automatisch. Prüfe zuerst die gemeldeten Pfade.",
        ),
        WRITE_COMMIT_RACE: (
            "Der Zielname wurde während des Exports belegt.",
            "PROVOWARE hat die vorhandene Datei nicht überschrieben.",
            "Starte mit einem neuen Dateinamen erneut.",
        ),
        WRITE_VERIFY_FAILED: (
            "Die geschriebene Partial-Datei bestand die Hash-/Größenprüfung nicht.",
            "Sie wurde nicht als erfolgreicher Export veröffentlicht.",
            "Starte den Export nicht automatisch erneut; prüfe zuerst den Datenträger.",
        ),
        WRITE_IO_ERROR: (
            "Beim Schreiben trat ein Ein-/Ausgabefehler auf.",
            "Der Export ist nicht als erfolgreich bestätigt.",
            "Prüfe den Datenträger und starte danach einen neuen Exportvorgang.",
        ),
        BLOCKED_TARGET_UNSAFE: (
            "Der Zielpfad erfüllt den Sicherheitsvertrag nicht.",
            "Der Writer bleibt gesperrt.",
            "Wähle einen vorhandenen echten Ordner ohne Symlink.",
        ),
        BLOCKED_PAYLOAD_INVALID: (
            "Diagnosedaten und bestätigter Exportplan stimmen nicht mehr überein.",
            "Die Autorisierung wurde aus Sicherheitsgründen nicht ausgeführt.",
            "Erzeuge eine neue Vorschau und bestätige erneut.",
        ),
        BLOCKED_NOT_AUTHORIZED: (
            "Die vollständige Doppelbestätigung fehlt.",
            "Der Writer bleibt gesperrt.",
            "Beginne den Bestätigungsablauf erneut.",
        ),
        CANCELLED: (
            "Der Export wurde abgebrochen.",
            "Es wird keine neue Diagnosedatei erstellt.",
            "Du kannst den Prüfablauf später neu starten.",
        ),
    }
    happened, meaning, next_step = messages.get(
        status,
        (
            "Der Diagnoseexport wurde nicht erfolgreich abgeschlossen.",
            "Der Status ist fail-closed; ein Erfolg wird nicht angenommen.",
            "Prüfe den angezeigten Status und starte nur mit einer neuen Vorschau erneut.",
        ),
    )
    return AdapterResult(
        status,
        "Diagnoseexport – nicht abgeschlossen",
        (
            f"Was ist passiert? {happened}\n"
            f"Was bedeutet das? {meaning}\n"
            f"Was kann ich jetzt tun? {next_step}"
        ),
        final_path=final_path,
    )


class DiagnosticExportAdapterSession:
    """Common adapter-facing state for the gated I31 workflow."""

    def __init__(
        self,
        report: DiagnosticReport,
        *,
        target_dir: Path,
        export_format: str,
        filename: str | None = None,
    ) -> None:
        self.preparation = prepare_diagnostic_export(
            report,
            target_dir=target_dir,
            export_format=export_format,
            filename=filename or default_filename(export_format),
        )
        self.authorization: DiagnosticExportAuthorizationSession | None = None
        if self.preparation.status == PASS:
            self.authorization = DiagnosticExportAuthorizationSession(self.preparation)

    def preview(self) -> AdapterResult:
        return format_preparation(self.preparation)

    def confirm_stage1(self) -> AdapterResult:
        if self.authorization is None:
            return self.preview()
        decision = self.authorization.confirm_stage1(self.preparation)
        if decision.status == CONFIRMED_STAGE_1:
            return AdapterResult(
                decision.status,
                "Erste Bestätigung angenommen",
                (
                    "Es wurde noch nichts geschrieben.\n"
                    "Die Exportzusammenfassung bleibt unverändert.\n"
                    "Für das tatsächliche Erstellen ist noch die zweite ausdrückliche Bestätigung erforderlich."
                ),
                final_path=self.preparation.plan.final_path if self.preparation.plan else None,
            )
        return AdapterResult(decision.status, "Bestätigung blockiert", "\n".join(decision.errors))

    def confirm_and_execute(self) -> AdapterResult:
        if self.authorization is None:
            return self.preview()
        decision = self.authorization.confirm_stage2(self.preparation)
        if decision.status != AUTHORIZED or decision.request is None:
            return AdapterResult(
                decision.status,
                "Finale Bestätigung blockiert",
                "\n".join(decision.errors) or "Der Writer wurde nicht aufgerufen.",
            )
        return format_execution(self.authorization.execute(decision.request))

    def cancel(self) -> AdapterResult:
        if self.authorization is None:
            return AdapterResult(
                CANCELLED,
                "Diagnoseexport abgebrochen",
                "Es wurde keine Diagnosedatei erstellt.",
            )
        decision = self.authorization.cancel()
        return AdapterResult(
            decision.status,
            "Diagnoseexport abgebrochen",
            "Es wurde keine Diagnosedatei erstellt.",
        )


def run_cli_export_evidence_flow(
    report: DiagnosticReport,
    *,
    target_dir: Path,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> str:
    """Run the I31 gated numeric adapter against a supplied test target."""
    output_fn("PROVOWARE – Diagnose lokal speichern · Prüfmodus")
    output_fn("Nur der ausdrücklich bereitgestellte Testordner wird verwendet.")
    output_fn("")
    output_fn("1  Klartext")
    output_fn("2  JSON")
    output_fn("0  Abbrechen")
    choice = input_fn("Format: ").strip()
    if choice == "0":
        output_fn("Abgebrochen. Es wurde keine Diagnosedatei erstellt.")
        return CANCELLED
    formats = {"1": FORMAT_TEXT, "2": FORMAT_JSON}
    if choice not in formats:
        output_fn("Ungültige Auswahl. Es wurde keine Diagnosedatei erstellt.")
        return "OPEN"

    session = DiagnosticExportAdapterSession(
        report,
        target_dir=target_dir,
        export_format=formats[choice],
    )
    preview = session.preview()
    output_fn("")
    output_fn(preview.title)
    output_fn(preview.body)
    if preview.status != PASS:
        return preview.status

    output_fn("")
    output_fn("1  Weiter zur finalen Bestätigung")
    output_fn("0  Abbrechen")
    if input_fn("Erste Bestätigung: ").strip() != "1":
        cancelled = session.cancel()
        output_fn(cancelled.body)
        return cancelled.status

    stage1 = session.confirm_stage1()
    output_fn(stage1.body)
    if stage1.status != CONFIRMED_STAGE_1:
        return stage1.status

    output_fn("")
    output_fn("Es wird genau eine neue Diagnosedatei erstellt.")
    output_fn("Bestehende Dateien werden nicht überschrieben.")
    output_fn("Es werden keine Daten hochgeladen.")
    output_fn("1  Diagnosedatei jetzt neu erstellen")
    output_fn("0  Abbrechen")
    if input_fn("Finale Bestätigung: ").strip() != "1":
        cancelled = session.cancel()
        output_fn(cancelled.body)
        return cancelled.status

    result = session.confirm_and_execute()
    output_fn("")
    output_fn(result.title)
    output_fn(result.body)
    return result.status
