# I13 – B06 Recovery-/Journal-Zustandsvertrag

## Status

Reiner Domain-Vertrag. **Keine Persistenz, kein Journal-Writer, kein Undo-Executor und keine Dateioperation.**

## Ziel

Bevor produktive Schreibpfade entstehen, muss eindeutig feststehen:

- welcher Zustand vor einer Aktion dokumentiert wird;
- wann eine Wirkung als ausgeführt gilt;
- wie ein Undo angefordert wird;
- wie Recovery beginnt und endet;
- was nach einem Crash angenommen werden darf;
- welche Übergänge ausdrücklich verboten sind.

## Zustände

```text
prepared
   ↓
applying
   ↓
applied
   ↓
undo-requested
   ↓
recovering
   ↓
recovered
```

Fehler-/Crash-Pfade:

- `applying → interrupted | failed`
- `recovering → interrupted | failed`
- `interrupted → recovering | failed`

Direkte Sprünge wie `prepared → applied` oder `applied → recovered` sind gesperrt.

## Immutable Modelle

### RecoveryContract

Bindet eine spätere Aktion an:

- Preview-Aktions-ID;
- Operation;
- erwartete Reversibilität;
- Undo-Strategie;
- verpflichtende Journal-Nutzung.

### JournalSnapshot

Beschreibt nur einen Zustand:

- Journal-ID;
- Preview-Plan-ID;
- Preview-Aktions-ID;
- Zustand;
- Versuchszähler;
- letzter Fehler, falls vorhanden.

I13 speichert diesen Snapshot **nirgendwo**.

## Undo-Strategien

Nur als Fachvertrag definiert:

- `remove-created-copy`
- `move-back`
- `restore-from-trash`

Es gibt noch keine Implementierung dieser Strategien.

## Crash-Matrix

Grundregel:

**Kein Zustand erlaubt automatische Wiederholung.**

Besonders wichtig:

- Crash in `applying` → Wirkung unbekannt → Ist-Zustand prüfen, niemals blind wiederholen.
- Crash in `recovering` → Recovery-Wirkung unbekannt → Zustand prüfen, niemals blind fortsetzen.
- `failed` → einfrieren und Fehler dokumentieren.
- `recovered` → nichts automatisch erneut ausführen.

## Fail-closed Regeln

Der Vertrag lehnt unter anderem ab:

- fehlende Preview-Aktions-ID;
- nicht reversible Recovery-Verträge;
- unbekannte Undo-Strategie;
- deaktivierte Journal-Pflicht;
- unbekannte Zustände;
- Versuchszähler < 1;
- `FAILED` ohne Fehlergrund;
- nicht erlaubte Zustandsübergänge.

## Architekturgrenze

```text
I12 Preview
    ↓
I13 Recovery Contract
    ↓
später: Journal Persistenz
    ↓
später: Executor

I13 selbst endet VOR Persistenz und VOR Executor.
```

## Nicht-Ziele

- keine Dateioperation;
- keine SQLite-/JSON-/Log-Persistenz;
- kein Journal-Writer;
- kein Undo;
- kein Restore;
- kein Crash-Hook;
- kein Retry-System;
- keine GUI-/CLI-Erweiterung;
- keine TOCTOU-Freigabe.

## Gate

```bash
PYTHONPATH=src python3 -m unittest tests.test_recovery_contract -v
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
