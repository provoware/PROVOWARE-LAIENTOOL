# I15 – Read-only Dateiinventar

## Status

Read-only Inventarkern implementiert. **Keine Datei wird verändert, verschoben, kopiert, gelöscht, gehasht oder persistent gespeichert.**

## Ziel

Eine explizit ausgewählte und durch B01 validierte Wurzel rekursiv inventarisieren und dabei nur bereits vorhandene Dateifakten erfassen.

Der Inventarkern liefert die fachlichen Eingangsdaten für spätere Preview-Schritte, erzeugt in I15 aber **noch keinen `PreviewPlan`** und keinen GUI-/CLI-Use-Case.

## Datenmodell

### InventoryItem

Immutable:

- relativer Pfad innerhalb der gewählten Wurzel;
- Dateigröße in Bytes.

### InventoryIssue

Immutable:

- Befundcode;
- relativer Pfad;
- laiengerechte Meldung.

### InventoryResult

Immutable:

- validierte Wurzel;
- `root_allowed`;
- Tupel aller regulären Dateien;
- Tupel aller Befunde;
- `file_count`;
- `total_bytes`;
- `complete`.

## Sicherheitsregeln

1. Die Wurzel muss den bestehenden B01-Pfadvertrag bestehen.
2. Rekursion folgt **keinen Symlinks**.
3. Jeder gefundene Pfad wird erneut gegen B01 geprüft.
4. Nur reguläre Dateien werden als Inventarobjekte aufgenommen.
5. Spezialdateien werden übersprungen und dokumentiert.
6. Zugriffs-/Race-Fehler werden als Befund zurückgegeben statt den ganzen Lauf ungeprüft abzubrechen.
7. Unicode und Leerzeichen bleiben vollständig erhalten.
8. Ergebnisreihenfolge ist deterministisch.
9. Der Inventarkern besitzt keinen Schreibpfad.

## Befundcodes

- `root-blocked`
- `path-blocked`
- `symlink-blocked`
- `access-error`
- `special-file`

## Bedeutung von complete

`complete=True` bedeutet:

- Wurzel ist freigegeben;
- innerhalb des erlaubten normalen Dateiscope gab es keinen blockierenden Pfad-/Zugriffsfehler.

Bewusst übersprungene Symlinks machen den Lauf nicht automatisch unvollständig, weil sie laut Sicherheitsvertrag außerhalb des Inventars liegen.

## Verbindung zu I12 Preview

I15 liefert ausschließlich neutrale Fakten:

```text
root + relative_path + size_bytes
```

Erst I16 darf daraus fachliche Preview-Aktionen erstellen.

Damit bleibt die Trennung:

```text
I15 Inventory → Fakten
I16 Application → Preview-Aufbereitung
I12 Preview Model → Wirkungsvertrag
Executor → weiterhin gesperrt
```

## Nicht-Ziele

- kein Hashing;
- keine Duplikaterkennung;
- keine Dateitypklassifikation;
- keine Thumbnails;
- keine Vorschaugenerierung;
- kein `PreviewPlan`;
- keine Registry-/GUI-/CLI-Funktion;
- kein Journal;
- keine Persistenz;
- kein Executor;
- keine TOCTOU-Freigabe für spätere Schreiboperationen.

## Tests

Abgedeckt werden mindestens:

- verschachtelte Dateien;
- Unicode;
- Leerzeichen;
- unveränderte Quelldateien;
- Symlink-Sperre;
- fehlende Wurzel;
- deterministische Sortierung;
- simulierter Zugriffsfehler in einem Unterordner;
- immutable Inventarobjekte.

## Gate

```bash
PYTHONPATH=src python3 -m unittest tests.test_inventory -v
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
