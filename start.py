#!/usr/bin/env python3
"""Minimal read-only project entry point for B01-A."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from provoware_laientool.preflight import main


if __name__ == "__main__":
    raise SystemExit(main())
