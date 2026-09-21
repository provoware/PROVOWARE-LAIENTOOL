"""Read-only recursive inventory for an explicitly selected root.

I15 only observes filesystem facts. It never creates, modifies, moves, copies,
deletes, hashes, chmods or persists user data.
"""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path

from .path_policy import validate_existing_root, validate_path

ISSUE_ROOT_BLOCKED = "root-blocked"
ISSUE_PATH_BLOCKED = "path-blocked"
ISSUE_SYMLINK_BLOCKED = "symlink-blocked"
ISSUE_ACCESS_ERROR = "access-error"
ISSUE_SPECIAL_FILE = "special-file"


@dataclass(frozen=True, slots=True)
class InventoryItem:
    relative_path: str
    size_bytes: int


@dataclass(frozen=True, slots=True)
class InventoryIssue:
    code: str
    relative_path: str
    message: str


@dataclass(frozen=True, slots=True)
class InventoryResult:
    root: str
    root_allowed: bool
    items: tuple[InventoryItem, ...]
    issues: tuple[InventoryIssue, ...]

    @property
    def file_count(self) -> int:
        return len(self.items)

    @property
    def total_bytes(self) -> int:
        return sum(item.size_bytes for item in self.items)

    @property
    def complete(self) -> bool:
        blocking = {ISSUE_ROOT_BLOCKED, ISSUE_PATH_BLOCKED, ISSUE_ACCESS_ERROR}
        return self.root_allowed and not any(
            issue.code in blocking for issue in self.issues
        )


def _relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def scan_inventory(root: Path) -> InventoryResult:
    """Recursively inventory regular files without following symlinks."""
    root_decision = validate_existing_root(root)
    if not root_decision.allowed or root_decision.resolved is None:
        return InventoryResult(
            root=str(root),
            root_allowed=False,
            items=(),
            issues=(
                InventoryIssue(
                    ISSUE_ROOT_BLOCKED,
                    ".",
                    root_decision.reason,
                ),
            ),
        )

    resolved_root = Path(root_decision.resolved)
    items: list[InventoryItem] = []
    issues: list[InventoryIssue] = []
    pending: list[Path] = [resolved_root]

    while pending:
        directory = pending.pop()
        try:
            with os.scandir(directory) as iterator:
                entries = list(iterator)
        except OSError as exc:
            issues.append(
                InventoryIssue(
                    ISSUE_ACCESS_ERROR,
                    _relative(resolved_root, directory),
                    f"Ordner konnte nicht gelesen werden: {exc}",
                )
            )
            continue

        entries.sort(key=lambda entry: (entry.name.casefold(), entry.name))

        for entry in entries:
            path = Path(entry.path)
            relative = _relative(resolved_root, path)

            try:
                if entry.is_symlink():
                    issues.append(
                        InventoryIssue(
                            ISSUE_SYMLINK_BLOCKED,
                            relative,
                            "Verknüpfung (Symlink) wird nicht verfolgt.",
                        )
                    )
                    continue

                decision = validate_path(
                    resolved_root,
                    path,
                    allow_symlink=False,
                    must_exist=True,
                )
                if not decision.allowed:
                    issues.append(
                        InventoryIssue(
                            ISSUE_PATH_BLOCKED,
                            relative,
                            decision.reason,
                        )
                    )
                    continue

                if entry.is_dir(follow_symlinks=False):
                    pending.append(path)
                    continue

                info = entry.stat(follow_symlinks=False)
                if not stat.S_ISREG(info.st_mode):
                    issues.append(
                        InventoryIssue(
                            ISSUE_SPECIAL_FILE,
                            relative,
                            "Spezialdatei wird im normalen Dateiinventar übersprungen.",
                        )
                    )
                    continue

                items.append(
                    InventoryItem(
                        relative_path=relative,
                        size_bytes=info.st_size,
                    )
                )
            except OSError as exc:
                issues.append(
                    InventoryIssue(
                        ISSUE_ACCESS_ERROR,
                        relative,
                        f"Eintrag konnte nicht sicher gelesen werden: {exc}",
                    )
                )

    items.sort(key=lambda item: (item.relative_path.casefold(), item.relative_path))
    issues.sort(key=lambda issue: (
        issue.relative_path.casefold(),
        issue.relative_path,
        issue.code,
    ))

    return InventoryResult(
        root=str(resolved_root),
        root_allowed=True,
        items=tuple(items),
        issues=tuple(issues),
    )
