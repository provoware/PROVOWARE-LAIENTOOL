# PROVOWARE – Current Iteration

## I12 – B05 Immutable Preview-Modell

**Status:** 🟨 IN ARBEIT
**Fortschritt:** `███████░░░ 70 %`

Der Prozentwert bildet ausschließlich definierte I12-Checkpoints ab.

## A – FESTER PLAN

**Quelle:** I11-Drei-Schritte-Vorausplanung + B05 + AQ-001/AQ-003/AQ-004.

**Ziel:** einen immutable, fail-closed Preview-Vertrag für spätere Dateiaktionen schaffen, der Wirkung, Umfang, Pfadgrenzen und Rückweg beschreibt, ohne irgendeinen Executor oder Schreibzugriff einzuführen.

**Checkpoints:**

- 🟢 `PreviewItem` immutable definiert
- 🟢 `PreviewPlan` immutable definiert
- 🟢 `PreviewCheck` immutable definiert
- 🟢 `writes_enabled=False` fest im Plan
- 🟢 Aktionen auf `copy | move | trash` begrenzt
- 🟢 irreversible Direktlöschung nicht modelliert
- 🟢 Quellen an B01-Pfadvertrag gebunden
- 🟢 Ziele an B01-Pfadvertrag mit Planungsmodus gebunden
- 🟢 Wirkung, Byte-Umfang, Reversibilität und Recovery-Hinweis verpflichtend validiert
- 🟢 Tests für Außenpfad, fehlende Quelle, Doppel-ID, negative Größe, identische Quelle/Ziel und Trash-Reversibilität angelegt
- 🔵 Repository-/PR-CI-Gates
- 🔵 finaler Diff / Merge / Post-Merge

## B – VARIABLE FOLGEAUFGABE

**Quelle letzter Lauf:** I11 war bereits gemergt und Post-Merge-CI grün, während `CURRENT_ITERATION.md` noch „Merge / Post-Merge“ als offen auswies.

**Priorität:** Dokumentationsdrift.

**Maßnahme:** I12 startet vom bestätigten grünen I11-`main`; der alte Status wird damit ersetzt.

**Status:** 🟢 erledigt.

## Datei-Besitz dieser Iteration

| Datei | Schreibender Besitzer | Prüfer |
| --- | --- | --- |
| `src/provoware_laientool/preview_model.py` | IMPLEMENT | VERIFY read-only |
| `tests/test_preview_model.py` | IMPLEMENT/TEST-SCOPE | VERIFY read-only |
| `docs/I12_PREVIEW_MODEL.md` | DOC | VERIFY read-only |
| `docs/CURRENT_ITERATION.md` | ORGANIZE/DOC | VERIFY read-only |
| `README.md` | DOC | VERIFY read-only |
| `todo.txt` | DOC | VERIFY read-only |
| `scripts/repo_quality.py` | PROCESS-IMPLEMENT | VERIFY read-only |

## Nicht-Ziele

- kein Dateiinventar;
- kein Klassifizieren;
- kein Executor;
- kein Copy/Move/Delete/Trash-Echtlauf;
- kein Journal;
- kein Undo;
- kein Recovery-Mechanismus;
- keine GUI-/CLI-Erweiterung;
- keine TOCTOU-Freigabe.

## Exit-Gates

1. Preview-Unit-Tests PASS.
2. vollständige Test-Suite PASS.
3. Repository-Contract PASS.
4. Info-Text-Impact PASS.
5. bestehender B01/I11-Stand regressionsfrei.
6. finaler Diff ohne Scope-Drift.
7. Post-Merge-CI PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I13 – B06 Recovery-Zustandsvertrag
**Ziel:** Journal-/Undo-/Crash-/Recovery-Zustände fachlich definieren.
**Abhängigkeit:** I12 Preview-Vertrag grün.
**Gate:** Zustandsautomat + Failure-Matrix vollständig; keine produktive Dateioperation.

### 2. 🔵 I14 – reale Shell-/Accessibility-Evidence
**Ziel:** I11 auf echter PySide6-/Display-Umgebung mit 100/150/200 %, Tastatur, Fokus und Kontrast prüfen.
**Abhängigkeit:** stabiler I11/I12-`main`.
**Gate:** technisches PASS plus dokumentiertes Laien-/Accessibility-Ergebnis.

### 3. 🔵 I15 – read-only Dateiinventar
**Ziel:** B05 erstmals reale Downloads ausschließlich lesend inventarisieren und daraus Preview-Eingaben erzeugen.
**Abhängigkeit:** Preview- und Recovery-Verträge eingefroren.
**Gate:** keine Schreiboperation; Pfad-/Symlink-Grenzen; große Mengen/Sondernamen/Fehlerfälle getestet.
