# PROVOWARE – Current Iteration

## I18 – read-only Inventar-Komfortkern

**Status:** 🟢 REPOSITORY-ANTEIL ABGESCHLOSSEN
**Fortschritt:** `█████████░ 90 %`

Der Prozentwert bildet ausschließlich definierte I18-Checkpoints ab.

## A – FESTER PLAN

**Quelle:** I17-Drei-Schritte-Vorausplanung.

**Ziel:** Suche, Sortierung und größte-Dateien-Ansichten auf den bestehenden I15-Inventarfakten vorbereiten, ohne sichtbare GUI-Erweiterung und ohne neuen Dateisystem-Schreibpfad.

**Checkpoints:**

- 🟢 immutable `InventoryViewSpec`
- 🟢 immutable `InventoryView`
- 🟢 Unicode-/Casefold-Suche
- 🟢 Name auf-/absteigend
- 🟢 Größe auf-/absteigend
- 🟢 exakt 10/50/100 größte Dateien
- 🟢 deterministische Tie-Breaks
- 🟢 vollständige Summary trotz sichtbarem Limit
- 🟢 ungültige Sortierung/Limit fail-closed
- 🟢 gemeinsamer Application-Pfad `prepare_inventory_view()`
- 🟢 keine Such-/Sortierlogik in GUI/CLI
- 🟢 professioneller temporärer Core-Diagnoselauf
- 🟢 Debugging-Klassifikation PRODUCT / TEST / INFRASTRUCTURE / EVIDENCE
- 🟢 CI-Diagnostic-Gate ergänzt
- 🟢 Repository-/PR-CI PASS
- 🟢 finaler Diff ohne Scope-Drift
- 🔵 Merge / Post-Merge

## B – VARIABLE FOLGEAUFGABE

**B = NONE**

Aus dem letzten Lauf entstand kein neuer objektiver Produktfehler, der einen eigenen DELTA-Write-Batch rechtfertigt.

Der reale I17-Zielsystemlauf bleibt als externe Evidence-Aufgabe OPEN und wird nicht künstlich in diesen Repository-Block umgedeutet.

## Warum noch keine sichtbare I18-GUI

Der nichtvisuelle Komfortkern kann vollständig automatisiert geprüft werden.

Die sichtbare Anbindung wird bewusst erst nach realer I17-100/150/200-%-/Tastatur-Evidence freigegeben, damit Layout-Probleme nicht in einen größeren UI-Ausbau hineinmultipliziert werden.

## Core Diagnostic

```bash
python3 scripts/core_diagnostics.py
python3 scripts/core_diagnostics.py --json
```

Der Lauf verwendet ausschließlich ein temporäres Dateisystem und prüft:

- Symlink-Sperre;
- Inventar;
- größte-Dateien-Sicht;
- gemeinsamen Application-Pfad;
- Preview-Vertrag;
- unveränderte Quellen.

## Datei-Besitz

| Datei | Schreibender Besitzer | Prüfer |
| --- | --- | --- |
| `src/provoware_laientool/inventory_view.py` | DOMAIN-IMPLEMENT | VERIFY read-only |
| `src/provoware_laientool/application_core.py` | APPLICATION-IMPLEMENT | VERIFY read-only |
| `tests/test_inventory_view.py` | TEST-SCOPE | VERIFY read-only |
| `scripts/core_diagnostics.py` | DIAGNOSTIC-IMPLEMENT | VERIFY read-only |
| `tests/test_core_diagnostics.py` | TEST-SCOPE | VERIFY read-only |
| `docs/I18_READONLY_INVENTORY_COMFORT.md` | DOC | VERIFY read-only |
| `docs/DEBUGGING_STANDARD.md` | DOC/PROCESS | VERIFY read-only |
| `docs/REGRESSION_MATRIX.md` | DOC/PROCESS | VERIFY read-only |
| `.github/workflows/repo-quality.yml` | PROCESS-IMPLEMENT | VERIFY read-only |
| `.github/PULL_REQUEST_TEMPLATE.md` | PROCESS-DOC | VERIFY read-only |
| `docs/CURRENT_ITERATION.md` | ORGANIZE/DOC | VERIFY read-only |
| `README.md` | DOC | VERIFY read-only |
| `todo.txt` | DOC | VERIFY read-only |
| `scripts/repo_quality.py` | PROCESS-IMPLEMENT | VERIFY read-only |

## Nicht-Ziele

- kein sichtbarer GUI-Ausbau vor realem I17;
- keine neue CLI-Fachoberfläche;
- keine Dateiänderung;
- kein Hashing;
- keine Duplikaterkennung;
- keine Persistenz;
- kein Executor;
- keine Copy-/Move-Zielwahl;
- kein automatisches Reparieren eines Diagnosebefunds.

## Exit-Gates

1. I18-View-Tests PASS.
2. Core-Diagnostic-Test PASS.
3. temporärer Core-Diagnoselauf PASS.
4. vollständige Test-Suite PASS.
5. Repository-Contract PASS.
6. Info-Text-Impact PASS.
7. B01–I17 repository-seitig regressionsfrei.
8. finaler Diff ohne Scope-Drift.
9. Post-Merge-CI PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I18-B – sichtbare Komfort-Anbindung nach realem I17
**Ziel:** Such-/Sortier-/Top-Ansichten ausschließlich über `prepare_inventory_view()` in GUI und Zahlenmenü darstellen.
**Gate:** reale 100/150/200-%-Evidence; GUI-/CLI-Parität.

### 2. 🔵 I19 – Preview-Zielwahl-Decision-Gate
**Ziel:** sichere Copy-/Move-Zielauswahl definieren.
**Gate:** Vertrag/Entscheidung; weiterhin kein Executor.

### 3. 🔵 I20 – Diagnose-/Recovery-Observability
**Ziel:** datensparsame, exportierbare Diagnoseberichte für reale Fehlerfälle planen.
**Gate:** Opt-in, Redaction, keine Secrets, keine automatischen Reparaturen.
