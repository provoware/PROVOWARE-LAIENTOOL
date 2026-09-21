# PROVOWARE – Current Iteration

## I23 – Same-Root Zielauswahl Adapter-Decision

**Status:** 🟢 REPOSITORY-ANTEIL ABGESCHLOSSEN
**Fortschritt:** `█████████░ 90 %`

## A – FESTER PLAN

**Ziel:** festlegen, wie I18-Auswahl und I21-Same-Root-Preview später laiengerecht und paritätsgleich in GUI und Zahlenmenü angebunden werden.

**Entscheidungen:**

- 🟢 gemeinsamer fachlicher Workflow für beide Adapter
- 🟢 geplante IDs `files.preview_copy` / `files.preview_move`
- 🟢 keine irreführenden Execute-Namen
- 🟢 gemeinsame Inputs: Root, relative Auswahl, Zielordner
- 🟢 GUI-Auswahl ausschließlich Darstellung/Eingabe auf I18
- 🟢 CLI nummeriert Dateien statt Dateinamenwissen vorauszusetzen
- 🟢 Zielordner bleibt Same-Root
- 🟢 Preview endet immer vor Write
- 🟢 Status PASS/OPEN/BLOCKED bleibt Core-seitig
- 🟢 keine Adapter-Sicherheitslogik
- 🟢 keine READY-Freigabe vor GUI+CLI+Parität+realer Accessibility-Evidence
- 🔒 keine sichtbare Implementierung in I23
- 🔒 kein Executor

## B – VARIABLE FOLGEAUFGABE

**Quelle letzter Lauf:** I22 wurde gemergt und Post-Merge-CI vollständig grün, während `CURRENT_ITERATION.md` Merge/Post-Merge noch offen zeigte.

**Maßnahme:** Statusdrift beim Wechsel auf I23 synchronisiert.

**Status:** 🟢 erledigt.

## Accessibility-Sperre

Der reale I17-Basislauf ist weiterhin OPEN.

Daher definiert I23 nur den Adaptervertrag. Sichtbare GUI-Erweiterungen werden nicht implementiert, bis die bestehende Shell real bei 100/150/200 %, Tastatur und Fokus geprüft wurde.

## Nicht-Ziele

- keine Registry-Änderung;
- keine GUI-Änderung;
- keine CLI-Änderung;
- kein neuer READY-Use-Case;
- kein Executor;
- keine Dateioperation;
- keine externe Zielwurzel;
- keine Persistenz.

## Exit-Gates

1. GUI-Workflow eindeutig beschrieben.
2. CLI-Workflow eindeutig beschrieben.
3. gemeinsame Input-/Statussemantik festgelegt.
4. READY-Gate an Parität + reale Accessibility gebunden.
5. Repository-Contract PASS.
6. Info-Text-Impact PASS.
7. Read-only-Lock PASS.
8. vollständige Regression-Suite PASS.
9. finaler Diff ohne Produktcode.
10. Post-Merge-CI PASS.

**Repository-/PR-CI:** 🟢 PASS
**Finaler Diff:** 🟢 nur Decision-/Statusdoku
**Merge/Post-Merge:** 🔵 ausstehend

## Nächste drei vorgeplante Schritte

### 1. 🔵 I24 – Diagnose-Export Writer Design
Create-only/no-overwrite, Partial-Write und gezielte Guard-REOPEN-Architektur technisch planen. Noch kein Writer.

### 2. 🔵 I17-B – realer GUI-Zielsystemlauf
Basis-Shell real prüfen; danach kann der I23-Adaptervertrag sichtbar implementiert werden.

### 3. 🔵 I25 – Adapter-Implementierung
Nur nach grünem I17: I18-Auswahl + I21 Preview in GUI und Zahlenmenü, weiterhin ohne Executor.
