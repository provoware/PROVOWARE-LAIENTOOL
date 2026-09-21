#!/usr/bin/env python3
"""PROVOWARE read-only starter.

Default keeps the original B01 preflight behavior.
Optional I11 adapters:
- --menu: novice numeric CLI shell
- --gui: optional PySide6 shell
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if args == ["--menu"]:
        from provoware_laientool.cli_shell import main as cli_main
        return cli_main()

    if args == ["--gui"]:
        from provoware_laientool.gui_shell import main as gui_main
        return gui_main()

    if args == ["--gui-i25-evidence"]:
        from provoware_laientool.gui_shell import create_main_window
        app, window = create_main_window(evidence_mode=True)
        window.show()
        return app.exec()

    if args in ([], ["--json"]):
        from provoware_laientool.preflight import main as preflight_main
        return preflight_main(args)

    print(
        "Unbekannte Option. Erlaubt: --json, --menu, --gui, --gui-i25-evidence",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
