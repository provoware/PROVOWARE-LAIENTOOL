"""Pure read-only inventory views for I18 comfort features."""

from __future__ import annotations

from dataclasses import dataclass

from .inventory import InventoryItem, InventoryResult

SORT_NAME_ASC = "name-asc"
SORT_NAME_DESC = "name-desc"
SORT_SIZE_ASC = "size-asc"
SORT_SIZE_DESC = "size-desc"
VALID_SORTS = {
    SORT_NAME_ASC,
    SORT_NAME_DESC,
    SORT_SIZE_ASC,
    SORT_SIZE_DESC,
}
VALID_LIMITS = {10, 50, 100}


@dataclass(frozen=True, slots=True)
class InventoryViewSpec:
    query: str = ""
    sort: str = SORT_NAME_ASC
    limit: int | None = None


@dataclass(frozen=True, slots=True)
class InventoryView:
    items: tuple[InventoryItem, ...]
    total_matched: int
    total_bytes: int
    query: str
    sort: str
    limit: int | None


def validate_view_spec(spec: InventoryViewSpec) -> tuple[str, ...]:
    errors: list[str] = []
    if spec.sort not in VALID_SORTS:
        errors.append(f"Unbekannte Sortierung: {spec.sort}")
    if spec.limit is not None and spec.limit not in VALID_LIMITS:
        errors.append("Limit muss 10, 50, 100 oder leer sein.")
    return tuple(errors)


def _name_key(item: InventoryItem) -> tuple[str, str]:
    return (item.relative_path.casefold(), item.relative_path)


def _size_key(item: InventoryItem) -> tuple[int, str, str]:
    return (item.size_bytes, item.relative_path.casefold(), item.relative_path)


def build_inventory_view(
    inventory: InventoryResult,
    spec: InventoryViewSpec = InventoryViewSpec(),
) -> InventoryView:
    """Filter/sort immutable inventory facts without touching the filesystem."""
    errors = validate_view_spec(spec)
    if errors:
        raise ValueError("; ".join(errors))

    query = spec.query.strip()
    folded = query.casefold()
    matched = [
        item
        for item in inventory.items
        if not folded or folded in item.relative_path.casefold()
    ]

    if spec.sort == SORT_NAME_ASC:
        matched.sort(key=_name_key)
    elif spec.sort == SORT_NAME_DESC:
        matched.sort(key=_name_key, reverse=True)
    elif spec.sort == SORT_SIZE_ASC:
        matched.sort(key=_size_key)
    elif spec.sort == SORT_SIZE_DESC:
        matched.sort(key=_size_key, reverse=True)

    total_matched = len(matched)
    total_bytes = sum(item.size_bytes for item in matched)
    visible = matched[: spec.limit] if spec.limit is not None else matched

    return InventoryView(
        items=tuple(visible),
        total_matched=total_matched,
        total_bytes=total_bytes,
        query=query,
        sort=spec.sort,
        limit=spec.limit,
    )
