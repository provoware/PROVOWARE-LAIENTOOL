"""Read-only application/navigation core shared by GUI and CLI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .capability_registry import get_use_case, list_use_cases
from .diagnostics import build_diagnostic_report, format_diagnostic_text
from .inventory import InventoryResult, scan_inventory
from .inventory_view import InventoryView, InventoryViewSpec, build_inventory_view
from .preflight import format_text, run_preflight
from .preview_model import (
    ACTION_TRASH,
    PreviewCheck,
    PreviewItem,
    PreviewPlan,
    make_plan,
    validate_preview,
)
from .transfer_application import (
    TargetDirectoryPreparation,
    TargetPreviewPreparation,
    prepare_copy_preview,
    prepare_move_preview,
    prepare_target_directories,
)


@dataclass(frozen=True, slots=True)
class ActionResult:
    use_case_id: str
    title: str
    body: str
    status: str = "PASS"


@dataclass(frozen=True, slots=True)
class PreviewPreparation:
    inventory: InventoryResult
    plan: PreviewPlan | None
    check: PreviewCheck | None
    status: str


@dataclass(frozen=True, slots=True)
class InventoryViewPreparation:
    inventory: InventoryResult
    view: InventoryView | None
    status: str



def prepare_inventory_view(
    root: Path,
    spec: InventoryViewSpec = InventoryViewSpec(),
) -> InventoryViewPreparation:
    """Build a read-only filtered/sorted view through the shared core."""
    inventory = scan_inventory(root)
    if not inventory.root_allowed:
        return InventoryViewPreparation(inventory, None, "BLOCKED")
    if not inventory.complete:
        return InventoryViewPreparation(inventory, None, "OPEN")
    return InventoryViewPreparation(
        inventory=inventory,
        view=build_inventory_view(inventory, spec),
        status="PASS",
    )




def available_actions() -> tuple[str, ...]:
    return tuple(
        entry.id
        for entry in list_use_cases()
        if entry.status == "READY"
    )


TRANSFER_PREVIEW_IDS = ("files.preview_copy", "files.preview_move")


def action_requires_root(use_case_id: str) -> bool:
    """Return whether an adapter must collect one explicit root path."""
    return use_case_id == "files.preview_trash" or use_case_id in TRANSFER_PREVIEW_IDS


def _format_target_preview(
    use_case_id: str,
    preparation: TargetPreviewPreparation,
) -> ActionResult:
    title = (
        "Kopieren – Vorschau"
        if use_case_id == "files.preview_copy"
        else "Verschieben – Vorschau"
    )
    if preparation.status != "PASS" or preparation.plan is None:
        errors = preparation.errors or ("Die Vorschau ist noch nicht vollständig.",)
        return ActionResult(
            use_case_id=use_case_id,
            title=title,
            body=(
                "Was ist passiert? Die Transfer-Vorschau wurde nicht freigegeben.\n"
                "Was bedeutet das? Es wird nichts kopiert oder verschoben.\n"
                "Befunde:\n- "
                + "\n- ".join(errors)
                + "\nWas kann ich tun? Prüfe Auswahl und Zielordner und versuche es erneut.\n\n"
                "🔒 Es wurden keine Dateien verändert."
            ),
            status=preparation.status,
        )

    plan = preparation.plan
    root = Path(plan.root)
    first_target = Path(plan.items[0].target or root)
    try:
        target_label = first_target.parent.relative_to(root).as_posix() or "."
    except ValueError:
        target_label = first_target.parent.name

    lines = [
        "🔒 Reine Vorschau – es wird nichts ausgeführt.",
        "",
        f"Aktion: {'Kopieren' if use_case_id == 'files.preview_copy' else 'Verschieben'}",
        f"Dateien: {plan.total_items}",
        f"Gesamtgröße: {plan.total_bytes_estimate} Byte",
        f"Zielordner innerhalb der gewählten Wurzel: {target_label}",
        "",
        "Geplante Wirkung:",
    ]
    for item in plan.items[:10]:
        lines.append(f"- {item.effect}")
    if len(plan.items) > 10:
        lines.append(f"- … plus {len(plan.items) - 10} weitere")
    lines.extend(
        [
            "",
            "Rückweg:",
            "Alle Einträge sind im aktuellen Preview-Vertrag als reversibel markiert.",
            "Ein Executor ist weiterhin gesperrt.",
            "",
            "🔒 Es wurden keine Dateien verändert.",
        ]
    )
    return ActionResult(
        use_case_id=use_case_id,
        title=title,
        body="\n".join(lines),
        status="PASS",
    )


def prepare_trash_preview(root: Path) -> PreviewPreparation:
    """Turn a complete read-only inventory into a reversible trash preview."""
    inventory = scan_inventory(root)

    if not inventory.root_allowed:
        return PreviewPreparation(inventory, None, None, "BLOCKED")

    if not inventory.complete:
        return PreviewPreparation(inventory, None, None, "OPEN")

    if not inventory.items:
        return PreviewPreparation(inventory, None, None, "OPEN")

    resolved_root = Path(inventory.root)
    items = tuple(
        PreviewItem(
            id=f"inventory-{index:06d}",
            action=ACTION_TRASH,
            source=str(resolved_root / item.relative_path),
            target=None,
            bytes_estimate=item.size_bytes,
            effect=f"„{item.relative_path}“ würde in den Papierkorb verschoben.",
            reversible=True,
            recovery_hint="Die Datei soll aus dem Papierkorb wiederherstellbar bleiben.",
        )
        for index, item in enumerate(inventory.items, start=1)
    )
    plan = make_plan(resolved_root, items)
    check = validate_preview(plan)

    return PreviewPreparation(
        inventory=inventory,
        plan=plan,
        check=check,
        status="PASS" if check.allowed else "BLOCKED",
    )


def _format_preview(preparation: PreviewPreparation) -> ActionResult:
    inventory = preparation.inventory

    if not inventory.root_allowed:
        reason = inventory.issues[0].message if inventory.issues else "Wurzel ist blockiert."
        return ActionResult(
            use_case_id="files.preview_trash",
            title="Dateivorschau",
            body=(
                f"Was ist passiert? Der gewählte Ordner wurde blockiert: {reason}\n"
                "Was bedeutet das? Es wurde kein Inventar und keine Vorschau freigegeben.\n"
                "Was kann ich tun? Wähle einen vorhandenen, sicher auflösbaren Ordner."
            ),
            status="BLOCKED",
        )

    if not inventory.complete:
        return ActionResult(
            use_case_id="files.preview_trash",
            title="Dateivorschau",
            body=(
                "Was ist passiert? Der Ordner konnte nicht vollständig gelesen werden.\n"
                f"Gefundene Dateien: {inventory.file_count}; Befunde: {len(inventory.issues)}.\n"
                "Was bedeutet das? Aus unvollständigen Daten wird keine Aktionsvorschau erzeugt.\n"
                "Was kann ich tun? Prüfe die gemeldeten Zugriffs-/Pfadprobleme und starte erneut.\n\n"
                "🔒 Es wurden keine Dateien verändert."
            ),
            status="OPEN",
        )

    if preparation.plan is None:
        return ActionResult(
            use_case_id="files.preview_trash",
            title="Dateivorschau",
            body=(
                "Der gewählte Ordner enthält keine regulären Dateien für diese Vorschau.\n\n"
                "🔒 Es wurden keine Dateien verändert."
            ),
            status="OPEN",
        )

    if preparation.check is None or not preparation.check.allowed:
        errors = preparation.check.errors if preparation.check else ("Preview-Prüfung fehlt.",)
        return ActionResult(
            use_case_id="files.preview_trash",
            title="Dateivorschau",
            body=(
                "Was ist passiert? Die Vorschau wurde aus Sicherheitsgründen blockiert.\n"
                "Was bedeutet das? Mindestens eine Preview-Regel ist nicht erfüllt.\n"
                "Befunde:\n- "
                + "\n- ".join(errors)
                + "\nWas kann ich tun? Nutze keine Dateiaktion und prüfe zuerst die Befunde.\n\n"
                "🔒 Es wurden keine Dateien verändert."
            ),
            status="BLOCKED",
        )

    plan = preparation.plan
    skipped = len(inventory.issues)
    lines = [
        "🔒 Reine Vorschau – es wird nichts ausgeführt.",
        "",
        f"Ordner: {inventory.root}",
        f"Reguläre Dateien: {plan.total_items}",
        f"Gesamtgröße: {plan.total_bytes_estimate} Byte",
        f"Bewusst übersprungene Hinweise: {skipped}",
        "",
        "Geplante Wirkung:",
        "Die aufgeführten regulären Dateien würden später nur reversibel in den Papierkorb verschoben.",
        "Ein Executor ist weiterhin gesperrt.",
    ]
    if plan.items:
        lines.extend(["", "Erste Einträge:"])
        for item in plan.items[:10]:
            lines.append(f"- {Path(item.source).relative_to(Path(plan.root)).as_posix()}")
        if len(plan.items) > 10:
            lines.append(f"- … plus {len(plan.items) - 10} weitere")

    return ActionResult(
        use_case_id="files.preview_trash",
        title="Dateivorschau",
        body="\n".join(lines),
        status="PASS",
    )


def execute(
    use_case_id: str,
    *,
    root: str | None = None,
    selected_relative_paths: tuple[str, ...] = (),
    target_dir: str | None = None,
) -> ActionResult:
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

    if entry.status != "READY" and use_case_id not in TRANSFER_PREVIEW_IDS:
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

    if use_case_id in TRANSFER_PREVIEW_IDS:
        if root is None or not root.strip():
            return ActionResult(
                use_case_id=use_case_id,
                title=entry.label,
                body=(
                    "Was ist passiert? Es wurde kein Ordner ausgewählt.\n"
                    "Was bedeutet das? Es wurde keine Transfer-Vorschau erzeugt.\n"
                    "Was kann ich tun? Wähle zuerst ausdrücklich einen Ordner.\n\n"
                    "🔒 Es wurden keine Dateien verändert."
                ),
                status="OPEN",
            )
        if target_dir is None or not target_dir.strip():
            return ActionResult(
                use_case_id=use_case_id,
                title=entry.label,
                body=(
                    "Was ist passiert? Es wurde kein Zielordner ausgewählt.\n"
                    "Was bedeutet das? Es wird nichts kopiert oder verschoben.\n"
                    "Was kann ich tun? Wähle einen vorhandenen Zielordner innerhalb der Wurzel.\n\n"
                    "🔒 Es wurden keine Dateien verändert."
                ),
                status="OPEN",
            )
        preparation = (
            prepare_copy_preview(Path(root), selected_relative_paths, Path(target_dir))
            if use_case_id == "files.preview_copy"
            else prepare_move_preview(Path(root), selected_relative_paths, Path(target_dir))
        )
        return _format_target_preview(use_case_id, preparation)

    if use_case_id == "app.overview":
        return ActionResult(
            use_case_id=use_case_id,
            title="Übersicht",
            body=(
                "🔒 Sicherer Lese-Modus\n\n"
                "Dieses PROVOWARE-Grundgerüst verändert keine Dateien.\n"
                "Du kannst den Systemcheck starten, eine reine Dateivorschau erzeugen "
                "oder die Hilfe öffnen.\n"
                "Schreibende Funktionen bleiben weiterhin gesperrt."
            ),
        )

    if use_case_id == "app.help":
        return ActionResult(
            use_case_id=use_case_id,
            title="Hilfe",
            body=(
                "1. Beginne mit „Übersicht“.\n"
                "2. Nutze „System prüfen“, um die lokalen Voraussetzungen zu sehen.\n"
                "3. „Dateivorschau“ liest einen von dir gewählten Ordner und zeigt nur, "
                "was später passieren würde.\n"
                "4. In der Konsole wählst du Funktionen nur über Zahlen.\n"
                "5. Mit 0 gehst du zurück oder beendest das Menü.\n\n"
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

    if use_case_id == "diagnostics.snapshot":
        report = build_diagnostic_report()
        return ActionResult(
            use_case_id=use_case_id,
            title="Diagnose anzeigen",
            body=format_diagnostic_text(report),
            status=report.health_status,
        )

    if use_case_id == "files.preview_trash":
        if root is None or not root.strip():
            return ActionResult(
                use_case_id=use_case_id,
                title="Dateivorschau",
                body=(
                    "Was ist passiert? Es wurde kein Ordner ausgewählt.\n"
                    "Was bedeutet das? Es wurde nichts gelesen und keine Datei verändert.\n"
                    "Was kann ich tun? Wähle ausdrücklich einen Ordner für die reine Vorschau."
                ),
                status="OPEN",
            )
        return _format_preview(prepare_trash_preview(Path(root)))

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
