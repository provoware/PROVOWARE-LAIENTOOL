"""Layperson-friendly numeric CLI adapter backed by the shared registry."""

from __future__ import annotations

from collections.abc import Callable

from .application_core import action_requires_root, execute
from .capability_registry import list_use_cases


def menu_entries() -> tuple[tuple[int, str, str], ...]:
    entries = [
        entry
        for entry in list_use_cases()
        if entry.cli_available and entry.status == "READY"
    ]
    return tuple(
        (number, entry.id, entry.label)
        for number, entry in enumerate(entries, start=1)
    )


def render_menu() -> str:
    lines = [
        "PROVOWARE",
        "",
        "🔒 Sicherer Lese-Modus – Es werden keine Dateien verändert.",
        "",
    ]
    lines.extend(f"{number}  {label}" for number, _, label in menu_entries())
    lines.extend(["0  Beenden", "", "Bitte Zahl eingeben:"])
    return "\n".join(lines)


def run(
    *,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> int:
    mapping = {number: use_case_id for number, use_case_id, _ in menu_entries()}

    while True:
        output_fn(render_menu())
        raw = input_fn("> ").strip()

        if raw == "0":
            output_fn("PROVOWARE wurde beendet. Es wurden keine Dateien verändert.")
            return 0

        if not raw.isdigit() or int(raw) not in mapping:
            output_fn(
                "⚠️ Diese Auswahl gibt es nicht. Bitte nur eine angezeigte Zahl eingeben."
            )
            continue

        use_case_id = mapping[int(raw)]
        root = None
        if action_requires_root(use_case_id):
            root = input_fn("Ordnerpfad für die reine Vorschau: ").strip()
        result = execute(use_case_id, root=root)
        output_fn("")
        output_fn(f"{result.title} – {result.status}")
        output_fn(result.body)
        output_fn("")
        input_fn("Enter drücken für das Hauptmenü …")


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
