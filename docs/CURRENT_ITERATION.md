# PROVOWARE – Current Iteration

## I20 – Diagnose-/Recovery-Observability

**Status:** 🟢 REPOSITORY-ANTEIL ABGESCHLOSSEN
**Fortschritt:** `█████████░ 90 %`

## A – FESTER PLAN

**Ziel:** datensparsame, read-only Diagnoseberichte für reale Fehlerfälle bereitstellen, ohne Datei-Export, Persistenz, Netzwerk oder automatische Reparatur.

**Checkpoints:**

- 🟢 immutable DiagnosticEntry / DiagnosticReport
- 🟢 Collection-Status getrennt von Health-Status
- 🟢 Plattform-/Capability-Fakten aus bestehendem Preflight
- 🟢 optionaler Recovery-Snapshot ohne Recovery-IDs
- 🟢 Crash-Guidance und Auto-Retry-Status sichtbar
- 🟢 Home-Pfade redigiert
- 🟢 E-Mail-Adressen redigiert
- 🟢 typische GitHub/OpenAI/Bearer-Tokens redigiert
- 🟢 write_paths_enabled=False
- 🟢 Klartext-Ausgabe in-memory
- 🟢 JSON-Ausgabe in-memory
- 🟢 stdout-only diagnostic_snapshot.py
- 🟢 CLI-only Registry-Use-Case diagnostics.snapshot
- 🟢 gemeinsamer Application-Core
- 🟢 keine GUI-Erweiterung
- 🟢 CI-Snapshot-Gate
- 🔵 Repository-/PR-CI
- 🔵 finaler Diff / Merge / Post-Merge

## B – VARIABLE FOLGEAUFGABE

Der I19-Post-Merge-Status war repository-seitig grün und wird in I20 als bestätigte Basis übernommen. Kein zusätzlicher Produkt-DELTA erforderlich.

## Datenschutzgrenze

Der Bericht enthält keine Recovery-IDs und schreibt keine Diagnose-Datei. Redaction erfolgt vor Ausgabe. Netzwerk, Upload, Telemetrie und automatische Reparatur bleiben gesperrt.

## Direkter Diagnoseweg

`python3 scripts/diagnostic_snapshot.py`
`python3 scripts/diagnostic_snapshot.py --json`

## CLI-only Ausnahme

`diagnostics.snapshot` ist absichtlich nur im Zahlenmenü verfügbar. Das entspricht dem bestehenden Paritätsvertrag für rein diagnostische CLI-Funktionen und erzeugt keine neue sichtbare GUI-Fachfläche vor Abschluss der realen I17-Evidence.

## Nicht-Ziele

- kein Datei-Export;
- keine Diagnose-Persistenz;
- kein Upload/Netzwerk;
- kein Crash-Reporter;
- keine Telemetrie;
- keine automatische Reparatur;
- keine Journal-Persistenz;
- keine GUI-Erweiterung;
- kein Executor;
- keine Freigabe schreibender Pfade.

## Exit-Gates

1. Diagnose-/Redaction-Tests PASS.
2. Registry-/CLI-only-Vertrag PASS.
3. stdout-JSON parsebar.
4. Read-only-Lock PASS.
5. Core-Diagnostic PASS.
6. vollständige Suite PASS.
7. Repository-Contract PASS.
8. Info-Text-Impact PASS.
9. finaler Diff ohne Scope-Drift.
10. Post-Merge-CI PASS.

**Repository-/PR-CI:** 🟢 PASS
**Finaler Diff:** 🟢 ohne Scope-Drift
**Merge/Post-Merge:** 🔵 ausstehend

## Nächste drei vorgeplante Schritte

### 1. 🔵 I21 – Same-Root Copy/Move Preview Application
Nur Preview-Erzeugung für explizit gewählte Zielordner innerhalb derselben Root; kein Executor, kein Overwrite.

### 2. 🔵 I22 – Diagnose-Export Decision Gate
Entscheiden, ob und wie ein explizit angeforderter redigierter Diagnoseexport später geschrieben werden darf. Noch keine Implementierung.

### 3. 🔵 I17-B / I18-B – reale GUI-Evidence und sichtbare Komfort-Anbindung
Sobald Zielsystemzugriff möglich ist, echten 100/150/200-%-/Tastaturlauf abschließen und danach Such-/Sortieransichten sichtbar anbinden.