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
    ACTION_COPY,
    ACTION_MOVE,
    ACTION_TRASH,
    PreviewCheck,
    PreviewItem,
    PreviewPlan,
    make_plan,
    validate_preview,
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


@dataclass(frozen=True, slots=True)
class TargetPreviewPreparation:
    inventory: InventoryResult
    plan: PreviewPlan | None
    check: PreviewCheck | None
    errors: tuple[str, ...]
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



def _prepare_same_root_target_preview(
    action: str,
    root: Path,
    selected_relative_paths: tuple[str, ...],
    target_dir: Path,
) -> TargetPreviewPreparation:
    """Build a copy/move preview inside one validated root without writing."""
    if action not in {ACTION_COPY, ACTION_MOVE}:
        raise ValueError(f"Nicht unterstützte Zielaktion: {action}")

    inventory = scan_inventory(root)
    if not inventory.root_allowed:
        return TargetPreviewPreparation(
            inventory, None, None, ("Wurzel ist blockiert.",), "BLOCKED"
        )
    if not inventory.complete:
        return TargetPreviewPreparation(
            inventory,
            None,
            None,
            ("Inventar ist unvollständig.",),
            "OPEN",
        )
    if not selected_relative_paths:
        return TargetPreviewPreparation(
            inventory,
            None,
            None,
            ("Keine Datei ausgewählt.",),
            "OPEN",
        )

    resolved_root = Path(inventory.root)
    target_dir_decision = validate_path(
        resolved_root,
        target_dir,
        allow_symlink=False,
        must_exist=True,
    )
    if not target_dir_decision.allowed or target_dir_decision.resolved is None:
        return TargetPreviewPreparation(
            inventory,
            None,
            None,
            (f"Zielordner blockiert: {target_dir_decision.reason}",),
            "BLOCKED",
        )

    resolved_target_dir = Path(target_dir_decision.resolved)
    if not resolved_target_dir.is_dir():
        return TargetPreviewPreparation(
            inventory,
            None,
            None,
            ("Ziel muss ein vorhandener Ordner sein.",),
            "BLOCKED",
        )

    inventory_by_relative = {
        item.relative_path: item
        for item in inventory.items
    }
    errors: list[str] = []
    items: list[PreviewItem] = []
    seen_selection: set[str] = set()

    for index, relative_path in enumerate(selected_relative_paths, start=1):
        if relative_path in seen_selection:
            errors.append(f"Doppelte Auswahl: {relative_path}")
            continue
        seen_selection.add(relative_path)

        inventory_item = inventory_by_relative.get(relative_path)
        if inventory_item is None:
            errors.append(f"Auswahl nicht im aktuellen Inventar: {relative_path}")
            continue

        source = resolved_root / relative_path
        target = resolved_target_dir / Path(relative_path).name

        if target.exists():
            errors.append(f"Ziel existiert bereits: {target}")
            continue

        source_decision = validate_path(
            resolved_root,
            source,
            allow_symlink=False,
            must_exist=True,
        )
        if not source_decision.allowed:
            errors.append(
                f"Quelle blockiert: {relative_path}: {source_decision.reason}"
            )
            continue

        target_decision = validate_path(
            resolved_root,
            target,
            allow_symlink=False,
            must_exist=False,
        )
        if not target_decision.allowed:
            errors.append(
                f"Ziel blockiert: {relative_path}: {target_decision.reason}"
            )
            continue

        if source_decision.resolved == target_decision.resolved:
            errors.append(f"Quelle und Ziel sind identisch: {relative_path}")
            continue

        effect_verb = "kopiert" if action == ACTION_COPY else "verschoben"
        recovery_hint = (
            "Die später erzeugte Kopie müsste eindeutig entfernbar bleiben."
            if action == ACTION_COPY
            else "Die Datei müsste später an den Ursprungsort zurückverschiebbar bleiben."
        )
        items.append(
            PreviewItem(
                id=f"{action}-{index:06d}",
                action=action,
                source=str(source),
                target=str(target),
                bytes_estimate=inventory_item.size_bytes,
                effect=(
                    f"„{relative_path}“ würde nach "
                    f"„{target.relative_to(resolved_root).as_posix()}“ {effect_verb}."
                ),
                reversible=True,
                recovery_hint=recovery_hint,
            )
        )

    if errors:
        return TargetPreviewPreparation(
            inventory,
            None,
            None,
            tuple(errors),
            "BLOCKED",
        )

    plan = make_plan(resolved_root, tuple(items))
    check = validate_preview(plan)
    if not check.allowed:
        return TargetPreviewPreparation(
            inventory,
            plan,
            check,
            check.errors,
            "BLOCKED",
        )

    return TargetPreviewPreparation(
        inventory,
        plan,
        check,
        (),
        "PASS",
    )


def prepare_copy_preview(
    root: Path,
    selected_relative_paths: tuple[str, ...],
    target_dir: Path,
) -> TargetPreviewPreparation:
    """Build a read-only same-root copy preview."""
    return _prepare_same_root_target_preview(
        ACTION_COPY,
        root,
        selected_relative_paths,
        target_dir,
    )


def prepare_move_preview(
    root: Path,
    selected_relative_paths: tuple[str, ...],
    target_dir: Path,
) -> TargetPreviewPreparation:
    """Build a read-only same-root move preview."""
    return _prepare_same_root_target_preview(
        ACTION_MOVE,
        root,
        selected_relative_paths,
        target_dir,
    )


def available_actions() -> tuple[str, ...]:
    return tuple(
        entry.id
        for entry in list_use_cases()
        if entry.status == "READY"
    )


def action_requires_root(use_case_id: str) -> bool:
    """Return whether an adapter must collect one explicit root path."""
    return use_case_id == "files.preview_trash"


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


def execute(use_case_id: str, *, root: str | None = None) -> ActionResult:
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
