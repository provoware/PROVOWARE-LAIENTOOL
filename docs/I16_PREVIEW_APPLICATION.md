# I16 – Preview-Application-Use-Case

## Status

Read-only Application-Integration zwischen I15-Inventar und I12-Preview implementiert.

**Kein Executor, keine Persistenz und keine Dateiänderung.**

## Ziel

Eine explizit ausgewählte Wurzel soll über einen einzigen gemeinsamen Application-Pfad verarbeitet werden:

```text
GUI / CLI
   ↓
Application-Core
   ↓
I15 Inventory
   ↓
InventoryItem[]
   ↓
I12 PreviewItem / PreviewPlan
   ↓
I12 validate_preview()
   ↓
nur Darstellung
```

GUI und CLI sammeln ausschließlich den Ordnerpfad ein. Inventarisierung, Preview-Erzeugung und Sicherheitsentscheidung liegen vollständig im gemeinsamen Core.

## Warum I16 zunächst nur Trash-Preview erzeugt

I15 liefert ausschließlich neutrale Dateifakten.

Für `copy` oder `move` wäre zusätzlich eine ausdrücklich gewählte Zielstruktur notwendig. Diese Zielwahl gehört nicht in I16 und wird nicht erfunden.

Darum erzeugt I16 ausschließlich:

- `action = trash`;
- `target = None`;
- `reversible = True`;
- klaren Recovery-Hinweis;
- `writes_enabled = False`.

Das bedeutet ausdrücklich **nicht**, dass eine Trash-Operation freigegeben wäre.

## Shared Application Contract

### `prepare_trash_preview(root)`

Der gemeinsame Core:

1. ruft `scan_inventory(root)` auf;
2. blockiert eine unsichere Wurzel;
3. erzeugt bei unvollständigem Inventar **keinen** Preview-Plan;
4. erzeugt bei leerem Inventar keinen künstlichen Aktionsplan;
5. übersetzt reguläre Inventardateien deterministisch in `PreviewItem`;
6. baut über `make_plan()` den immutable `PreviewPlan`;
7. validiert den Plan erneut über `validate_preview()`;
8. gibt ausschließlich ein immutable `PreviewPreparation` zurück.

## Fail-closed Regeln

### Blockierte Wurzel

```text
Inventory root blocked
→ kein PreviewPlan
→ Status BLOCKED
```

### Unvollständiges Inventar

Beispiel: mindestens ein Unterordner konnte nicht gelesen werden.

```text
Inventory complete = False
→ kein PreviewPlan
→ Status OPEN
```

Es wird ausdrücklich **keine Teilvorschau als vollständige Aktionsgrundlage** ausgegeben.

### Preview-Validierung schlägt fehl

```text
PreviewCheck.allowed = False
→ keine Freigabe
→ Status BLOCKED
```

## Adapter-Parität

Registry-ID:

```text
files.preview_trash
```

Anzeigename:

```text
Dateivorschau
```

Verfügbar:

- GUI: ja;
- CLI: ja;
- Sicherheitsklasse: read-only;
- Status: READY.

Die Adapter dürfen nur:

- den Ordner auswählen/abfragen;
- `execute("files.preview_trash", root=...)` aufrufen;
- das gemeinsame `ActionResult` darstellen.

Nicht erlaubt in GUI/CLI:

- `scan_inventory()`;
- `PreviewItem`-Erzeugung;
- `make_plan()`;
- `validate_preview()`;
- eigene Sicherheitsentscheidungen.

## GUI

Die PySide6-Shell öffnet für diesen Use Case einen normalen Ordnerauswahldialog.

Abbruch oder leere Auswahl:

- Status OPEN;
- nichts wird gelesen;
- nichts wird verändert.

## CLI

Das Zahlenmenü enthält denselben Registry-Use-Case.

Nach Auswahl wird genau ein Ordnerpfad abgefragt und anschließend derselbe Application-Core ausgeführt.

## Ergebnisdarstellung

Bei erfolgreicher Vorschau werden unter anderem angezeigt:

- validierte Wurzel;
- Zahl regulärer Dateien;
- Gesamtgröße in Byte;
- Zahl bewusst übersprungener Hinweise;
- geplante Wirkung;
- maximal die ersten zehn Dateinamen;
- ausdrücklicher Hinweis, dass der Executor gesperrt bleibt.

## Nicht-Ziele

- keine echte Trash-Operation;
- kein Copy/Move;
- keine Zielauswahl;
- keine Bestätigung für Schreibzugriff;
- kein Journal-Write;
- kein Undo-Executor;
- keine Persistenz;
- keine automatische Ordnerwahl;
- keine Suche/Sortierung/Größenkomfortschicht;
- keine neue Fachlogik in GUI/CLI.

## Testgate

Geprüft werden mindestens:

- Inventory → reversible Trash-Preview;
- Byte-/Anzahlkonsistenz;
- Preview bleibt `writes_enabled=False`;
- erneute I12-Validierung;
- fehlende Wurzel;
- unvollständiges Inventar → kein PreviewPlan;
- fehlende explizite Root-Eingabe;
- Unicode/Leerzeichen;
- Quelldatei bleibt unverändert;
- GUI/CLI enthalten keine Inventar-/Preview-Fachlogik;
- CLI verwendet denselben Registry-/Application-Pfad.

## Sicherheitsstatus

```text
I15 Inventory          🟢 read-only
I16 Application        🟢 read-only
I12 Preview            🟢 Modell/Validierung
Executor                🔒 gesperrt
Persistenz              🔒 gesperrt
Dateiänderung           🔒 gesperrt
```
