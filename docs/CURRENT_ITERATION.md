# PROVOWARE – Current Iteration

## I17 – realer Accessibility-Zielsystemlauf

**Status:** 🟨 EVIDENCE-INFRASTRUKTUR BEREIT / REALER ZIELSYSTEMLAUF OPEN
**Fortschritt:** `███████░░░ 70 %`

Der Prozentwert bildet ausschließlich definierte I17-Checkpoints ab.

## A – FESTER PLAN

**Quelle:** I16-Drei-Schritte-Vorausplanung + I14/I15 Accessibility-Evidence.

**Ziel:** die echte PySide6-Shell inklusive I16-Dateivorschau auf einer realen Display-Session bei 100/150/200 %, Tastatur, Fokus, Kontrast, Reduced Motion und Laienprofil reproduzierbar prüfen.

**Checkpoints:**

- 🟢 automatisierter Fokus-/Kontrast-/Skalierungsvertrag vorhanden
- 🟢 I17-Zielsystem-Helfer implementiert
- 🟢 PySide6-/Display-Fähigkeit wird vor Lauf geprüft
- 🟢 einheitlicher Ein-Befehl-Start definiert
- 🟢 manuelle 100/150/200-%-Gates definiert
- 🟢 Tab/Shift+Tab-Prüfpfad definiert
- 🟢 Dateivorschau-Abbruch-/Erfolgsprüfung definiert
- 🟢 Laienprofil mit vier Verständnisfragen definiert
- 🟢 feste Screenshot-Namen und Datenschutzregel definiert
- 🟢 README-Screenshot-Regel definiert
- 🟢 Regressionsmatrix „targeted first → full before merge“ dokumentiert
- 🟨 echter Zielsystemlauf OPEN
- 🟨 echte Screenshots OPEN
- 🟨 reales Laien-/Accessibility-Ergebnis OPEN
- 🔵 Repository-/PR-CI
- 🔵 finaler Diff / Merge / Post-Merge

## B – VARIABLE FOLGEAUFGABE

**Quelle letzter Lauf:** I16 war bereits gemergt und Post-Merge-CI grün, während `CURRENT_ITERATION.md` Merge/Post-Merge noch als offen auswies.

**Priorität:** Dokumentationsdrift.

**Maßnahme:** I17 startet vom bestätigten grünen I16-`main`; der alte offene Merge-/Post-Merge-Status wird ersetzt.

**Status:** 🟢 erledigt.

## Reale Zielsystem-Grenze

Dieser Repository-Lauf kann keinen echten Bildschirm, keine reale Tastaturführung und keine menschliche Wahrnehmung simulieren.

Deshalb gilt:

- CI kann die I17-Infrastruktur prüfen;
- CI kann den automatisierten Accessibility-Vertrag prüfen;
- CI darf **nicht** den realen Zielsystemlauf auf PASS setzen.

## Ein-Befehl-Lauf auf Zielsystem

```bash
python3 scripts/i17_target_evidence.py --launch-gui
```

## Screenshot-Set

- `i17-100-overview.png`
- `i17-150-overview.png`
- `i17-200-overview.png`
- `i17-keyboard-focus.png`
- `i17-file-preview.png`

Nur echte Zielsystem-Screenshots dürfen als Produktabbildung im README verwendet werden.

## Entwicklungs-/Regressionseffizienz

Die neue Regressionsmatrix trennt:

1. gezielten Erstlauf für den geänderten Verantwortungsbereich;
2. angrenzende Cross-Core-Tests nur bei tatsächlicher Relevanz;
3. vollständige Testsuite zwingend vor Merge;
4. echte GUI-/Hardware-Evidence separat.

Damit bleibt die Entwicklungsloop kurz, ohne die Merge-Abnahme abzusenken.

## Datei-Besitz

| Datei | Schreibender Besitzer | Prüfer |
| --- | --- | --- |
| `scripts/i17_target_evidence.py` | EVIDENCE-IMPLEMENT | VERIFY read-only |
| `tests/test_i17_target_evidence.py` | TEST-SCOPE | VERIFY read-only |
| `docs/I17_TARGET_ACCESSIBILITY_RUN.md` | DOC | VERIFY read-only |
| `docs/REGRESSION_MATRIX.md` | DOC/PROCESS | VERIFY read-only |
| `docs/CURRENT_ITERATION.md` | ORGANIZE/DOC | VERIFY read-only |
| `README.md` | DOC | VERIFY read-only |
| `todo.txt` | DOC | VERIFY read-only |
| `scripts/repo_quality.py` | PROCESS-IMPLEMENT | VERIFY read-only |

## Nicht-Ziele

- keine Behauptung eines realen GUI-PASS;
- keine produktive Dateiaktion;
- kein Executor;
- keine Persistenz;
- keine Copy-/Move-Freigabe;
- kein UI-Feature-Ausbau vor dem realen I17-Befund;
- keine Mockups als Evidence-Screenshots;
- keine automatische Installation von PySide6.

## Exit-Gates dieser Repository-Phase

1. I17-Helfertests PASS.
2. vollständige Test-Suite PASS.
3. Repository-Contract PASS.
4. Info-Text-Impact PASS.
5. bestehende B01–I16-Verträge regressionsfrei.
6. finaler Diff ohne Scope-Drift.
7. Post-Merge-CI PASS.
8. realer I17-Zielsystemlauf bleibt bis tatsächlicher Ausführung OPEN.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I17-B – echten Zielsystemlauf durchführen
**Ziel:** den vorbereiteten Ein-Befehl-Lauf auf echter PySide6-/Display-Umgebung ausführen und die fünf Screenshots erzeugen.
**Gate:** dokumentiertes PASS/FAIL/OPEN pro manuellem Gate.

### 2. 🔵 I18 – read-only UI-/Inventar-Komfort
**Ziel:** nach I17-Befund Oberfläche und Inventarkomfort zusammen weiterentwickeln: Suche, Sortierung, Größenansichten und „größte Dateien“ auf bestehendem Core.
**Gate:** GUI-/CLI-Parität für Fachfunktionen; sichtbare UI-Änderungen erneut Accessibility-gaten.

### 3. 🔵 I19 – Preview-Zielwahl-Decision-Gate
**Ziel:** Copy-/Move-Zielwahl fachlich und sicher definieren.
**Gate:** nur Vertrag/Entscheidung; weiterhin kein Executor.
