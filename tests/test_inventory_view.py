from __future__ import annotations

import unittest

from provoware_laientool.inventory import InventoryItem, InventoryResult
from provoware_laientool.inventory_view import (
    SORT_NAME_ASC,
    SORT_NAME_DESC,
    SORT_SIZE_ASC,
    SORT_SIZE_DESC,
    InventoryViewSpec,
    build_inventory_view,
    validate_view_spec,
)


def sample_inventory() -> InventoryResult:
    return InventoryResult(
        root="/tmp/Downloads",
        root_allowed=True,
        items=(
            InventoryItem("zeta.bin", 100),
            InventoryItem("Alpha.txt", 10),
            InventoryItem("Unter Ordner/ä Bild.png", 500),
            InventoryItem("beta.log", 100),
        ),
        issues=(),
    )


class InventoryViewTests(unittest.TestCase):
    def test_default_name_sort_is_deterministic(self) -> None:
        view = build_inventory_view(sample_inventory())
        self.assertEqual(
            [item.relative_path for item in view.items],
            ["Alpha.txt", "beta.log", "Unter Ordner/ä Bild.png", "zeta.bin"],
        )

    def test_unicode_casefold_search_is_read_only(self) -> None:
        inventory = sample_inventory()
        view = build_inventory_view(
            inventory,
            InventoryViewSpec(query="BILD", sort=SORT_NAME_ASC),
        )
        self.assertEqual(
            [item.relative_path for item in view.items],
            ["Unter Ordner/ä Bild.png"],
        )
        self.assertEqual(inventory.file_count, 4)

    def test_size_desc_tie_break_is_deterministic(self) -> None:
        view = build_inventory_view(
            sample_inventory(),
            InventoryViewSpec(sort=SORT_SIZE_DESC),
        )
        self.assertEqual(
            [(item.relative_path, item.size_bytes) for item in view.items],
            [
                ("Unter Ordner/ä Bild.png", 500),
                ("zeta.bin", 100),
                ("beta.log", 100),
                ("Alpha.txt", 10),
            ],
        )

    def test_size_asc(self) -> None:
        view = build_inventory_view(
            sample_inventory(),
            InventoryViewSpec(sort=SORT_SIZE_ASC),
        )
        self.assertEqual([item.size_bytes for item in view.items], [10, 100, 100, 500])

    def test_name_desc(self) -> None:
        view = build_inventory_view(
            sample_inventory(),
            InventoryViewSpec(sort=SORT_NAME_DESC),
        )
        self.assertEqual(view.items[0].relative_path, "zeta.bin")

    def test_limit_preserves_full_match_summary(self) -> None:
        inventory = InventoryResult(
            root="/tmp/Downloads",
            root_allowed=True,
            items=tuple(InventoryItem(f"{i:03d}.bin", i) for i in range(120)),
            issues=(),
        )
        view = build_inventory_view(
            inventory,
            InventoryViewSpec(sort=SORT_SIZE_DESC, limit=10),
        )
        self.assertEqual(len(view.items), 10)
        self.assertEqual(view.total_matched, 120)
        self.assertEqual(view.total_bytes, sum(range(120)))
        self.assertEqual(view.items[0].size_bytes, 119)

    def test_supported_limits_are_exact(self) -> None:
        for limit in (10, 50, 100, None):
            self.assertEqual(validate_view_spec(InventoryViewSpec(limit=limit)), ())
        self.assertTrue(validate_view_spec(InventoryViewSpec(limit=25)))

    def test_unknown_sort_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            build_inventory_view(
                sample_inventory(),
                InventoryViewSpec(sort="random"),
            )


if __name__ == "__main__":
    unittest.main()
