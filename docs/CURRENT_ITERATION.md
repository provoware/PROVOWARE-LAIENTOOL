# PROVOWARE – Current Iteration

## I11 – Read-only GUI-/CLI-Shell

**Status:** 🟨 IN ARBEIT
**Fortschritt:** `███████░░░ 70 %`

Der Prozentwert bildet ausschließlich definierte I11-Checkpoints ab.

## A – FESTER PLAN

**Quelle:** I10-Drei-Schritte-Vorausplanung + B02/B03 + GUI-/CLI-Paritätsvertrag.

**Ziel:** gemeinsamen read-only Application-/Navigation-Core schaffen und darauf sowohl ein laienfreundliches Zahlenmenü als auch eine optionale PySide6-Grundshell setzen.

**Checkpoints:**

- 🟢 gemeinsamer Application-Core
- 🟢 Registry um drei reale read-only Use Cases erweitert
- 🟢 Zahlenmenü ausschließlich aus Registry abgeleitet
- 🟢 PySide6-Shell ausschließlich als Adapter
- 🟢 vier dokumentierte Theme-Familien umgesetzt
- 🟢 Größenwahl 100/125/150/175/200 %
- 🟢 Starter-Routing für `--menu` und `--gui`
- 🟢 bestehende B01-Default-Startsemantik erhalten
- 🟢 technische Paritätstests angelegt
- 🔵 Repository-/PR-CI-Gates
- 🔵 finaler Diff / Merge / Post-Merge
- 🟨 reale visuelle Accessibility-Evidence bleibt separat OPEN

## B – VARIABLE FOLGEAUFGABE

**Quelle letzter Lauf:** I10 war bereits gemergt und Post-Merge-CI grün, während `CURRENT_ITERATION.md` noch „Merge / Post-Merge“ als offen auswies.

**Priorität:** Dokumentationsdrift.

**Maßnahme:** I11 startet vom bestätigten grünen I10-`main`; der alte Status wird damit ersetzt.

**Status:** 🟢 erledigt.

## Datei-Besitz dieser Iteration

| Datei | Schreibender Besitzer | Prüfer |
| --- | --- | --- |
| `src/provoware_laientool/application_core.py` | IMPLEMENT | VERIFY read-only |
| `src/provoware_laientool/cli_shell.py` | IMPLEMENT | VERIFY read-only |
| `src/provoware_laientool/gui_shell.py` | IMPLEMENT | VERIFY read-only |
| `src/provoware_laientool/ui_themes.py` | IMPLEMENT | VERIFY read-only |
| `src/provoware_laientool/capability_registry.py` | IMPLEMENT nach Core-Batch | VERIFY read-only |
| `start.py` | IMPLEMENT nach Adapter-Batch | VERIFY read-only |
| `tests/test_i11_shell.py` | IMPLEMENT/TEST-SCOPE | VERIFY read-only |
| `tests/test_capability_registry.py` | TEST-SCOPE nach Vertragsänderung | VERIFY read-only |
| `docs/I11_READONLY_SHELL.md` | DOC | VERIFY read-only |
| `docs/CURRENT_ITERATION.md` | ORGANIZE/DOC | VERIFY read-only |
| `README.md` | DOC | VERIFY read-only |
| `todo.txt` | DOC | VERIFY read-only |
| `scripts/repo_quality.py` | PROCESS-IMPLEMENT | VERIFY read-only |

Die Änderungen wurden serialisiert: zuerst Core/Adapter-Dateien, danach Registry/Starter-Vertrag.

## Nicht-Ziele

- keine Datei-Inventarisierung;
- keine Dateioperation;
- keine persistente Einstellung;
- kein Executor;
- kein Preview-/Recovery-Vorgriff;
- keine automatische Installation von PySide6;
- kein behauptetes visuelles Accessibility-PASS ohne reale Evidence.

## Exit-Gates

1. I11 Unit-/Paritätstests PASS.
2. vollständige Test-Suite PASS.
3. Repository-Contract PASS.
4. Info-Text-Impact PASS.
5. bestehender Preflight Text/JSON PASS.
6. finaler Diff ohne Scope-Drift.
7. Post-Merge-CI PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I12 – B05 Preview-Modell
**Ziel:** immutable Vorschauvertrag für spätere Dateiaktionen definieren.
**Abhängigkeit:** gemeinsamer Application-Core aus I11.
**Gate:** Quelle, Ziel, Wirkung, Umfang, Sicherheitsgrenzen und Rückweg modelliert; kein Executor.

### 2. 🔵 I13 – B06 Recovery-Zustandsvertrag
**Ziel:** Journal-/Undo-/Crash-/Recovery-Zustände fachlich definieren.
**Abhängigkeit:** Preview-Vertrag aus I12.
**Gate:** Zustandsautomat und Failure-Matrix vollständig; produktive Schreibpfade weiter gesperrt.

### 3. 🔵 I14 – reale Shell-/Accessibility-Evidence
**Ziel:** I11 auf echter PySide6-/Display-Umgebung bei 100/150/200 %, Tastatur, Fokus und Kontrast reproduzierbar prüfen.
**Abhängigkeit:** stabiler I11-Merge.
**Gate:** technisches PASS plus dokumentiertes Laien-/Accessibility-Ergebnis; offene Punkte bleiben OPEN.
