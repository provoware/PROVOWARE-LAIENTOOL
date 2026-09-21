"""Immutable B05 preview model for future file operations.

This module describes and validates planned effects only.
It never copies, moves, deletes, trashes, creates, chmods, mounts or otherwise
mutates filesystem objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .path_policy import PathDecision, validate_path

ACTION_COPY = "copy"
ACTION_MOVE = "move"
ACTION_TRASH = "trash"
VALID_ACTIONS = {ACTION_COPY, ACTION_MOVE, ACTION_TRASH}


@dataclass(frozen=True, slots=True)
class PreviewItem:
    id: str
    action: str
    source: str
    target: str | None
    bytes_estimate: int
    effect: str
    reversible: bool
    recovery_hint: str


@dataclass(frozen=True, slots=True)
class PreviewPlan:
    root: str
    items: tuple[PreviewItem, ...]
    total_items: int
    total_bytes_estimate: int
    writes_enabled: bool = False


@dataclass(frozen=True, slots=True)
class PreviewCheck:
    allowed: bool
    errors: tuple[str, ...]
    source_decisions: tuple[PathDecision, ...]
    target_decisions: tuple[PathDecision | None, ...]


def make_plan(root: Path, items: tuple[PreviewItem, ...]) -> PreviewPlan:
    """Create immutable summary metadata without executing any action."""
    return PreviewPlan(
        root=str(root),
        items=items,
        total_items=len(items),
        total_bytes_estimate=sum(item.bytes_estimate for item in items),
        writes_enabled=False,
    )


def validate_preview(plan: PreviewPlan) -> PreviewCheck:
    """Validate a preview fail-closed against the B01 path policy."""
    errors: list[str] = []
    source_decisions: list[PathDecision] = []
    target_decisions: list[PathDecision | None] = []
    seen_ids: set[str] = set()

    root = Path(plan.root)

    if plan.writes_enabled:
        errors.append("Preview darf keine Schreibfreigabe enthalten.")

    if plan.total_items != len(plan.items):
        errors.append("Preview-Anzahl stimmt nicht mit den Einträgen überein.")

    expected_bytes = sum(item.bytes_estimate for item in plan.items)
    if plan.total_bytes_estimate != expected_bytes:
        errors.append("Preview-Gesamtgröße stimmt nicht mit den Einträgen überein.")

    for item in plan.items:
        if not item.id.strip():
            errors.append("Preview-Eintrag ohne stabile ID.")
        elif item.id in seen_ids:
            errors.append(f"Doppelte Preview-ID: {item.id}")
        seen_ids.add(item.id)

        if item.action not in VALID_ACTIONS:
            errors.append(f"Unbekannte Preview-Aktion bei {item.id}: {item.action}")

        if item.bytes_estimate < 0:
            errors.append(f"Negative Größenangabe bei {item.id}.")

        if not item.effect.strip():
            errors.append(f"Fehlende Wirkungserklärung bei {item.id}.")

        if not item.recovery_hint.strip():
            errors.append(f"Fehlender Rückweg bei {item.id}.")

        source = validate_path(root, Path(item.source), must_exist=True)
        source_decisions.append(source)
        if not source.allowed:
            errors.append(f"Quelle blockiert bei {item.id}: {source.reason}")

        target_decision: PathDecision | None = None
        if item.action in {ACTION_COPY, ACTION_MOVE}:
            if not item.target:
                errors.append(f"Ziel fehlt bei {item.id}.")
            else:
                target_decision = validate_path(
                    root,
                    Path(item.target),
                    must_exist=False,
                )
                if not target_decision.allowed:
                    errors.append(f"Ziel blockiert bei {item.id}: {target_decision.reason}")
                elif source.resolved == target_decision.resolved:
                    errors.append(f"Quelle und Ziel sind identisch bei {item.id}.")
        elif item.target is not None:
            errors.append(f"Trash-Aktion darf kein freies Ziel enthalten: {item.id}")

        target_decisions.append(target_decision)

        if item.action in {ACTION_MOVE, ACTION_TRASH} and not item.reversible:
            label = "Move" if item.action == ACTION_MOVE else "Trash"
            errors.append(f"{label} muss als reversibel markiert sein: {item.id}")

    return PreviewCheck(
        allowed=not errors,
        errors=tuple(errors),
        source_decisions=tuple(source_decisions),
        target_decisions=tuple(target_decisions),
    )
