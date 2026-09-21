# PROVOWARE – Wartbarkeitsvertrag

## Ziel

Wartbarkeit bedeutet hier: **wenige Quellen der Wahrheit, kleine Änderungen, automatische Konsistenzprüfung und kein Status, der nur deshalb veraltet, weil ein PR inzwischen gemergt wurde.**

Dieses Dokument ergänzt `AGENTS.md`; es ersetzt keine Sicherheits- oder Fachverträge.

## 1. Informationsarchitektur

| Information | Führende Quelle | Nicht duplizieren in |
| --- | --- | --- |
| Projektüberblick | `README.md` | Iterationsdetails |
| laufender Arbeitsblock | `docs/CURRENT_ITERATION.md` | mehrere Statuslisten |
| operative Priorität | `todo.txt` | README-Checklisten |
| Fach-/Sicherheitsvertrag | passendes `docs/I??_*.md` oder Bxx-Dokument | TODO-Langtext |
| Architekturbegründung | `docs/adr/**` | Quellcode-Kommentarblöcke |
| reproduzierbarer Nachweis | `docs/evidence/**` | Behauptungen ohne Evidence |
| Entwicklungsregeln | `AGENTS.md` + Prozessdokumente | Iterationsdateien |

Der navigierbare Einstiegspunkt ist [docs/README.md](README.md).

## 2. Dauerhafter Status statt Live-CI-Kopie

GitHub ist die Quelle für den **aktuellen** PR-, Merge- und Workflow-Zustand. Dauerhafte Repository-Texte speichern dagegen den belegten fachlichen Zustand.

Darum gilt:

- `README.md` und `todo.txt` verwenden `PASS`, `OPEN`, `LOCKED` oder konkrete Capability-Aussagen.
- Formulierungen wie „CI ausstehend“ oder „über CI einfrieren“ gehören nicht in dauerhafte Übersichten.
- Historische CI-/Merge-Nachweise dürfen mit Commit/Run-ID in Evidence oder Abschlussnotizen stehen.
- `CURRENT_ITERATION.md` darf laufende Gates zeigen, soll nach Abschluss aber keinen bereits überholten Merge-Zustand konservieren.

So entsteht nach einem Merge kein zwangsläufig falscher README-/TODO-Stand.

## 3. Wartungsroutine pro Änderung

1. kleinsten fachlich zusammenhängenden Diff bestimmen;
2. betroffene Quelle der Wahrheit identifizieren;
3. targeted Tests zuerst;
4. `python3 scripts/repo_quality.py`;
5. bei Produktcode `python3 scripts/read_only_guard.py`;
6. vollständige Suite vor Merge;
7. finalen Diff auf Status-/Dokumentationsdrift prüfen;
8. GitHub-CI abwarten und nur fachlich dauerhafte Ergebnisse dokumentierun.

Der Repository-Gate prüft zusätzlich interne Markdown-Links, Python-Syntax, Iterationsindex, Workflow-Pinning, TODO-Schema und Text-Hygiene.

## 4. Dateiwachstum und Verantwortungen

Neue Datei nur bei **neuer stabiler Verantwortung**. Vorher prüfen:

- Kann bestehende Logik ohne zusätzliche öffentliche Schnittstelle erweitert werden?
- Wird ein zweiter Fachkern erzeugt?
- Muss dieselbe Regel künftig an mehreren Stellen synchron gehalten werden?
- Kann ein Datenobjekt oder eine vorhandene Validierungsfunktion wiederverwendet werden?

### Soft-Review, kein starres CI-Limit

Ein Modul ab ungefähr **500 Zeilen** ist kein Fehler, aber ein Anlass zur Verantwortungsprüfung, bevor weitere Use-Cases hineingeschoben werden. Auf dem geprüften Stand liegt `application_core.py` an dieser Beobachtungsschwelle. Eine Aufteilung ist erst sinnvoll, wenn echte getrennte Verantwortungen erkennbar sind; kein Refactor nur wegen einer Zahl.

## 5. Dokumentationsregeln

- README bleibt Übersicht und verweist auf Detailverträge.
- `docs/README.md` enthält alle Iterationsverträge.
- Relative Markdown-Links müssen auf vorhandene Dateien/Ordner zeigen.
- Tabellen dürfen keine versehentlich als Text gespeicherten `\n`-Trenner enthalten.
- Evidence ist historisch; sie wird nicht nachträglich auf einen neuen Stand „umgeschrieben“.
- Die eingefrorene Baseline wird nur durch expliziten Change Request geöffnet.

## 6. Prüfebenen

| Ebene | Zweck |
| --- | --- |
| Repository-Contract | Struktur, Syntax, Links, Doku-Index, Workflow-Regeln |
| Info-Text-Impact | erkennt, ob eine Änderung Dokumentationswirkung besitzt |
| Read-only-Lock | verhindert unbeabsichtigte Schreibpfade |
| Targeted Tests | schneller erster Fachtest |
| Full Suite | Regression vor Merge |
| Core Diagnostic | End-to-End-Smoke auf temporären Daten |
| Real Evidence | GUI, Accessibility, Hardware und Zielsystemeigenschaften |

## 7. Bekannte Wartungsschwerpunkte

Diese Punkte sind bewusst zu beobachten, aber nicht automatisch zu refactoren:

- `application_core.py`: gemeinsamer Use-Case-Knoten; weitere Verantwortung nur nach Kohäsionsprüfung.
- README/TODO: keine erneute per-Iteration-CI-Chronik aufbauen.
- `scripts/repo_quality.py`: nur stabile Repository-Verträge prüfen; neue Iterationsdateien werden dynamisch erkannt statt einzeln hart codiert.
- GUI/CLI: keine Fachlogik in Adapter zurückwandern lassen.
- Diagnose-Writer: Guard-REOPEN eng halten; keinen allgemeinen Schreibpfad daraus ableiten.

## 8. Ein-Befehl-Abnahme

```bash
python3 scripts/repo_quality.py && python3 scripts/read_only_guard.py && PYTHONPATH=src python3 -m unittest discover -s tests -v && python3 scripts/core_diagnostics.py && python3 scripts/diagnostic_snapshot.py --json && python3 start.py && python3 start.py --json
```

Reale I17-GUI-Evidence bleibt davon getrennt und kann nicht durch Headless-CI ersetzt werden.
