"""Read-only same-root transfer preview application services.

This module owns target-directory discovery and copy/move preview preparation.
It performs no file writes and intentionally has no executor.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from .inventory import InventoryResult, scan_inventory
from .path_policy import validate_path
from .preview_model import (
    ACTION_COPY,
    ACTION_MOVE,
    PreviewCheck,
    PreviewItem,
    PreviewPlan,
    make_plan,
    validate_preview,
)


@dataclass(frozen=True, slots=True)
class TargetPreviewPreparation:
    inventory: InventoryResult
    plan: PreviewPlan | None
    check: PreviewCheck | None
    errors: tuple[str, ...]
    status: str


@dataclass(frozen=True, slots=True)
class TargetDirectoryPreparation:
    root: str
    directories: tuple[str, ...]
    errors: tuple[str, ...]
    status: str


def prepare_target_directories(root: Path) -> TargetDirectoryPreparation:
    """List only existing, non-symlink directories inside one validated root."""
    root_decision = validate_path(
        root,
        root,
        allow_symlink=False,
        must_exist=True,
    )
    if not root_decision.allowed or root_decision.resolved is None:
        return TargetDirectoryPreparation(
            str(root),
            (),
            (root_decision.reason,),
            "BLOCKED",
        )

    resolved_root = Path(root_decision.resolved)
    pending: list[Path] = [resolved_root]
    directories: list[str] = ["."]
    errors: list[str] = []

    while pending:
        directory = pending.pop()
        try:
            with os.scandir(directory) as iterator:
                entries = list(iterator)
        except OSError as exc:
            relative = (
                "."
                if directory == resolved_root
                else directory.relative_to(resolved_root).as_posix()
            )
            errors.append(f"Ordner nicht lesbar: {relative}: {exc}")
            continue

        entries.sort(key=lambda entry: (entry.name.casefold(), entry.name))
        for entry in entries:
            try:
                if entry.is_symlink() or not entry.is_dir(follow_symlinks=False):
                    continue
                path = Path(entry.path)
                decision = validate_path(
                    resolved_root,
                    path,
                    allow_symlink=False,
                    must_exist=True,
                )
                if not decision.allowed or decision.resolved is None:
                    continue
                resolved = Path(decision.resolved)
                relative = resolved.relative_to(resolved_root).as_posix()
                directories.append(relative)
                pending.append(resolved)
            except (OSError, ValueError) as exc:
                errors.append(f"Zielordner konnte nicht sicher geprüft werden: {entry.name}: {exc}")

    directories = sorted(
        set(directories),
        key=lambda value: (value != ".", value.casefold(), value),
    )
    return TargetDirectoryPreparation(
        root=str(resolved_root),
        directories=tuple(directories),
        errors=tuple(errors),
        status="PASS" if not errors else "OPEN",
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

        if target.exists():
            errors.append(f"Ziel existiert bereits: {target}")
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
