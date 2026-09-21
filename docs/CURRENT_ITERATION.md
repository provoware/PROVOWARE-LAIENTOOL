# PROVOWARE – Current Iteration

## M01 – Info-Text-Konsistenz und Wartbarkeit

**Status:** 🟢 REPOSITORY-BLOCK UMGESETZT
**Fortschritt:** `██████████ 100 %`

**Basis vor M01:** `fcbdd9048eb082cd86a73cff74bacc43dbf6d299`

Der I26-Merge war auf `main` bereits abgeschlossen. Der anschließende `repo-quality`-Push-Lauf **#83** (ID `35633942745`) war vollständig grün. M01 verändert keine Produktlogik.

## A – FESTER PLAN

**Ziel:** Informationsdateien und Repository-Wartbarkeit vollständig prüfen, nachgewiesene Drift beheben und künftige Inkonsistenzen früher automatisch stoppen.

### Analysebefunde

- 🟢 14 Produktmodule unter `src/`, zusammen ca. 2.355 Python-Zeilen geprüft.
- 🟢 17 Testdateien mit 143 Testmethoden; keine TODO/FIXME-Häufung festgestellt.
- 🟢 8 Wartungs-/Evidence-Skripte vorhanden.
- 🟡 `application_core.py` liegt bei rund 500 Zeilen: Beobachtungsschwelle, aber aktuell kein begründeter Zwangsrefactor.
- 🔴 README und TODO enthielten mehrere bereits überholte „CI ausstehend/über CI einfrieren“-Angaben.
- 🔴 diese Datei meldete I26 Merge/Post-Merge noch als ausstehend, obwohl `main` und Lauf #83 grün waren.
- 🔴 `docs/REGRESSION_MATRIX.md` enthielt einen wörtlichen Backslash-n-Tabellenumbruch.
- 🟡 `scripts/repo_quality.py` führte fast jede Iterationsdatei einzeln als Pflichtdatei; das erzeugte unnötige Pflegekopplung.
- 🟡 ein zentraler navigierbarer Dokumentationsindex fehlte.

### Umgesetzter Wartungsblock

- 🟢 `docs/README.md` als Dokumentationsindex.
- 🟢 `docs/MAINTENANCE.md` als dauerhafter Wartungsvertrag.
- 🟢 README/TODO auf dauerhafte Capability-/OPEN-/LOCKED-Aussagen statt flüchtiger CI-Kopien umgestellt.
- 🟢 Regressionsmatrix repariert.
- 🟢 Repository-Gate modularisiert.
- 🟢 alle Python-Dateien in `src/`, `scripts/`, `tests/` und `start.py` werden syntaktisch geprüft.
- 🟢 relative Markdown-Links werden auf existierende Ziele geprüft.
- 🟢 alle `docs/I??_*.md` müssen im Dokumentationsindex auffindbar sein.
- 🟢 versehentliche wörtliche Backslash-n-Tabellenumbrüche werden blockiert.
- 🟢 flüchtige CI-Statusformulierungen in README/TODO werden blockiert.

## B – VARIABLE FOLGEAUFGABE

**Quelle:** Vollanalyse der Informationsarchitektur.

**Befund:** Der bisherige Prozess spiegelte PR-/Merge-/CI-Livezustände in dauerhaften Dateien. Dadurch entstand unmittelbar nach erfolgreichen Merges wieder Statusdrift.

**Maßnahme:** GitHub bleibt Quelle für aktuellen PR-/Workflow-/Merge-Zustand. Dauerhafte Repo-Texte speichern Capability-, OPEN-/LOCKED- und historische Evidence-Zustände.

**Status:** 🟢 in Governance und Wartungsvertrag überführt.

## Sicherheitsgrenze

M01 verändert ausschließlich Dokumentation, Repository-Prüfcode und PR-Prozessmetadaten.

Kein:

- Produktverhalten;
- Datei-Executor;
- Persistenz;
- Guard-REOPEN;
- Netzwerkpfad im Produkt;
- Dependency-Zuwachs.

## Exit-Gates

1. Repository-Contract PASS.
2. Info-Text-Impact PASS.
3. Read-only-Lock PASS.
4. vollständige Regression-Suite PASS.
5. Core Diagnostic PASS.
6. Diagnostic Snapshot PASS.
7. Starter-Preflight Klartext/JSON PASS.
8. finaler Diff ohne Produktlogik.
9. PR-CI PASS.
10. Post-Merge-Main-CI PASS.

## Nächste drei vorgeplante Produktschritte

### 1. 🔵 I17-B – realer GUI-Zielsystemlauf
Weiterhin einziges sichtbares UI-/Accessibility-Gate.

### 2. 🔵 I25 – Adapter-Implementierung
Erst nach grünem realem I17-Befund.

### 3. 🔵 I27 – Writer-spezifischer Guard Decision/Prototype
Zuerst exakte Guard-Architektur und No-clobber-Plattformbeweis; noch kein produktiver Export-Adapter.
