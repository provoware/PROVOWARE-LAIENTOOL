# I21 – Same-Root Copy/Move Preview Application

## Status

Core-only Preview-Erzeugung implementiert.

**Kein Executor. Keine Persistenz. Keine sichtbare GUI-/CLI-Freigabe.**

## Ziel

Den in I19 eingefrorenen ersten Zielwahlvertrag technisch als gemeinsame Application-Funktion umsetzen:

```text
validierte root
    ↓
aktuelles I15-Inventar
    ↓
explizite Auswahl relativer Dateien
    ↓
explizit vorhandener Zielordner innerhalb derselben root
    ↓
Copy- oder Move-PreviewItem
    ↓
I12 make_plan()
    ↓
I12 validate_preview()
    ↓
🔒 STOP
```

## Gemeinsame Funktionen

```text
prepare_copy_preview(root, selected_relative_paths, target_dir)
prepare_move_preview(root, selected_relative_paths, target_dir)
```

Beide verwenden intern denselben privaten Same-Root-Builder.

## Harte Sicherheitsgrenzen

### Root

- Quelle und Ziel liegen unter derselben B01-validierten Root.
- externe Zielordner werden BLOCKED.
- Symlink-Zielordner werden BLOCKED.

### Zielordner

- muss explizit angegeben werden;
- muss bereits existieren;
- muss ein Ordner sein;
- darf nicht automatisch erzeugt werden.

### Auswahl

- muss aus dem aktuellen vollständigen Inventar stammen;
- leere Auswahl bleibt OPEN;
- doppelte Auswahl wird BLOCKED;
- unbekannte/nicht inventarisierte Auswahl wird BLOCKED.

### Zielpfad

```text
target = target_dir / source.name
```

Kein:

- Auto-Rename;
- Suffix `(1)`;
- Overwrite;
- Merge;
- automatische Konfliktentscheidung.

Existiert der Zielpfad bereits, wird die gesamte Preview BLOCKED.

### Quelle = Ziel

Wird BLOCKED, auch wenn Quelle und Ziel nur nach Pfadauflösung identisch werden.

## Preview-Vertrag

Copy:

- `action=copy`
- `reversible=True`
- Recovery-Hinweis: später erzeugte Kopie eindeutig entfernbar.

Move:

- `action=move`
- `reversible=True`
- Recovery-Hinweis: später an Ursprungsort zurückverschiebbar.

Beide:

- `writes_enabled=False`
- I12 `validate_preview()` muss PASS liefern.

## Fail-closed Verhalten

Kein PreviewPlan bei:

- blockierter Root;
- unvollständigem Inventar;
- fehlender Auswahl;
- Zielordner außerhalb Root;
- Symlink-Ziel;
- fehlendem Zielordner;
- Ziel ist Datei;
- unbekannter Auswahl;
- doppelter Auswahl;
- bestehendem Ziel;
- identischer Quelle/Ziel;
- I12-Validierungsfehler.

## Keine Adapterfreigabe

I21 registriert **keinen** neuen sichtbaren Use Case.

Begründung:

- realer I17-Accessibility-Lauf bleibt OPEN;
- Copy/Move benötigen später eine laiengerechte Auswahl-/Zieloberfläche;
- Fachkern und Sicherheitsvertrag können unabhängig davon jetzt vollständig getestet werden.

## Debugging-/Regressionsevidence

Unit-Tests prüfen:

- Copy PASS;
- Move PASS;
- kein Schreiben;
- Overwrite BLOCKED;
- externes Ziel BLOCKED;
- Symlink-Ziel BLOCKED;
- fehlender/ungültiger Zielordner BLOCKED;
- Quelle=Ziel BLOCKED;
- unbekannte Auswahl BLOCKED;
- doppelte Auswahl BLOCKED;
- leere Auswahl OPEN;
- fehlende Root BLOCKED;
- deterministische Mehrfachauswahl.

`scripts/core_diagnostics.py` prüft zusätzlich in einem ausschließlich temporären Dateisystem:

- Same-Root Copy Preview;
- Same-Root Move Preview;
- Overwrite-Sperre;
- unveränderte Quelldateien.

## Weiter gesperrt

- Executor;
- Copy/Move-Ausführung;
- Overwrite;
- Auto-Rename;
- externe Zielwurzel;
- Cross-Device Move;
- Persistenz;
- Journal-Writer;
- TOCTOU-Freigabe;
- automatische Rechteausweitung;
- sichtbare GUI-/CLI-Anbindung.
