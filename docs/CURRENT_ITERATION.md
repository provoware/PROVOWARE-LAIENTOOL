# PROVOWARE – Current Iteration

## I19 – Preview-Zielwahl Decision Gate + Read-only-Lock DELTA

**Status:** 🟨 IMPLEMENTIERT / CI-ABNAHME AUSSTEHEND
**Fortschritt:** `████████░░ 80 %`

## A – FESTER PLAN: Zielwahl-Decision-Gate

**Ziel:** sichere Copy-/Move-Zielauswahl definieren, ohne Produktimplementierung und ohne Executor.

**Entscheidung:**

- erste Zielwahl nur innerhalb derselben explizit freigegebenen B01-Wurzel;
- keine zweite/externe Zielwurzel;
- kein Cross-Device-Move;
- Zielordner explizit auswählen;
- Quelle = Ziel blockieren;
- Symlinks bleiben gesperrt;
- existierendes Ziel blockiert;
- kein Overwrite;
- kein automatisches Auto-Rename;
- Preview bleibt read-only;
- I13-Recovery-Semantik bleibt verpflichtend;
- unmittelbar vor späterer Ausführung erneute Pfad-/Existenz-/Kapazitätsprüfung;
- kein I12-Schema-Reopen für den initialen Same-Root-Vertrag.

**Status:** 🟢 Entscheidung dokumentiert.

## B – DELTA: Read-only-Lock

**Quelle:** ausdrücklicher Qualitäts-/Debugging-Auftrag.

**Ziel:** solange Executor und Persistenz gesperrt sind, offensichtliche Schreib-APIs im Produktionscode automatisch blockieren.

**Abgedeckt:**

- 🟢 pathlib-Schreibmethoden
- 🟢 os-Schreiboperationen
- 🟢 shutil-Schreiboperationen
- 🟢 schreibende open()-Modi
- 🟢 Modul- und Funktions-Aliase
- 🟢 dynamische open()-Modi fail-closed
- 🟢 aktueller Produktbaum muss vollständig read-only bleiben
- 🟢 CI-Gate vor Full-Suite

## Warum Same-Root zuerst

Der bestehende I12-Vertrag besitzt genau eine root für Quelle und Ziel.

Same-Root deckt den Kernfall „Downloads in Unterordner organisieren“ ab und vermeidet aktuell Multi-Root-Schema, Cross-Device-Sonderfälle, komplexere Recovery sowie zusätzliche Kapazitäts-/Mount-Verträge.

Externe Datenträger bleiben bis zu einem späteren Multi-Root-Decision-Gate BLOCKED.

## Nicht-Ziele

- keine Copy-/Move-Implementierung;
- kein Executor;
- keine Persistenz;
- keine externe Zielwurzel;
- kein Cross-Device-Move;
- kein Overwrite;
- kein Auto-Rename;
- keine sichtbare GUI-Erweiterung;
- keine Abschwächung des Read-only-Locks.

## Exit-Gates

1. I19-Decision-Doku vollständig.
2. Read-only-Guard-Tests PASS.
3. aktueller Produktbaum Read-only-Lock PASS.
4. Core-Diagnostic PASS.
5. vollständige Suite PASS.
6. Repository-Contract PASS.
7. Info-Text-Impact PASS.
8. finaler Diff ohne Scope-Drift.
9. Post-Merge-CI PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I20 – Diagnose-/Recovery-Observability
Datensparsame Diagnoseberichte für reale Fehlerfälle planen und als read-only Exportmodell vorbereiten. Gate: Redaction, Opt-in, keine Secrets, keine automatische Reparatur.

### 2. 🔵 I21 – Same-Root Copy/Move Preview Application
Ausschließlich Preview-Erzeugung für explizit gewählte Zielordner innerhalb derselben Root. Gate: kein Executor, kein Overwrite, GUI-/CLI-Parität.

### 3. 🔵 I17-B / I18-B – reale GUI-Evidence und sichtbare Komfort-Anbindung
Sobald Zielsystemzugriff möglich ist, 100/150/200-%-/Tastatur-Evidence abschließen und dann sichtbare Suche/Sortierung anbinden.