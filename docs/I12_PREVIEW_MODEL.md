# I12 – B05 Immutable Preview-Modell

## Ziel

I12 definiert ausschließlich, **was eine spätere Dateiaktion bewirken würde**. Es gibt keinen Executor und keinen freigegebenen Schreibpfad.

Das Preview-Modell muss vor späteren Schreiboperationen mindestens zeigen:

- Quelle;
- Ziel, falls fachlich erforderlich;
- Aktionsart;
- verständliche Wirkung;
- geschätzten Umfang in Bytes;
- Reversibilität;
- Rückweg/Recovery-Hinweis;
- verifizierte Pfadgrenzen;
- Gesamtanzahl und geschätzten Gesamtumfang.

## Unterstützte Plan-Aktionen

I12 modelliert bewusst nur:

- `copy`
- `move`
- `trash`

Eine irreversible Direktlöschung wird in I12 **nicht** freigegeben oder modelliert.

## Immutable Vertrag

`PreviewItem`, `PreviewPlan` und `PreviewCheck` sind unveränderlich.

Ein Plan besitzt zusätzlich fest:

`writes_enabled = False`

Damit kann ein Preview-Objekt nicht gleichzeitig eine Ausführungsfreigabe darstellen.

## Sicherheitsprüfung

`validate_preview(plan)` verwendet den bestehenden B01-Pfadvertrag.

### Quelle

- muss existieren;
- muss innerhalb der freigegebenen Wurzel liegen;
- Symlinks bleiben standardmäßig gesperrt.

### Ziel bei Copy/Move

- muss angegeben sein;
- darf noch fehlen, weil es sich nur um Planung handelt;
- muss dennoch sicher innerhalb der freigegebenen Wurzel auflösbar sein;
- darf nicht identisch mit der Quelle sein.

### Trash

- besitzt in I12 kein frei wählbares Ziel;
- muss als reversibel markiert sein.

## Fail-closed

Der Preview-Vertrag blockiert unter anderem:

- unbekannte Aktion;
- doppelte oder leere ID;
- fehlendes Ziel bei Copy/Move;
- Außenpfade/Traversal;
- fehlende Quelle;
- negative Größenwerte;
- fehlende Wirkungserklärung;
- fehlenden Rückweg;
- inkonsistente Summen;
- `writes_enabled=True`;
- nicht reversiblen Trash.

## Architekturgrenze

```text
Dateiinventar (später)
        ↓
   PreviewItem(s)
        ↓
    PreviewPlan
        ↓
 validate_preview()
        ↓
 PASS / BLOCKED

KEIN Pfeil zu einem Executor in I12.
```

## Nicht-Ziele

- kein Dateiscan;
- kein Klassifizieren realer Downloads;
- kein Kopieren;
- kein Verschieben;
- kein Löschen;
- kein Papierkorb-Executor;
- kein Journal;
- kein Undo;
- keine GUI-/CLI-Erweiterung;
- kein TOCTOU-Versprechen.

## Bezug

- REQ-001
- REQ-005
- AQ-001
- AQ-003
- AQ-004
- B01 Pfad-/Symlink-Vertrag

## Gate

```bash
PYTHONPATH=src python3 -m unittest tests.test_preview_model -v
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
