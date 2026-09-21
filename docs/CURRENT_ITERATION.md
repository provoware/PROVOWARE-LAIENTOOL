# PROVOWARE – Current Iteration

## I10 – Gemeinsame Capability-/Use-Case-Registry

**Status:** 🟨 IN ARBEIT
**Fortschritt:** `██████░░░░ 60 %`

Der Prozentwert bildet ausschließlich die definierten Checkpoints dieser Iteration ab.

## A – FESTER PLAN

**Quelle:** I09-Drei-Schritte-Vorausplanung + GUI-/CLI-Paritätsvertrag.

**Ziel:** eine einzige unveränderliche Funktionsregistry bereitstellen, aus der spätere GUI- und Konsolenadapter dieselben Use Cases, Verfügbarkeiten und Sicherheitsmetadaten lesen.

**Checkpoints:**

- 🟢 immutable Registry-Modell implementiert
- 🟢 stabile Funktions-IDs und Laienanzeigename definiert
- 🟢 GUI-/CLI-Verfügbarkeit zentralisiert
- 🟢 Sicherheitsklasse, Preview-/Recovery-Pflicht und Status zentralisiert
- 🟢 Paritätsvalidator blockiert GUI ohne CLI
- 🟢 keine zukünftigen Produktfunktionen als READY vorgetäuscht
- 🟢 Unit-Tests für Kernverträge angelegt
- 🔵 Repository-/CI-Gates
- 🔵 finaler Diff / Merge / Post-Merge

## B – VARIABLE FOLGEAUFGABE

**B = NONE**

Der I09-Lauf erzeugte keinen neuen Repository-Fehler, keine Regression und keinen neuen Sicherheitsbefund. Die physische Zweitgeräte-Evidence bleibt eine bereits bekannte externe OPEN-Aufgabe und wird nicht künstlich als neuer DELTA-Patch geführt.

## Datei-Besitz dieser Iteration

| Datei | Schreibender Besitzer | Prüfer |
| --- | --- | --- |
| `src/provoware_laientool/capability_registry.py` | IMPLEMENT | VERIFY read-only |
| `tests/test_capability_registry.py` | IMPLEMENT | VERIFY read-only |
| `docs/I10_CAPABILITY_REGISTRY.md` | DOC | VERIFY read-only |
| `docs/GUI_CLI_PARITY.md` | DOC | VERIFY read-only |
| `docs/CURRENT_ITERATION.md` | ORGANIZE/DOC | VERIFY read-only |
| `README.md` | DOC | VERIFY read-only |
| `todo.txt` | DOC | VERIFY read-only |
| `scripts/repo_quality.py` | PROCESS-IMPLEMENT | VERIFY read-only |

## Nicht-Ziele

- keine GUI;
- kein Konsolenmenü;
- keine Dateioperation;
- keine Dateisuche;
- keine Plugin-Ladung;
- keine dynamische Registry;
- keine Änderung der B01-Sicherheitsgrenzen.

## Exit-Gates

1. Registry-Unit-Tests PASS.
2. vollständige Test-Suite PASS.
3. Repository-Contract PASS.
4. Info-Text-Impact PASS.
5. Preflight Text/JSON unverändert PASS.
6. finaler Diff ohne Scope-Drift.
7. Post-Merge-CI PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I11 – minimaler read-only UX-/CLI-Shell-Prototyp
**Ziel:** PySide6-Shell und laienfreundliches Konsolen-Zahlenmenü lesen dieselbe Registry.
**Abhängigkeit:** I10 Registry grün.
**Gate:** Navigation, Tastatur, 100/150/200 %, Parität und keine Nutzdaten-Schreiboperation.

### 2. 🔵 I12 – Preview-Modell vorbereiten
**Ziel:** B05 als immutable Preview-Modell für spätere Dateiaktionen entwerfen.
**Abhängigkeit:** gemeinsame Use-Case-Grenzen aus I10.
**Gate:** Wirkung, Quelle, Zielgrenzen und Rückweg modelliert; kein Executor.

### 3. 🔵 I13 – Recovery-Zustandsvertrag
**Ziel:** B06 Journal-/Undo-/Crash-Zustände fachlich definieren, bevor Schreibpfade entstehen.
**Abhängigkeit:** Preview-Vertrag aus I12.
**Gate:** Zustandsautomat + Failure-Matrix; Schreiboperationen bleiben gesperrt.
