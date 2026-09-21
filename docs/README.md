# PROVOWARE – Dokumentationsindex

Dieser Index ist der Einstiegspunkt für Menschen, Codex und Prüfer. Er zeigt **wofür** eine Datei zuständig ist. Aktueller Status wird nicht mehrfach kopiert: Für laufende Arbeit gilt `CURRENT_ITERATION.md`, für operative Prioritäten `todo.txt`.

## Schnellstart

| Frage | Quelle |
| --- | --- |
| Was ist das Projekt? | [README im Repository](../README.md) |
| Welche Regeln sind verbindlich? | [AGENTS.md](../AGENTS.md) |
| Was läuft gerade? | [CURRENT_ITERATION.md](CURRENT_ITERATION.md) |
| Was ist als Nächstes offen? | [todo.txt](../todo.txt) |
| Was war die ursprüngliche Baseline? | [PROVOWARE_TODO_INPUT_POOL0.md](../PROVOWARE_TODO_INPUT_POOL0.md) |
| Wie werden Änderungen wartbar gehalten? | [MAINTENANCE.md](MAINTENANCE.md) |

## Stabile Verträge

### Entwicklung und Qualität

- [UPDATE_ORCHESTRATION.md](UPDATE_ORCHESTRATION.md) – Zwei-Spuren-Prozess, Rollen und Dateibesitz.
- [REGRESSION_MATRIX.md](REGRESSION_MATRIX.md) – targeted-first bis Full-Suite/Real-Evidence.
- [DEBUGGING_STANDARD.md](DEBUGGING_STANDARD.md) – Fehlerklassen, Reproduktion und Diagnose.
- [INFO_TEXT_GOVERNANCE.md](INFO_TEXT_GOVERNANCE.md) – wann README, TODO, Docs und Evidence nachgeführt werden.
- [MAINTENANCE.md](MAINTENANCE.md) – Quellen der Wahrheit, Drift-Vermeidung und Wartungsroutine.

### UX, Accessibility und Adapter

- [UI_DESIGN_SYSTEM.md](UI_DESIGN_SYSTEM.md) – visuelle und interaktive Grundregeln.
- [theme-tokens.md](theme-tokens.md) – Theme-Tokens.
- [LAIEN_QUALITY_STANDARD.md](LAIEN_QUALITY_STANDARD.md) – messbare Laien-Gates.
- [GUI_CLI_PARITY.md](GUI_CLI_PARITY.md) – gemeinsamer Core für GUI und Zahlenmenü.

### Plattform und Sicherheitsgrenzen

- [B01_PLATFORM_PREFLIGHT.md](B01_PLATFORM_PREFLIGHT.md) – Zielsystem-/Capability-Prüfung.
- [B01_PATH_BOUNDARIES.md](B01_PATH_BOUNDARIES.md) – Pfad-, Traversal- und Symlink-Grenzen.
- [B01_SECOND_DEVICE_EVIDENCE.md](B01_SECOND_DEVICE_EVIDENCE.md) – Zweitgeräte-Nachweis.

## Iterationsverträge

Diese Dateien dokumentieren **fachliche Checkpoints**, nicht den flüchtigen Live-Status eines GitHub-Laufs.

| Iteration | Vertrag |
| --- | --- |
| I10 | [I10_CAPABILITY_REGISTRY.md](I10_CAPABILITY_REGISTRY.md) |
| I11 | [I11_READONLY_SHELL.md](I11_READONLY_SHELL.md) |
| I12 | [I12_PREVIEW_MODEL.md](I12_PREVIEW_MODEL.md) |
| I13 | [I13_RECOVERY_CONTRACT.md](I13_RECOVERY_CONTRACT.md) |
| I14 | [I14_ACCESSIBILITY_EVIDENCE.md](I14_ACCESSIBILITY_EVIDENCE.md) |
| I15 | [I15_READONLY_INVENTORY.md](I15_READONLY_INVENTORY.md) |
| I16 | [I16_PREVIEW_APPLICATION.md](I16_PREVIEW_APPLICATION.md) |
| I17 | [I17_TARGET_ACCESSIBILITY_RUN.md](I17_TARGET_ACCESSIBILITY_RUN.md) |
| I18 | [I18_READONLY_INVENTORY_COMFORT.md](I18_READONLY_INVENTORY_COMFORT.md) |
| I19 | [I19_TARGET_SELECTION_DECISION.md](I19_TARGET_SELECTION_DECISION.md) |
| I20 | [I20_DIAGNOSTIC_OBSERVABILITY.md](I20_DIAGNOSTIC_OBSERVABILITY.md) |
| I21 | [I21_SAME_ROOT_COPY_MOVE_PREVIEW.md](I21_SAME_ROOT_COPY_MOVE_PREVIEW.md) |
| I22 | [I22_DIAGNOSTIC_EXPORT_DECISION.md](I22_DIAGNOSTIC_EXPORT_DECISION.md) |
| I23 | [I23_TARGET_ADAPTER_DECISION.md](I23_TARGET_ADAPTER_DECISION.md) |
| I24 | [I24_DIAGNOSTIC_EXPORT_WRITER_DESIGN.md](I24_DIAGNOSTIC_EXPORT_WRITER_DESIGN.md) |
| I25 | [I25_TRANSFER_ADAPTERS.md](I25_TRANSFER_ADAPTERS.md) |
| I26 | [I26_DIAGNOSTIC_EXPORT_PREFLIGHT.md](I26_DIAGNOSTIC_EXPORT_PREFLIGHT.md) |

## Architektur und Evidence

- [ADR-0001 – UI/CLI Foundation](adr/ADR-0001-ui-cli-foundation.md) – grundlegende Architekturentscheidung.
- [Evidence-Regeln](evidence/README.md) – Aufbau und Zweck reproduzierbarer Nachweise.
- `docs/evidence/EV-*.md` – historische, reproduzierbare Prüfbelege.

## Pflegeprinzip

Eine Information soll **nur an einer Stelle führend** sein:

- Fähigkeiten und Grenzen: Fach-/Iterationsvertrag.
- aktuelle Arbeit: `CURRENT_ITERATION.md`.
- Prioritäten: `todo.txt`.
- Überblick: Repository-`README.md`.
- Architekturbegründung: ADR.
- gemessener Nachweis: Evidence.
- Prozess: `AGENTS.md` und die stabilen Prozessdokumente.

`scripts/repo_quality.py` prüft, dass interne Links auf existierende Ziele zeigen und alle `docs/I??_*.md` in diesem Index auffindbar bleiben.
