# PROVOWARE – Current Iteration

## I16 – Preview-Application-Use-Case

**Status:** 🟨 IMPLEMENTIERT / CI-ABNAHME AUSSTEHEND
**Fortschritt:** `████████░░ 80 %`

Der Prozentwert bildet ausschließlich definierte I16-Checkpoints ab.

## A – FESTER PLAN

**Quelle:** I15-Drei-Schritte-Vorausplanung + B05 + GUI-/CLI-Paritätsvertrag.

**Ziel:** I15-Inventarfakten ausschließlich über den gemeinsamen Application-Core in valide I12-Preview-Modelle überführen und denselben Use Case in GUI und Zahlenmenü verfügbar machen.

**Checkpoints:**

- 🟢 Registry-Use-Case `files.preview_trash`
- 🟢 GUI- und CLI-Verfügbarkeit aus derselben Registry
- 🟢 explizite Root-Eingabe zentral über `action_requires_root()`
- 🟢 gemeinsamer `prepare_trash_preview()`-Pfad
- 🟢 I15 `scan_inventory()` wird ausschließlich im Application-Core aufgerufen
- 🟢 unvollständiges Inventar erzeugt keinen PreviewPlan
- 🟢 InventoryItem → reversible Trash-PreviewItem
- 🟢 I12 `make_plan()` wiederverwendet
- 🟢 I12 `validate_preview()` erneut ausgeführt
- 🟢 `writes_enabled=False` bleibt erhalten
- 🟢 GUI sammelt nur Ordnerauswahl ein
- 🟢 CLI sammelt nur Ordnerpfad ein
- 🟢 keine duplizierte Inventar-/Preview-Fachlogik in Adaptern
- 🟢 Unit-/Paritätstests angelegt
- 🔵 Repository-/PR-CI
- 🔵 finaler Diff / Merge / Post-Merge

## B – VARIABLE FOLGEAUFGABE

**Quelle letzter Lauf:** I15 war bereits gemergt und Post-Merge-CI grün, während `CURRENT_ITERATION.md` Merge/Post-Merge noch als offen auswies.

**Priorität:** Dokumentationsdrift.

**Maßnahme:** I16 startet vom bestätigten grünen I15-`main`; der alte offene Merge-/Post-Merge-Status wird ersetzt.

**Status:** 🟢 erledigt.

## Warum I16 nur Trash-Preview erzeugt

Copy und Move benötigen ein ausdrücklich gewähltes Ziel. Eine solche Zielauswahl ist noch nicht freigegeben und wird nicht erfunden.

I16 nutzt deshalb ausschließlich den bereits reversibel modellierten `trash`-Previewpfad:

- keine Zielwahl;
- keine Dateiaktion;
- keine Executor-Freigabe.

## Datei-Besitz

| Datei | Schreibender Besitzer | Prüfer |
| --- | --- | --- |
| `src/provoware_laientool/application_core.py` | IMPLEMENT | VERIFY read-only |
| `src/provoware_laientool/capability_registry.py` | IMPLEMENT | VERIFY read-only |
| `src/provoware_laientool/cli_shell.py` | ADAPTER-IMPLEMENT | VERIFY read-only |
| `src/provoware_laientool/gui_shell.py` | ADAPTER-IMPLEMENT | VERIFY read-only |
| `tests/test_i16_preview_application.py` | TEST-SCOPE | VERIFY read-only |
| `docs/I16_PREVIEW_APPLICATION.md` | DOC | VERIFY read-only |
| `docs/GUI_CLI_PARITY.md` | DOC | VERIFY read-only |
| `docs/CURRENT_ITERATION.md` | ORGANIZE/DOC | VERIFY read-only |
| `README.md` | DOC | VERIFY read-only |
| `todo.txt` | DOC | VERIFY read-only |
| `scripts/repo_quality.py` | PROCESS-IMPLEMENT | VERIFY read-only |

## Nicht-Ziele

- keine echte Dateiaktion;
- kein Copy/Move;
- keine Zielauswahl;
- keine Schreibbestätigung;
- keine Journal-Persistenz;
- kein Undo-/Recovery-Executor;
- kein Executor;
- keine Persistenz;
- keine Suche/Sortierung/Größenkomfortschicht;
- keine automatische Downloads-Wurzel;
- keine neue Sicherheitslogik in GUI/CLI.

## Exit-Gates

1. I16-Unit-/Integrations-/Paritätstests PASS.
2. vollständige Test-Suite PASS.
3. Repository-Contract PASS.
4. Info-Text-Impact PASS.
5. bestehende B01/I12/I13/I14/I15-Verträge regressionsfrei.
6. finaler Diff ohne Scope-Drift.
7. Post-Merge-CI PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I17 – realer I14-Zielsystemlauf
**Ziel:** echte PySide6-Shell mit 100/150/200 %, Tab/Shift+Tab, Fokus, Kontrast, Reduced Motion und Laienprofil prüfen.
**Abhängigkeit:** automatisierter Fokusvertrag grün und I16 stabil.
**Gate:** dokumentiertes PASS/FAIL/OPEN ohne künstliche Hochstufung.

### 2. 🔵 I18 – read-only Inventar-Komfort
**Ziel:** Suche, Sortierung, Größenansichten und „größte Dateien“ ausschließlich auf I15-Inventarfakten aufbauen.
**Abhängigkeit:** I16 Application-Pfad stabil.
**Gate:** GUI-/CLI-Parität; keine Dateiänderung.

### 3. 🔵 I19 – Preview-Zielwahl-Decision-Gate
**Ziel:** erst nach I18 entscheiden, wie Copy/Move-Ziele sicher, laiengerecht und portabel ausgewählt werden.
**Abhängigkeit:** stabile read-only Inventar-/Preview-Nutzung.
**Gate:** nur Entscheidungs-/Vertragsarbeit; weiterhin kein Executor.
