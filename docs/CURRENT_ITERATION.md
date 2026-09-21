# PROVOWARE – Current Iteration

## I15 – read-only Dateiinventar + I14-Fokus-DELTA

**Status:** 🟢 REPOSITORY-ANTEIL ABGESCHLOSSEN
**Fortschritt:** `█████████░ 90 %`

Der Prozentwert bildet ausschließlich definierte I15-Checkpoints ab.

## B – DELTA: I14-Fokusvertrag

Der bestätigte I14-Fokusbefund wurde zuerst separat umgesetzt und vollständig abgenommen.

- 🟢 `QPushButton:focus`
- 🟢 `QComboBox:focus`
- 🟢 `QTextEdit:focus`
- 🟢 automatisierter Accessibility-Re-Check
- 🟢 PR #15 gemergt
- 🟢 Post-Merge-CI PASS
- 🟨 reale Desktop-/Laien-Evidence bleibt weiterhin OPEN

## A – FESTER PLAN: read-only Dateiinventar

**Ziel:** eine explizit gewählte, B01-validierte Wurzel ausschließlich lesend rekursiv inventarisieren und neutrale Dateifakten für I16 bereitstellen.

**Checkpoints:**

- 🟢 immutable `InventoryItem`
- 🟢 immutable `InventoryIssue`
- 🟢 immutable `InventoryResult`
- 🟢 B01-Wurzelvalidierung
- 🟢 B01-Prüfung je gefundenem Pfad
- 🟢 rekursiver read-only Scan
- 🟢 reguläre Dateien mit relativem Pfad + Byte-Größe
- 🟢 Symlinks werden nicht verfolgt
- 🟢 Unicode/Leerzeichen bleiben erhalten
- 🟢 deterministische Sortierung
- 🟢 Zugriffsfehler als Befund statt Gesamtcrash
- 🟢 keine Preview-/Application-/GUI-/CLI-Vorwegnahme
- 🟢 Unit-Tests angelegt
- 🟢 Repository-/PR-CI PASS
- 🟢 finaler Diff ohne Scope-Drift
- 🔵 Merge / Post-Merge

## Datei-Besitz – A-PLAN

| Datei | Schreibender Besitzer | Prüfer |
| --- | --- | --- |
| `src/provoware_laientool/inventory.py` | IMPLEMENT | VERIFY read-only |
| `tests/test_inventory.py` | TEST-SCOPE | VERIFY read-only |
| `docs/I15_READONLY_INVENTORY.md` | DOC | VERIFY read-only |
| `docs/CURRENT_ITERATION.md` | ORGANIZE/DOC | VERIFY read-only |
| `README.md` | DOC | VERIFY read-only |
| `todo.txt` | DOC | VERIFY read-only |
| `scripts/repo_quality.py` | PROCESS-IMPLEMENT | VERIFY read-only |

## Nicht-Ziele

- keine Dateiänderung;
- kein Hashing;
- keine Duplikaterkennung;
- keine Klassifikation;
- keine Thumbnails/Vorschauerzeugung;
- kein `PreviewPlan`;
- keine Registry-/GUI-/CLI-Erweiterung;
- keine Persistenz;
- kein Executor;
- keine Freigabe produktiver Schreibpfade.

## Exit-Gates

1. Inventar-Unit-Tests PASS.
2. vollständige Test-Suite PASS.
3. Repository-Contract PASS.
4. Info-Text-Impact PASS.
5. B01/I12/I13/I14 regressionsfrei.
6. finaler Diff ohne Scope-Drift.
7. Post-Merge-CI PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I16 – Preview-Application-Use-Case
**Ziel:** I15-Inventarfakten in valide I12-Preview-Modelle überführen und über gemeinsamen Application-Core bereitstellen.
**Gate:** GUI-/CLI-Parität; kein Executor; keine Persistenz.

### 2. 🔵 I17 – realer I14-Zielsystemlauf
**Ziel:** echte PySide6-Shell bei 100/150/200 %, Tastatur, Fokus und Laienprofil prüfen.
**Gate:** dokumentiertes PASS/FAIL/OPEN; automatisierter Fokusvertrag bereits grün.

### 3. 🔵 I18 – read-only Inventar-Komfortschicht
**Ziel:** erst nach stabilem I16 Such-/Sortier-/Größenansichten auf denselben Inventarfakten planen.
**Gate:** weiterhin read-only; keine neue Fachlogik in GUI/CLI-Adaptern.
