#!/usr/bin/env python3
"""Print a redacted, read-only PROVOWARE diagnostic snapshot."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from provoware_laientool.diagnostics import (  # noqa: E402
    build_diagnostic_report,
    diagnostic_to_json,
    format_diagnostic_text,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = build_diagnostic_report(home=Path.home())
    if args.json:
        print(diagnostic_to_json(report))
    else:
        print(format_diagnostic_text(report))
    return 0 if report.collection_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
