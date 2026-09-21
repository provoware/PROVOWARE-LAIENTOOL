"""Layperson-friendly numeric CLI adapter backed by the shared registry."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from .application_core import (
    TRANSFER_PREVIEW_IDS,
    action_requires_root,
    execute,
    prepare_inventory_view,
    prepare_target_directories,
)
from .capability_registry import list_use_cases
from .inventory_view import InventoryViewSpec, SORT_NAME_ASC


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
        if use_case_id in TRANSFER_PREVIEW_IDS:
            output_fn("")
            run_transfer_preview_flow(
                use_case_id,
                input_fn=input_fn,
                output_fn=output_fn,
            )
            output_fn("")
            input_fn("Enter drücken für das Hauptmenü …")
            continue

        root = None
        if action_requires_root(use_case_id):
            root = input_fn("Ordnerpfad für die reine Vorschau: ").strip()
        result = execute(use_case_id, root=root)
        output_fn("")
        output_fn(f"{result.title} – {result.status}")
        output_fn(result.body)
        output_fn("")
        input_fn("Enter drücken für das Hauptmenü …")


def run_transfer_preview_flow(
    use_case_id: str,
    *,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> str:
    """Run the I25 numeric preview flow without enabling any writer."""
    if use_case_id not in TRANSFER_PREVIEW_IDS:
        raise ValueError(f"Keine Transfer-Vorschau: {use_case_id}")

    root_text = input_fn("1/4 Ordnerpfad wählen (0 = Zurück): ").strip()
    if root_text == "0" or not root_text:
        output_fn("Zurück. Es wurden keine Dateien verändert.")
        return "OPEN"

    preparation = prepare_inventory_view(
        Path(root_text),
        InventoryViewSpec(sort=SORT_NAME_ASC, limit=100),
    )
    if preparation.status != "PASS" or preparation.view is None:
        output_fn(
            "Der Ordner konnte nicht sicher als vollständige Dateiansicht vorbereitet werden."
        )
        return preparation.status

    items = preparation.view.items
    if not items:
        output_fn("Der Ordner enthält keine auswählbaren regulären Dateien.")
        return "OPEN"

    output_fn("2/4 Dateien auswählen:")
    for number, item in enumerate(items, start=1):
        output_fn(f"{number}  {item.relative_path}  ({item.size_bytes} Byte)")
    if preparation.view.total_matched > len(items):
        output_fn(
            f"Es werden die ersten {len(items)} von {preparation.view.total_matched} Treffern gezeigt."
        )
    output_fn("a  Alle sichtbaren auswählen")
    output_fn("0  Zurück")

    raw_selection = input_fn("Nummern mit Leerzeichen/Komma: ").strip().lower()
    if raw_selection == "0" or not raw_selection:
        output_fn("Zurück. Es wurden keine Dateien verändert.")
        return "OPEN"

    if raw_selection == "a":
        selected = tuple(item.relative_path for item in items)
    else:
        tokens = [token for token in raw_selection.replace(",", " ").split() if token]
        if not tokens or any(not token.isdigit() for token in tokens):
            output_fn("⚠️ Bitte nur angezeigte Nummern verwenden.")
            return "OPEN"
        numbers = [int(token) for token in tokens]
        if any(number < 1 or number > len(items) for number in numbers):
            output_fn("⚠️ Mindestens eine Nummer liegt außerhalb der angezeigten Liste.")
            return "OPEN"
        selected = tuple(items[number - 1].relative_path for number in numbers)

    output_fn(
        "3/4 Aktion: "
        + ("Kopieren – nur Vorschau" if use_case_id.endswith("copy") else "Verschieben – nur Vorschau")
    )

    targets = prepare_target_directories(Path(root_text))
    if targets.status != "PASS":
        output_fn("Die Zielordner konnten nicht vollständig und sicher vorbereitet werden.")
        return targets.status
    output_fn("4/4 Zielordner wählen:")
    for number, relative in enumerate(targets.directories, start=1):
        label = "/ (gewählte Wurzel)" if relative == "." else relative
        output_fn(f"{number}  {label}")
    output_fn("0  Zurück")
    raw_target = input_fn("Zielnummer: ").strip()
    if raw_target == "0" or not raw_target:
        output_fn("Zurück. Es wurden keine Dateien verändert.")
        return "OPEN"
    if not raw_target.isdigit():
        output_fn("⚠️ Bitte nur eine angezeigte Zielnummer verwenden.")
        return "OPEN"
    target_number = int(raw_target)
    if target_number < 1 or target_number > len(targets.directories):
        output_fn("⚠️ Diese Zielnummer gibt es nicht.")
        return "OPEN"
    target_relative = targets.directories[target_number - 1]
    target = Path(targets.root) if target_relative == "." else Path(targets.root) / target_relative

    result = execute(
        use_case_id,
        root=root_text,
        selected_relative_paths=selected,
        target_dir=str(target),
    )
    output_fn(f"{result.title} – {result.status}")
    output_fn(result.body)
    return result.status


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
