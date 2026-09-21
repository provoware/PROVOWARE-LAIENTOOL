"""Fail-closed path and symlink boundary policy for B01-B.

This module performs read-only validation only. It does not create, move,
delete, chmod, mount or otherwise mutate filesystem objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PathDecision:
    allowed: bool
    reason: str
    requested: str
    resolved: str | None


def _resolve_existing_or_parent(path: Path) -> tuple[Path, bool]:
    """Resolve as much of a path as safely possible without creating it."""
    try:
        return path.resolve(strict=True), True
    except FileNotFoundError:
        parent = path.parent.resolve(strict=True)
        return parent / path.name, False


def validate_path(
    root: Path,
    candidate: Path,
    *,
    allow_symlink: bool = False,
    must_exist: bool = True,
) -> PathDecision:
    """Validate candidate against an explicit trusted root."""
    try:
        resolved_root = root.resolve(strict=True)
    except (FileNotFoundError, OSError, RuntimeError) as exc:
        return PathDecision(
            False,
            f"Freigegebene Wurzel ist nicht sicher auflösbar: {exc}",
            str(candidate),
            None,
        )

    try:
        absolute_candidate = candidate if candidate.is_absolute() else resolved_root / candidate
        resolved_candidate, exists = _resolve_existing_or_parent(absolute_candidate)
    except (FileNotFoundError, OSError, RuntimeError) as exc:
        return PathDecision(False, f"Pfad ist nicht sicher auflösbar: {exc}", str(candidate), None)

    if must_exist and not exists:
        return PathDecision(False, "Pfad existiert nicht.", str(candidate), str(resolved_candidate))

    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError:
        return PathDecision(
            False,
            "Pfad liegt außerhalb der freigegebenen Wurzel.",
            str(candidate),
            str(resolved_candidate),
        )

    if not allow_symlink:
        current = absolute_candidate
        while True:
            try:
                if current.is_symlink():
                    return PathDecision(
                        False,
                        "Symlinks sind für diesen Zugriff nicht freigegeben.",
                        str(candidate),
                        str(resolved_candidate),
                    )
            except OSError as exc:
                return PathDecision(False, f"Symlink-Prüfung fehlgeschlagen: {exc}", str(candidate), None)

            if current == resolved_root or current.parent == current:
                break
            current = current.parent

    return PathDecision(
        True,
        "Pfad liegt innerhalb der freigegebenen Wurzel.",
        str(candidate),
        str(resolved_candidate),
    )


def validate_existing_root(root: Path) -> PathDecision:
    """Validate that an explicitly selected root exists and resolves safely."""
    return validate_path(root, root, allow_symlink=False, must_exist=True)
