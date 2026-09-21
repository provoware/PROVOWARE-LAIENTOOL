# PROVOWARE – Current Iteration

## I25 – Transfer-Preview Adapter

**Status:** 🟨 IMPLEMENTIERT · REAL-EVIDENCE OPEN
**Fortschritt:** `████████░░ 80 %`

## A – FESTER PLAN

I23/I18/I21 sind als gemeinsamer read-only Workflow umgesetzt:

- `files.preview_copy` und `files.preview_move` im gemeinsamen Application-Core;
- I18-Inventaransicht liefert die auswählbaren Dateien;
- I21 erzeugt ausschließlich Same-Root Copy-/Move-Preview;
- CLI besitzt nummerierte Mehrfachauswahl;
- GUI besitzt Mehrfachauswahl im expliziten I25-Prüfmodus;
- Start des Prüfmodus ausschließlich über `./start.sh --i25-evidence`;
- kein Executor, kein produktiver Datei-Write.

Die beiden Registry-Einträge bleiben absichtlich `OPEN`. I23 erlaubt `READY` erst nach realer Accessibility-/Laien-Evidence des neuen sichtbaren Workflows.

## B – DELTA AUS DEM RC-LAUF

Der erste I25-RC belegte einen Prozesskonflikt: `info_text_guard.py` lief vor den Produktgates und stoppte einen bewusst noch nicht finalisierten RC, bevor Full Suite und Safety-Gates ausgeführt wurden.

Korrektur:

- Produkt-/Safety-Gates laufen im CI zuerst;
- Info-Text-Impact bleibt hart, läuft aber als finales PR-Gate;
- fehlende Finalisierungsdoku bleibt damit merge-blockierend;
- Produktfehler können trotzdem unabhängig von Doku-Finalisierung diagnostiziert werden.

Zusätzlich wurde der spätere READY-Pfad des Zahlenmenüs explizit auf `run_transfer_preview_flow()` verdrahtet.

## Weiterhin gesperrt

- Executor;
- produktives Kopieren/Verschieben;
- Overwrite;
- Auto-Rename;
- externe Zielwurzel;
- Cross-Device Move;
- Persistenz;
- Rechteausweitung;
- READY ohne reale Folge-Evidence.

## Exit-Gates

1. Repository-Contract PASS.
2. Read-only-Lock PASS.
3. vollständige Unit-/Integrationssuite PASS.
4. Core Diagnostic PASS.
5. Diagnose/Preflight PASS.
6. Info-Text-Impact PASS.
7. finaler Diff ohne Scope-Drift.
8. reale I25-Evidence: 100/150/200 %, Tastatur/Fokus, Mehrfachauswahl, Zielwahl, Preview und Laienverständlichkeit.
9. erst danach Registry `READY`.

## Nächste drei Schritte

1. 🟨 finalen automatischen PR-Gate des I25-Branches abschließen.
2. 🔵 realen I25-Prüfmodus über `./start.sh --i25-evidence` ausführen und Ergebnis dokumentieren.
3. 🔒 nur bei realem PASS die beiden Transfer-Preview-Registry-Einträge in einem kleinen Freeze-Batch auf `READY` setzen; Executor bleibt gesperrt.
