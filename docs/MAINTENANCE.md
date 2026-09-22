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
8. GitHub-CI abwarten und nur fachlich dauerhafte Ergebnisse dokumentieren.

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

- `application_core.py`: gemeinsamer Navigation-/Result-Knoten; Same-Root Transfer-Preview ist als eigene stabile Verantwortung nach `transfer_application.py` ausgelagert.
- `transfer_application.py`: ausschließlich read-only Zielordner-Ermittlung und Copy/Move-Preview-Vorbereitung; kein Executor und keine Adapterlogik.
- README/TODO: keine erneute per-Iteration-CI-Chronik aufbauen.
- `scripts/repo_quality.py`: bleibt dünner Orchestrator; stabile Prüffamilien liegen unter `scripts/repo_quality_checks/`, neue Iterationsdateien werden weiterhin dynamisch erkannt.
- GUI/CLI: keine Fachlogik in Adapter zurückwandern lassen.
- Diagnose-Writer: Guard-REOPEN eng halten; keinen allgemeinen Schreibpfad daraus ableiten.
- Altbranches werden vor Löschung gegen `main` auf einzigartige Fach-/Sicherheitsinvarianten geprüft; alte Implementierungen werden nicht blind gemergt. Die Klassifikation vom 2026-09-21 liegt in `docs/evidence/EV-20260921-006-branch-hygiene-i27.md`.

### Branch- und PR-Hygiene

- Pro Arbeitsblock gibt es höchstens **einen offenen Integrations-PR** gegen `main`.
- Vor Beginn eines neuen Blocks werden offene PRs und benannte Arbeitsbranches gegen `main` geprüft.
- Ist ein PR fachlich bereits auf `main` enthalten, wird er mit Verweis auf den belegenden Commit als **überholt** geschlossen; er bleibt nicht als zweiter Integrationspfad offen.
- Ein alter Branch wird niemals für einen neuen Arbeitsblock wiederverwendet.
- Vor Branch-Löschung wird geprüft, ob einzigartige Commits oder noch nicht übernommene Sicherheitsinvarianten existieren. Nur eindeutig entbehrliche Branches dürfen entfernt werden.
- Nach einem erfolgreichen Merge wird die zugehörige Branch-/PR-Hygiene im selben Wartungslauf geprüft, damit offene Altpfade nicht bis zur nächsten Iteration liegenbleiben.

## 8. Testbudget und Schleifenschutz

Jeder Testlauf braucht einen Zweck, ein Budget und ein Stop-Kriterium.

| Ebene | Standardbudget | Wiederholung |
| --- | ---: | --- |
| einzelner targeted Test / Repository-Gate | 2 Minuten | max. 1 identischer Repro-Lauf |
| vollständige Unit-/Integration-Suite | 5 Minuten | erst nach Ursachenänderung erneut |
| GitHub-Job `repository-contract` | 15 Minuten gesamt | kein automatischer Retry; veraltete Runs werden abgebrochen |
| manueller GUI-/Evidence-Lauf | menschlich geführt | jederzeit klar abbrechbar |

Regeln:

- grün + unveränderter Stand = nicht erneut testen;
- rot = erst ersten ursächlichen Fehler isolieren, dann targeted;
- Timeout = Befund, nicht Anlass für blindes Retry;
- maximal zwei Reparaturzyklen pro Root Cause;
- bei drittem Reparaturbedarf: STOP und Re-Plan;
- kein wachsender Scope, nur um einen Test doch noch grün zu bekommen;
- Tests mit Schleifen brauchen endliche Iterationszahl oder Deadline.

### CI-Ökonomie und Post-Merge-Nachweis

- jeder Workflow besitzt einen `concurrency`-Schlüssel mit `cancel-in-progress: true`;
- neue Commits auf demselben PR/Ref ersetzen veraltete laufende Prüfungen statt sie parallel fertiglaufen zu lassen;
- `repo-quality` prüft PRs und `main`;
- `i25-gui-evidence` prüft nur I25-relevante Pfade, dafür sowohl im PR als auch nach Merge auf `main`;
- Post-Merge-Gates sind unabhängige Bestätigung des tatsächlich gemergten Heads, keine Aufforderung zu einem erneuten manuellen Nutzertest;
- I25-AUTO bewahrt ausschließlich synthetische Evidence (Screenshots, JSON, TXT, HTML) für 14 Tage als CI-Artefakt auf; keine realen Nutzdateien werden dafür verwendet;
- der GUI-Gate darf den pip-Downloadcache wiederverwenden, wenn der Cache-Key den Fingerprint von `requirements-gui.txt` enthält; die Test-Venv selbst bleibt pro Lauf frisch;
- technische GUI-Evidence kann dadurch nachträglich aus GitHub geprüft werden, ohne den Nutzer denselben Ablauf erneut ausführen zu lassen;
- ein grüner unveränderter Stand wird nicht manuell erneut gestartet.

### Portable-Paketvertrag

- Release-/Testpakete werden ausschließlich durch `scripts/build_portable_package.py` erzeugt;
- `start.sh` bleibt auch im ZIP der einzige kanonische Laufzeit-Starter;
- ein mitgeliefertes `wheelhouse/` erzwingt Offline-Installation mit `--no-index`; kein stiller Netzwerk-Fallback;
- jedes ZIP enthält `PACKAGE_MANIFEST.json` mit Commit und SHA-256 aller Nutzdateien;
- `scripts/validate_portable_package.py` validiert Paketpfade, Manifest, Fremdpfad und optional den Offline-Bootstrap;
- CI-Paketierung ersetzt keine physische Zweitgeräte-Evidence.

## 9. Ein-Befehl-Abnahme

```bash
timeout 2m python3 scripts/repo_quality.py && timeout 2m python3 scripts/read_only_guard.py && timeout 5m env PYTHONPATH=src python3 -m unittest discover -s tests -v && timeout 2m python3 scripts/core_diagnostics.py && timeout 2m python3 scripts/diagnostic_snapshot.py --json && timeout 2m python3 start.py && timeout 2m python3 start.py --json
```

Reale I17-GUI-Evidence bleibt davon getrennt und kann nicht durch Headless-CI ersetzt werden.
