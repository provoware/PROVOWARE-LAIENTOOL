"""Read-only application/navigation core shared by GUI and CLI."""

from __future__ import annotations

from dataclasses import dataclass

from .capability_registry import get_use_case, list_use_cases
from .preflight import format_text, run_preflight


@dataclass(frozen=True, slots=True)
class ActionResult:
    use_case_id: str
    title: str
    body: str
    status: str = "PASS"


def available_actions() -> tuple[str, ...]:
    return tuple(
        entry.id
        for entry in list_use_cases()
        if entry.status == "READY"
    )


def execute(use_case_id: str) -> ActionResult:
    entry = get_use_case(use_case_id)
    if entry is None:
        return ActionResult(
            use_case_id=use_case_id,
            title="Funktion nicht gefunden",
            body=(
                "Was ist passiert? Die gewählte Funktion ist nicht registriert.\n"
                "Was bedeutet das? Es wurde nichts ausgeführt und keine Datei verändert.\n"
                "Was kann ich tun? Kehre zur Übersicht zurück und wähle eine angebotene Funktion."
            ),
            status="OPEN",
        )

    if entry.status != "READY":
        return ActionResult(
            use_case_id=use_case_id,
            title=entry.label,
            body=(
                "Was ist passiert? Diese Funktion ist noch nicht freigegeben.\n"
                "Was bedeutet das? Sie bleibt sicher gesperrt.\n"
                "Was kann ich tun? Nutze eine Funktion mit dem Status READY."
            ),
            status=entry.status,
        )

    if use_case_id == "app.overview":
        return ActionResult(
            use_case_id=use_case_id,
            title="Übersicht",
            body=(
                "🔒 Sicherer Lese-Modus\n\n"
                "Dieses PROVOWARE-Grundgerüst verändert keine Dateien.\n"
                "Du kannst den Systemcheck starten oder die Hilfe öffnen.\n"
                "Schreibende Funktionen bleiben gesperrt, bis Preview und Recovery belegt sind."
            ),
        )

    if use_case_id == "app.help":
        return ActionResult(
            use_case_id=use_case_id,
            title="Hilfe",
            body=(
                "1. Beginne mit „Übersicht“.\n"
                "2. Nutze „System prüfen“, um die lokalen Voraussetzungen zu sehen.\n"
                "3. In der Konsole wählst du Funktionen nur über Zahlen.\n"
                "4. Mit 0 gehst du zurück oder beendest das Menü.\n\n"
                "🔒 Im aktuellen Entwicklungsstand werden keine Nutzerdaten verändert."
            ),
        )

    if use_case_id == "system.preflight":
        result = run_preflight()
        return ActionResult(
            use_case_id=use_case_id,
            title="System prüfen",
            body=format_text(result),
            status=result.status,
        )

    return ActionResult(
        use_case_id=use_case_id,
        title=entry.label,
        body=(
            "Was ist passiert? Für diese registrierte Funktion fehlt noch die Application-Ausführung.\n"
            "Was bedeutet das? Es wurde nichts ausgeführt.\n"
            "Was kann ich tun? Nutze eine vollständig implementierte READY-Funktion."
        ),
        status="OPEN",
    )
