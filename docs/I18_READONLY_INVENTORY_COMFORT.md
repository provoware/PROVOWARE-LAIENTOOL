# I18 – Read-only Inventar-Komfortkern

## Status

Repository-seitiger Komfortkern implementiert. Sichtbare GUI-Anbindung bleibt bis zum realen I17-Befund bewusst getrennt.

## Ziel

Auf den bereits in I15 erhobenen immutable Dateifakten sollen komfortable Ansichten entstehen, **ohne das Dateisystem erneut zu lesen oder zu verändern**.

## Funktionen

`InventoryViewSpec` unterstützt:

- Textsuche über relative Pfade;
- Sortierung Name aufsteigend;
- Sortierung Name absteigend;
- Größe aufsteigend;
- Größe absteigend;
- optional exakt 10, 50 oder 100 sichtbare Treffer.

Damit sind die geplanten Ansichten „10 / 50 / 100 größte Dateien“ fachlich vorbereitet.

## Datenfluss

```text
gewählte Wurzel
   ↓
I15 scan_inventory()
   ↓
InventoryResult
   ↓
I18 build_inventory_view()
   ↓
InventoryView
   ↓
spätere GUI/CLI-Darstellung
```

Über den gemeinsamen Application-Core:

```text
prepare_inventory_view(root, spec)
```

Damit müssen spätere Adapter keine Such-/Sortierlogik duplizieren.

## Eigenschaften

- immutable Eingaben/Ergebnisse;
- keine Dateiinhalte werden gelesen;
- kein neuer Dateisystemzugriff während Filterung/Sortierung;
- Unicode-/Casefold-Suche;
- deterministische Tie-Breaks;
- Summary bleibt vollständig, auch wenn nur Top 10/50/100 angezeigt werden;
- unbekannte Sortierung oder ungültiges Limit fail-closed.

## Sichtbare UI

Noch nicht freigegeben.

Grund: I17 reale 100/150/200-%-/Tastatur-/Laien-Evidence ist weiterhin OPEN.

Der nichtvisuelle I18-Kern kann trotzdem sicher eingefroren werden, damit die spätere GUI ausschließlich Darstellung und Eingabesammlung übernimmt.

## Professioneller Core-Diagnoselauf

```bash
python3 scripts/core_diagnostics.py
python3 scripts/core_diagnostics.py --json
```

Der Lauf erstellt ausschließlich einen temporären Dateibaum und prüft end-to-end:

1. Inventar;
2. externe Symlink-Sperre;
3. größte-Dateien-Ansicht;
4. gemeinsamer I18-Application-Pfad;
5. reversible I16-Preview;
6. I12-Validierung;
7. unveränderte Quelldateien.

Keine realen Nutzdateien werden benötigt.

## Nicht-Ziele

- keine sichtbare GUI-Erweiterung vor I17;
- keine neue CLI-Fachfunktion vor GUI-/CLI-Paritätsplanung;
- keine Dateiänderung;
- kein Hashing;
- keine Duplikaterkennung;
- keine Persistenz;
- kein Executor;
- keine Copy-/Move-Zielwahl.

## Gate

- `tests/test_inventory_view.py`;
- `tests/test_core_diagnostics.py`;
- vollständige Suite;
- `scripts/core_diagnostics.py`;
- Repository-/Info-Text-Gates;
- Post-Merge-CI.
