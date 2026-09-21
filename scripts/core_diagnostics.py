#!/usr/bin/env python3
"""Dependency-free professional core diagnostic smoke for CI and debugging.

Uses only a temporary filesystem created by the script. No user files are read
or modified.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from provoware_laientool.application_core import (  # noqa: E402
    prepare_copy_preview,
    prepare_inventory_view,
    prepare_move_preview,
    prepare_trash_preview,
)
from provoware_laientool.inventory import scan_inventory  # noqa: E402
from provoware_laientool.inventory_view import (  # noqa: E402
    SORT_SIZE_DESC,
    InventoryViewSpec,
)


def run_diagnostic() -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append(
            {
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "detail": detail,
            }
        )

    with tempfile.TemporaryDirectory(prefix="provoware-diag-") as temp:
        base = Path(temp)
        root = base / "Downloads"
        nested = root / "Unter Ordner"
        nested.mkdir(parents=True)

        first = root / "alpha.txt"
        second = nested / "ä Bild mit Leerzeichen.png"
        first.write_bytes(b"abc")
        second.write_bytes(b"1234567890")

        outside = base / "outside.txt"
        outside.write_bytes(b"secret")
        symlink = root / "outside-link"
        symlink.symlink_to(outside)

        inventory = scan_inventory(root)
        record(
            "inventory-complete",
            inventory.complete,
            f"files={inventory.file_count}; issues={len(inventory.issues)}",
        )
        record(
            "symlink-not-followed",
            inventory.file_count == 2
            and any(issue.code == "symlink-blocked" for issue in inventory.issues),
            "external symlink must be reported but not inventoried",
        )

        view_preparation = prepare_inventory_view(
            root,
            InventoryViewSpec(sort=SORT_SIZE_DESC, limit=10),
        )
        view = view_preparation.view
        record(
            "largest-first",
            view_preparation.status == "PASS"
            and view is not None
            and bool(view.items)
            and view.items[0].relative_path == "Unter Ordner/ä Bild mit Leerzeichen.png"
            and view.items[0].size_bytes == 10,
            f"status={view_preparation.status}; "
            f"first={view.items[0].relative_path if view and view.items else 'none'}",
        )

        preview = prepare_trash_preview(root)
        record(
            "preview-read-only",
            preview.status == "PASS"
            and preview.plan is not None
            and not preview.plan.writes_enabled
            and preview.check is not None
            and preview.check.allowed,
            f"status={preview.status}",
        )

        target_dir = root / "Ziel"
        target_dir.mkdir()
        copy_preview = prepare_copy_preview(
            root,
            ("alpha.txt",),
            target_dir,
        )
        move_preview = prepare_move_preview(
            root,
            ("Unter Ordner/ä Bild mit Leerzeichen.png",),
            target_dir,
        )
        record(
            "same-root-copy-preview",
            copy_preview.status == "PASS"
            and copy_preview.plan is not None
            and copy_preview.check is not None
            and copy_preview.check.allowed
            and not copy_preview.plan.writes_enabled
            and not (target_dir / "alpha.txt").exists(),
            f"status={copy_preview.status}",
        )
        record(
            "same-root-move-preview",
            move_preview.status == "PASS"
            and move_preview.plan is not None
            and move_preview.check is not None
            and move_preview.check.allowed
            and not move_preview.plan.writes_enabled
            and not (target_dir / "ä Bild mit Leerzeichen.png").exists(),
            f"status={move_preview.status}",
        )

        collision = target_dir / "alpha.txt"
        collision.write_bytes(b"existing")
        blocked_copy = prepare_copy_preview(
            root,
            ("alpha.txt",),
            target_dir,
        )
        record(
            "overwrite-blocked",
            blocked_copy.status == "BLOCKED"
            and blocked_copy.plan is None
            and collision.read_bytes() == b"existing",
            f"status={blocked_copy.status}",
        )

        record(
            "sources-unchanged",
            first.read_bytes() == b"abc"
            and second.read_bytes() == b"1234567890"
            and outside.read_bytes() == b"secret",
            "temporary sources remain byte-identical",
        )

    failures = [item for item in checks if item["status"] == "FAIL"]
    return {
        "diagnostic": "PROVOWARE core diagnostic",
        "mode": "temporary-filesystem-only",
        "status": "FAIL" if failures else "PASS",
        "checks": checks,
        "failure_count": len(failures),
    }


def format_text(report: dict[str, object]) -> str:
    lines = [
        "PROVOWARE – Core Diagnostic",
        "===========================",
        f"Status: {report['status']}",
        f"Fehler: {report['failure_count']}",
        "",
    ]
    for item in report["checks"]:
        lines.append(f"{item['status']} {item['name']}: {item['detail']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = run_diagnostic()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_text(report))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
