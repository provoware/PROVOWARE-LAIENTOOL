# PROVOWARE-LAIENTOOL

Laienoptimiertes, sicherheitsorientiertes Desktop-Werkzeug zur Organisation und später kontrollierten Bereinigung des Download-Ordners auf Ubuntu/Kubuntu.

## Projektstatus

**Gesamtstatus:** 🟨 PLANUNG / REPOSITORY-FOUNDATION
**Schreibende Dateioperationen:** 🔒 GESPERRT
**Produktkern:** 🟨 read-only Kern vorhanden (`preflight`, Pfadgrenzen, gemeinsame Registry, Application-Core, CLI-/GUI-Shell); keine Schreiboperationen

| Bereich | Stand | Anzeige |
|---|---:|---|
| Anforderungsbaseline | 9/9 Originalanforderungen erfasst | 🟢 `██████████` 100 % |
| Qualitätsanforderungen | 20 definiert | 🟢 dokumentiert |
| Entwicklungsblöcke | B00–B11 definiert | 🟢 12 Blöcke |
| B00 Visuelle Orientierung | Designsystem definiert | 🟢 `██████████` 100 % |
| B01 Projektkern/Sicherheitsgrenzen | B01-A Preflight + B01-B Pfadgrenzen implementiert; standardisierter Zweitgeräte-Evidence-Runner vorbereitet, physischer Lauf offen | 🟨 `████████░░` 80 % |
| I10 GUI-/CLI-Registry | gemeinsame immutable Registry implementiert und geprüft | 🟢 `██████████` 100 % |
| I11 read-only Shell | gemeinsamer Core + Zahlenmenü + optionale PySide6-Shell implementiert; reale visuelle Accessibility-Evidence offen | 🟨 `████████░░` 80 % |
| I12 B05 Preview-Modell | immutable Preview-Vertrag mit B01-Pfadgrenzen implementiert; kein Executor | 🟢 `██████████` 100 % Modellstand |
| I13 B06 Recovery-Vertrag | Zustandsautomat, Journal-/Undo-Vertrag und Crash-Matrix implementiert; keine Persistenz/kein Executor | 🟢 Repository grün |
| I14 Accessibility-Evidence | Fokusvertrag für Button/ComboBox/TextEdit automatisiert grün; reale Desktop-/Laienprüfung bleibt OPEN | 🟨 reale Evidence OPEN |
| I15 Read-only Inventar | rekursiver B01-gebundener Nur-Lese-Inventarkern mit Symlink-Sperre, Unicode/Leerzeichen, Größenfakten und strukturierten Befunden implementiert | 🟢 Repository grün |
| I16 Preview-Application | Inventar → reversible Trash-Preview über gemeinsamen Application-Core; GUI/CLI sammeln nur die Ordnerwahl ein | 🟢 Repository grün |
| I17 Real-Accessibility | automatisierte Qt-Pipeline für 100/150/200 %, Tab/Shift+Tab, Fokus, synthetische Preview und fünf Screenshots; Chromium bündelt Bericht und eine finale Human-Abnahme | 🟨 I17-AUTO/HUMAN Evidence OPEN |
| I18 Inventar-Komfort | read-only Suche, Sortierung und Top-10/50/100-Größenansichten im Domain-/Application-Core; sichtbare GUI-Anbindung wartet auf realen I17-Lauf | 🟢 Repository grün; UI weiter gegated |
| I19 Zielwahl-Decision | Same-Root-Zielwahl ohne Overwrite beschlossen; externe Ziele bleiben gesperrt; statischer Read-only-Lock blockiert Schreib-APIs im Produktcode | 🟢 Decision + Guard grün |
| I20 Diagnose-Observability | redigierter read-only Diagnosebericht als Klartext/JSON, CLI-only Use Case und stdout-Helfer; kein Datei-Export | 🟢 Repository grün |
| I21 Same-Root Copy/Move Preview | gemeinsamer Core erzeugt Copy-/Move-Preview nur innerhalb derselben Root; Overwrite, externe Ziele und Auto-Rename blockiert | 🟢 Repository grün |
| I22 Diagnose-Export Decision | späterer expliziter redigierter lokaler Export grundsätzlich zulässig, aber nur mit eigenem Writer-/Guard-REOPEN; aktuell keine Implementierung | 🟢 Decision eingefroren |
| I23 Zielauswahl Adapter-Decision | gemeinsamer späterer GUI-/CLI-Workflow für I18-Auswahl + I21 Copy/Move-Preview festgelegt; sichtbare Implementierung wartet auf realen I17-Lauf | 🟢 Decision eingefroren |
| I24 Diagnose-Export Writer Design | create-only/no-overwrite, Partial-/Crash-Strategie und gezielter Guard-REOPEN technisch festgelegt; noch kein Writer | 🟢 Design eingefroren |
| I26 Diagnose-Export Preflight | immutable ExportPlan + serialisierter Payload, zweites Redaction-Gate, SHA-256/Größe und No-overwrite-Zielprüfung; vollständig read-only | 🟢 Repository-/Post-Merge-Gate grün |
| Schreibpfade | 0 freigegeben | 🔒 gesperrt |

> Prozentwerte beziehen sich nur auf klar definierte Checkpoints. Dokumentierte Planung ist keine Produktimplementierung.

## Zielbild

Der Standardweg soll ohne Terminal und ohne Fachwissen funktionieren: Wizard → Dashboard → geführter Workflow → Vorschau → ausdrückliche Freigabe → verständlicher Abschlusszustand. Fortgeschrittene Optionen werden progressiv geöffnet.

Wichtige Leitplanken:

- keine stille Installation, kein stiller Netzwerkzugriff, keine versteckte Rechteausweitung;
- Pfade, Dateinamen, Unicode und Symlinks gelten als nicht vertrauenswürdige Eingaben;
- keine schreibende Dateiaktion ohne Preview, definierte Zielgrenzen und Rückweg;
- Diagnose nur bewusst aktiviert und datensparsam;
- Status nie nur über Farbe: Symbol + Klartext + Zahl;
- 100 %, 150 % und 200 % Skalierung sowie Tastaturbedienung werden als Qualitätsgates behandelt.

## Architekturentscheidung

Die geplante GUI basiert auf **PySide6/Qt**. **Tkinter ist im Produktionscode ausgeschlossen.** Datei- und Tabellenansichten sollen Qt-Modelle/Delegates verwenden; Thumbnails und Vorschauen werden bedarfsgesteuert und außerhalb des UI-Threads geladen.

GUI und Linux-Konsole sind zwei Adapter desselben Fachkerns. Jede fachliche GUI-Funktion benötigt einen gleichwertigen laienfreundlichen Konsolenweg über ein Zahlen-Auswahlmenü; rein visuelle Ausnahmen müssen ausdrücklich begründet sein. Seit I10 beschreibt eine gemeinsame immutable Capability-/Use-Case-Registry Verfügbarkeit und Sicherheitsmetadaten für beide Adapter.

Siehe [ADR-0001](docs/adr/ADR-0001-ui-cli-foundation.md), das [UI-Designsystem](docs/UI_DESIGN_SYSTEM.md), die [Theme-Tokens](docs/theme-tokens.md), den [messbaren Laien-Qualitätsstandard](docs/LAIEN_QUALITY_STANDARD.md), die [Info-Text-Governance](docs/INFO_TEXT_GOVERNANCE.md), den [GUI-/Konsolen-Paritätsvertrag](docs/GUI_CLI_PARITY.md), die [Regressionsmatrix](docs/REGRESSION_MATRIX.md), den [Debugging-Standard](docs/DEBUGGING_STANDARD.md), den [Dokumentationsindex](docs/README.md) und den [Wartbarkeitsvertrag](docs/MAINTENANCE.md).

## Repository-Struktur

```text
.
├── AGENTS.md                         # verbindliche Arbeits- und Agentenregeln
├── PROVOWARE_TODO_INPUT_POOL0.md    # eingefrorene Baseline + Implementierungs-Input-Pool
├── README.md                         # zentrale Projektübersicht
├── todo.txt                          # operative priorisierte Arbeitsliste
├── docs/
│   ├── README.md                     # navigierbarer Dokumentationsindex
│   ├── MAINTENANCE.md                # Quellen der Wahrheit + Wartungsregeln
│   ├── CURRENT_ITERATION.md          # aktueller Arbeitsblock und nächste 3 Schritte
│   ├── adr/                          # Architekturentscheidungen
│   └── evidence/                     # Regeln für reproduzierbare Nachweise
├── scripts/repo_quality.py           # dependency-freier Repository-Gate
└── .github/
    ├── CODEOWNERS
    ├── PULL_REQUEST_TEMPLATE.md
    └── workflows/repo-quality.yml
```

Produktcode unter `src/` und zugehörige Tests werden nur blockweise erweitert, wenn Scope und Abnahme definiert sind. Der aktuelle Kern umfasst Preflight/Pfadgrenzen, Registry/Application-Core, read-only GUI/CLI-Shell, Inventar/View, Preview-/Recovery-Verträge sowie redigierte Diagnose- und Export-Preflight-Verträge. Produktive Schreibpfade bleiben gesperrt; leere Architektur wird nicht auf Vorrat erzeugt.

## Entwicklungsdisziplin

Verbindlicher Standard:

`ORGANIZE → PLAN → IMPLEMENT → VERIFY → DOC → EVIDENCE → CI → DIFF → MERGE → POST-MERGE VERIFY → NEXT-PLAN`

Vor jeder Änderung:

1. `AGENTS.md` und betroffene REQ/CR/ADR lesen.
2. Scope in einem Satz und Nicht-Ziele festlegen.
3. kleinsten zusammenhängenden Write-Batch planen.
4. nur relevante Tests ausführen.
5. Ergebnis, Risiken und offene Punkte als Evidence festhalten.

## Subagenten

Subagenten sind **triggerbasiert**, nicht standardmäßig aktiv. Explorer, Implementierer, Testprüfer, UX/Accessibility-Prüfer und Sicherheitsprüfer werden nur eingesetzt, wenn ihre Arbeit unabhängig, überschneidungsfrei und messbar günstiger ist. Schreibbesitz an einer Datei hat immer nur ein Agent.

Die vollständigen Trigger und Stop-Bedingungen stehen in [AGENTS.md](AGENTS.md). Der Update-Prozess wird zusätzlich durch den [Update-Organisator mit Zwei-Spuren-Modell](docs/UPDATE_ORCHESTRATION.md) geregelt. Der aktuelle A/B-Stand, die Besitzmatrix, der Iterationsfortschritt und die nächsten drei vorgeplanten Schritte stehen in [CURRENT_ITERATION.md](docs/CURRENT_ITERATION.md). Pro Write-Batch hat jede Datei genau einen schreibenden Besitzer; Prüfer bleiben read-only. Jede Iteration endet außerdem mit einer kurzen Drei-Schritte-Vorausplanung.

## Lokale Python-Umgebung

Der Standardweg ist **Venv-first** und **`start.sh` ist dauerhaft der einzige offizielle Nutzer-Einstiegspunkt**. System-Python wird nur verwendet, um die lokale `.venv` anzulegen; GUI, CLI und I17 laufen anschließend über die validierte Projektumgebung. Neue Startmodi werden in `start.sh` ergänzt statt durch neue Nutzerbefehle neben dem Starter.

Empfohlene Befehle:

```bash
./start.sh --check
./start.sh --setup
./start.sh --gui
./start.sh --i17
./start.sh --diagnostics
```

`start.sh` installiert niemals per `sudo`/`apt` und schreibt keine Python-Pakete in das System. Fehlt die lokale Umgebung oder die festgelegte GUI-Abhängigkeit, wird vor dem Erzeugen bzw. vor dem PyPI-Download ausdrücklich gefragt. Für bewusst nicht-interaktive Einrichtung existiert `--yes`.

Die GUI-Abhängigkeit ist in `requirements-gui.txt` reproduzierbar auf **PySide6 6.11.2** festgelegt. `.venv/` bleibt über `.gitignore` außerhalb des Repositories.

## Automatische Qualitätsprüfung

`.github/workflows/repo-quality.yml` läuft ohne Projektabhängigkeiten und prüft Repository-Verträge:

- stabile Pflichtdateien und dynamischen Iterationsindex;
- operative TODO-Struktur, Prioritäten und Duplikate;
- Baseline-Marker REQ-BASELINE-1 und B00–B11;
- Python-Syntax in Produktcode, Skripten, Tests und Starter;
- keine Tkinter-Imports im Python-Produktionscode;
- GitHub Actions mit minimalen `permissions:` und gepinnten externen Actions;
- interne relative Markdown-Links und versehentliche Tabellenumbrüche;
- keine flüchtigen CI-Statuskopien in README/TODO;
- kein Trailing-Whitespace in zentralen Text-/Codeformaten;
- diff-basierten Info-Text-Impact bei dokumentationsrelevanten Änderungen.

Der Gate umfasst inzwischen die vollständige Unit-/Integrationssuite, den read-only Preflight und einen temporären End-to-End-Core-Diagnoselauf. Reale GUI-Wahrnehmung bleibt bewusst ein separates Evidence-Gate.

## Aktueller technischer Stand

1. **B00/B01:** Designsystem, Preflight sowie Pfad-/Symlink-Grenzen sind dokumentiert bzw. implementiert; reale Zweitgeräte-Evidence bleibt offen.
2. **I10–I16:** Registry, read-only Shell, Preview-/Recovery-Verträge, Inventar und gemeinsamer Inventory→Preview-Pfad sind implementiert.
3. **I17:** I17-AUTO übernimmt Qt-, Layout-, Fokus-, Preview- und Screenshot-Evidence; Chromium zeigt Bericht und genau eine finale I17-HUMAN-Laienabnahme.
4. **I18–I21:** Inventar-Komfort, Read-only-Lock, Diagnose-Observability und Same-Root Copy/Move-Preview sind im Repository grün.
5. **I22–I24/I26:** Diagnose-Export ist entschieden und bis zum vollständig read-only ExportPlan-/Payload-Preflight vorgezogen; echter Writer und Guard-REOPEN bleiben gesperrt.
6. **Schreibpfade:** weiterhin `0` produktiv freigegeben.

## Quellen der Wahrheit

1. aktuelle, explizit freigegebene Aufgabe / Change Request;
2. `AGENTS.md`;
3. akzeptierte ADRs;
4. `PROVOWARE_TODO_INPUT_POOL0.md` als Anforderungsbaseline;
5. `todo.txt` für operative Reihenfolge.

Bei Widerspruch wird nicht still geraten: Der Konflikt wird dokumentiert und die sicherere, kleinere Änderung gewählt.

## Nächster sicherer Schritt

**I17-D wird über `./start.sh --i17` real auf dem Zielsystem ausgeführt. Danach folgt die Repository-Hygiene-/Aktualitätsanalyse; I25 bleibt bis zum vollständigen I17-PASS gesperrt.**


## Screenshots

Echte Produktoberflächen können im README gezeigt werden. Für belastbare Produktabbildungen gilt:

- bevorzugter Pfad: `docs/assets/screenshots/readme/`;
- nur echte Zielsystem-Screenshots aus einem dokumentierten I17-/Folgelauf;
- keine unnötigen privaten Pfade, Nutzernamen oder Dateinamen;
- Mockups separat unter `docs/assets/mockups/` und sichtbar als **Designentwurf** kennzeichnen;
- Mockups zählen niemals als Accessibility-/Produkt-Evidence.

Geplantes I17-Set: 100 %, 150 %, 200 %, Tastaturfokus und Dateivorschau.

## Regressionsstrategie

Die Entwicklung verwendet ab I17 die Matrix `docs/REGRESSION_MATRIX.md`:

**gezielte betroffene Tests zuerst → vollständige Testsuite vor Merge → Post-Merge-CI → reale Evidence nur dort, wo CI sie nicht ersetzen kann.**

Damit werden frühe Iterationsläufe kürzer, ohne die finale Abnahme zu schwächen.


## Read-only-Lock

Solange Executor und Persistenz nicht ausdrücklich freigegeben sind, prüft `scripts/read_only_guard.py` den Produktionscode statisch auf typische Schreib-APIs. Der Guard läuft vor der Full-Suite in CI und blockiert auch Import-Aliase sowie nicht statisch als read-only belegbare `open()`-Modi.


## Diagnose-Snapshot

Für Support/Debugging steht ein read-only, redigierter Snapshot bereit:

```bash
./start.sh --diagnostics
./start.sh --diagnostics-json
```

Er schreibt keine Datei, nutzt kein Netzwerk und zeigt keine Recovery-IDs. Home-Pfade, E-Mails und typische Token-Muster werden vor der Ausgabe redigiert.
