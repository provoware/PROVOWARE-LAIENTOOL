# PROVOWARE – Current Iteration

## I08 – Kollisionsschutz und GUI-/CLI-Parität

**Status:** 🟨 IN ARBEIT
**Fortschritt:** `████████░░ 80 %`

Der Prozentwert bildet ausschließlich die definierten Checkpoints dieser Iteration ab.

## A – FESTER PLAN

**Quelle:** bestehende Update-Orchestrierung + GUI-/CLI-Architekturvertrag.

**Ziel:** Rollen- und Schreibkollisionen verbindlich verhindern, Zwei-Stufen-TODO präzisieren, Drei-Schritte-Vorausplanung einführen und vollständige fachliche GUI-/CLI-Parität als Architekturvertrag festschreiben.

**Checkpoints:**

- 🟢 Rollen und Kollisionsschutz präzisiert
- 🟢 Datei-Besitzregel definiert
- 🟢 Zwei-Stufen-TODO präzisiert
- 🟢 Drei-Schritte-Vorausplanung definiert
- 🟢 Iterationsstatus mit Farb-/Fortschrittsanzeige definiert
- 🟢 GUI-/CLI-Paritätsvertrag erstellt
- 🟢 laienfreundliches Zahlenmenü als CLI-Standard festgelegt
- 🔵 CI/PR-Abnahme und Post-Merge-Prüfung

## B – VARIABLE FOLGEAUFGABE

**Quelle letzter Lauf:** Analyse des aktuellen Repository-Gates.

**Befund:** In `scripts/repo_quality.py` waren drei Pflichtdateien doppelt in `REQUIRED` eingetragen.

**Priorität:** Wartbarkeit / Entwicklungsdisziplin.

**Maßnahme:** Duplikate entfernen und einen Selbsttest ergänzen, der doppelte Pflichtdatei-Einträge künftig als Gate-Fehler meldet.

**Status:** 🟢 umgesetzt; endgültige Abnahme folgt mit CI.

## Datei-Besitz dieser Iteration

| Datei | Schreibender Besitzer | Prüfer |
| --- | --- | --- |
| `AGENTS.md` | IMPLEMENT/DOC dieser Iteration | VERIFY read-only |
| `docs/UPDATE_ORCHESTRATION.md` | IMPLEMENT/DOC dieser Iteration | VERIFY read-only |
| `docs/GUI_CLI_PARITY.md` | IMPLEMENT/DOC dieser Iteration | VERIFY read-only |
| `docs/adr/ADR-0001-ui-cli-foundation.md` | IMPLEMENT/DOC dieser Iteration | VERIFY read-only |
| `README.md` | DOC dieser Iteration | VERIFY read-only |
| `todo.txt` | DOC dieser Iteration | VERIFY read-only |
| `.github/PULL_REQUEST_TEMPLATE.md` | PROCESS-IMPLEMENT dieser Iteration | VERIFY read-only |
| `scripts/repo_quality.py` | PROCESS-IMPLEMENT dieser Iteration | VERIFY read-only |
| `docs/CURRENT_ITERATION.md` | ORGANIZE/DOC dieser Iteration | VERIFY read-only |

Keine Datei besitzt zwei parallele schreibende Besitzer.

## Nicht-Ziele

- keine neue Produktfunktion;
- keine GUI-Implementierung;
- keine CLI-Implementierung;
- keine Schreiboperation auf Nutzerdaten;
- keine Änderung der eingefrorenen Anforderungsbaseline.

## Exit-Gates

1. Repository-Contract PASS.
2. Info-Text-Impact PASS.
3. bestehende B01-Unit-Tests PASS.
4. read-only Preflight Text/JSON PASS.
5. finaler Diff ohne Scope-Drift.
6. Post-Merge-CI PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I09 – B01 Zweitgeräte-Evidence schließen
**Ziel:** realen Preflight auf dem zweiten Zielgerät ausführen und Portabilitätsnachweis abschließen.
**Abhängigkeit:** I08 muss grün eingefroren sein.
**Gate:** reproduzierbare Evidence; keine Produktänderung nötig.

### 2. 🔵 I10 – gemeinsame Capability-/Use-Case-Registry
**Ziel:** zentralen Fachfunktionskatalog schaffen, aus dem GUI und Konsolenmenü dieselben Funktionen beziehen.
**Abhängigkeit:** GUI-/CLI-Paritätsvertrag aus I08.
**Gate:** keine doppelte Fachlogik; Registry-Tests; weiterhin read-only.

### 3. 🔵 I11 – minimaler read-only UX-/CLI-Shell-Prototyp
**Ziel:** erste navigierbare PySide6-Shell und äquivalentes Konsolen-Zahlenmenü auf demselben Core-Vertrag.
**Abhängigkeit:** I10 Registry.
**Gate:** Laienstandard, Tastatur, 100/150/200 %, Paritätstest und keine Nutzdaten-Schreiboperation.
