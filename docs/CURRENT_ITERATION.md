# PROVOWARE – Current Iteration

## I13 – B06 Recovery-/Journal-Zustandsvertrag

**Status:** 🟢 REPOSITORY-ANTEIL ABGESCHLOSSEN
**Fortschritt:** `█████████░ 90 %`

Der Prozentwert bildet ausschließlich definierte I13-Checkpoints ab.

## A – FESTER PLAN

**Quelle:** I12-Drei-Schritte-Vorausplanung + B06 + AQ-001/AQ-002.

**Ziel:** einen reinen immutable Zustandsvertrag für Journal, Undo, Crash und Recovery definieren, bevor Persistenz oder Executor entstehen.

**Checkpoints:**

- 🟢 immutable `RecoveryContract`
- 🟢 immutable `JournalSnapshot`
- 🟢 expliziter Zustandsautomat
- 🟢 gefährliche Zustands-Sprünge gesperrt
- 🟢 Operation und Undo-Strategie gekoppelt
- 🟢 Journal-Pflicht nicht deaktivierbar
- 🟢 `FAILED` benötigt Fehlergrund
- 🟢 Crash-Matrix definiert
- 🟢 automatische Wiederholung in allen Crash-Zuständen gesperrt
- 🟢 Unit-Tests für Happy Path, Blockaden und Crashfälle angelegt
- 🟢 Repository-/PR-CI-Gates PASS
- 🟢 finaler Diff ohne Scope-Drift
- 🔵 Merge / Post-Merge

## B – VARIABLE FOLGEAUFGABE

**Quelle letzter Lauf:** Während I12 parallel bearbeitet wurde, landete PR #12 bereits auf `main`.

**Priorität:** Kollisionsschutz.

**Maßnahme:** divergierende Parallelfassung nicht mergen; den gemergten I12-`main` als alleinige Wahrheit übernehmen. Kein Doppelpatch.

**Status:** 🟢 erledigt.

## Datei-Besitz dieser Iteration

| Datei | Schreibender Besitzer | Prüfer |
| --- | --- | --- |
| `src/provoware_laientool/recovery_contract.py` | IMPLEMENT | VERIFY read-only |
| `tests/test_recovery_contract.py` | IMPLEMENT/TEST-SCOPE | VERIFY read-only |
| `docs/I13_RECOVERY_CONTRACT.md` | DOC | VERIFY read-only |
| `docs/CURRENT_ITERATION.md` | ORGANIZE/DOC | VERIFY read-only |
| `README.md` | DOC | VERIFY read-only |
| `todo.txt` | DOC | VERIFY read-only |
| `scripts/repo_quality.py` | PROCESS-IMPLEMENT | VERIFY read-only |

## Nicht-Ziele

- keine Dateioperation;
- keine Journal-Persistenz;
- kein Journal-Writer;
- kein Undo-/Recovery-Executor;
- kein Retry-System;
- keine GUI-/CLI-Erweiterung;
- keine TOCTOU-Freigabe;
- keine Schreibfreigabe.

## Exit-Gates

1. Recovery-Unit-Tests PASS.
2. vollständige Test-Suite PASS.
3. Repository-Contract PASS.
4. Info-Text-Impact PASS.
5. bestehender B01/I11/I12-Stand regressionsfrei.
6. finaler Diff ohne Scope-Drift.
7. Post-Merge-CI PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I14 – reale Shell-/Accessibility-Evidence
**Ziel:** I11 auf echter PySide6-/Display-Umgebung mit 100/150/200 %, Tastatur, Fokus und Kontrast prüfen.
**Abhängigkeit:** stabiler I11–I13-`main`.
**Gate:** dokumentiertes technisches + Laien-/Accessibility-Ergebnis.

### 2. 🔵 I15 – read-only Dateiinventar
**Ziel:** Downloads ausschließlich lesend inventarisieren und daraus valide Preview-Eingaben erzeugen.
**Abhängigkeit:** I12 Preview + I13 Recovery-Vertrag eingefroren.
**Gate:** keine Schreiboperation; Pfad-/Symlink-Grenzen; Sondernamen/große Mengen/Fehlerfälle getestet.

### 3. 🔵 I16 – Preview-Application-Use-Case
**Ziel:** valide Preview-Pläne aus bereits ermittelten Inventar-Fakten darstellen.
**Abhängigkeit:** I15 Inventar.
**Gate:** GUI/CLI-Parität, keine Persistenz, kein Executor, keine Nutzdaten-Schreiboperation.
