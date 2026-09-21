# PROVOWARE – Current Iteration

## I21 – Same-Root Copy/Move Preview Application

**Status:** 🟨 IMPLEMENTIERT / CI-ABNAHME AUSSTEHEND
**Fortschritt:** `████████░░ 80 %`

## A – FESTER PLAN

**Ziel:** den in I19 eingefrorenen Same-Root-Zielvertrag als gemeinsamen read-only Application-Core für Copy-/Move-Preview umsetzen.

**Checkpoints:**

- 🟢 `prepare_copy_preview()`
- 🟢 `prepare_move_preview()`
- 🟢 gemeinsamer interner Same-Root-Builder
- 🟢 aktuelles vollständiges Inventar als Auswahlquelle
- 🟢 expliziter existierender Zielordner
- 🟢 Zielordner B01-validiert
- 🟢 externe Ziele BLOCKED
- 🟢 Symlink-Ziele BLOCKED
- 🟢 fehlender Zielordner BLOCKED
- 🟢 Ziel-Datei statt Ordner BLOCKED
- 🟢 unbekannte Auswahl BLOCKED
- 🟢 doppelte Auswahl BLOCKED
- 🟢 leere Auswahl OPEN
- 🟢 Quelle=Ziel BLOCKED
- 🟢 bestehendes Ziel / Overwrite BLOCKED
- 🟢 kein Auto-Rename
- 🟢 I12 `make_plan()` wiederverwendet
- 🟢 I12 `validate_preview()` erneut ausgeführt
- 🟢 `writes_enabled=False`
- 🟢 kein Registry-/GUI-/CLI-Ausbau
- 🟢 Unit-/Negativtests
- 🟢 Core-Diagnostic um Copy/Move/Overwrite erweitert
- 🔵 Repository-/PR-CI
- 🔵 finaler Diff / Merge / Post-Merge

## B – VARIABLE FOLGEAUFGABE

**Quelle letzter Lauf:** I20 war bereits gemergt und Post-Merge-CI vollständig grün, während `CURRENT_ITERATION.md` Merge/Post-Merge noch als offen auswies.

**Maßnahme:** Statusdrift beim Wechsel auf I21 synchronisiert.

**Status:** 🟢 erledigt.

## Debugging-Schwerpunkt

I21 wird nicht nur über Positivtests abgesichert.

Die Negativmatrix enthält bewusst:

- Overwrite;
- externe Zielwurzel;
- Symlink-Ziel;
- fehlenden Zielordner;
- Ziel ist Datei;
- identische Quelle/Ziel;
- unbekannte Auswahl;
- doppelte Auswahl;
- leere Auswahl.

Der End-to-End-Core-Diagnostic reproduziert Copy/Move ausschließlich in `tempfile` und bestätigt unveränderte Quellen.

## Nicht-Ziele

- kein Executor;
- keine Copy-/Move-Ausführung;
- keine Persistenz;
- keine UI-/CLI-Anbindung;
- kein zweiter Root;
- kein Cross-Device Move;
- kein Overwrite;
- kein Auto-Rename;
- kein TOCTOU-Executor-Vertrag;
- keine Rechteausweitung.

## Exit-Gates

1. I21 Unit-/Negativtests PASS.
2. erweiterter Core-Diagnostic PASS.
3. Read-only-Lock PASS.
4. vollständige Test-Suite PASS.
5. Repository-Contract PASS.
6. Info-Text-Impact PASS.
7. bestehende B01–I20-Verträge regressionsfrei.
8. finaler Diff ohne Scope-Drift.
9. Post-Merge-CI PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I22 – Diagnose-Export Decision Gate
Entscheiden, ob ein explizit angeforderter redigierter Diagnosebericht später als Datei geschrieben werden darf. Noch keine Implementierung.

### 2. 🔵 I23 – Same-Root Zielauswahl Adapter-Decision
Erst nach realem I17-Befund entscheiden, wie Dateiauswahl + Zielordner in GUI und Zahlenmenü laiengerecht angebunden werden.

### 3. 🔵 I17-B / UI-Evidence
Echten 100/150/200-%-/Tastaturlauf weiterhin abschließen, sobald Zielsystemzugriff möglich ist.
