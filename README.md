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
| I14 Accessibility-Evidence | historischer I14-Befund: Fokus für ComboBox/TextEdit fehlte; I15-DELTA ergänzt die Regeln, automatischer Re-Check läuft; reale Desktop-/Laienprüfung bleibt OPEN | 🟨 Re-Check läuft |
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

Siehe [ADR-0001](docs/adr/ADR-0001-ui-cli-foundation.md), das [UI-Designsystem](docs/UI_DESIGN_SYSTEM.md), die [Theme-Tokens](docs/theme-tokens.md), den [messbaren Laien-Qualitätsstandard](docs/LAIEN_QUALITY_STANDARD.md), die [Info-Text-Governance](docs/INFO_TEXT_GOVERNANCE.md) und den [GUI-/Konsolen-Paritätsvertrag](docs/GUI_CLI_PARITY.md).

## Repository-Struktur

```text
.
├── AGENTS.md                         # verbindliche Arbeits- und Agentenregeln
├── PROVOWARE_TODO_INPUT_POOL0.md    # eingefrorene Baseline + Implementierungs-Input-Pool
├── README.md                         # zentrale Projektübersicht
├── todo.txt                          # operative priorisierte Arbeitsliste
├── docs/
│   ├── CURRENT_ITERATION.md          # A/B-Iteration, Besitzmatrix, Status, nächste 3 Schritte
│   ├── adr/                          # Architekturentscheidungen
│   └── evidence/                     # Regeln für reproduzierbare Nachweise
├── scripts/repo_quality.py           # dependency-freier Repository-Gate
└── .github/
    ├── CODEOWNERS
    ├── PULL_REQUEST_TEMPLATE.md
    └── workflows/repo-quality.yml
```

Produktcode unter `src/` und zugehörige Tests werden nur blockweise angelegt, wenn Scope und Abnahme definiert sind. Aktuell existieren B01-Preflight/Pfadgrenzen, die gemeinsame Capability-Registry sowie der read-only I11 Application-/GUI-/CLI-Shell-Kern samt Tests; leere Architektur wird nicht auf Vorrat erzeugt.

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

## Automatische Qualitätsprüfung

`.github/workflows/repo-quality.yml` läuft ohne Projektabhängigkeiten und prüft zunächst nur Repository-Verträge:

- Pflichtdateien vorhanden;
- operative TODO-Struktur konsistent;
- Baseline enthält REQ-BASELINE-1 und B00–B11;
- keine Tkinter-Imports in zukünftigem Python-Produktionscode;
- GitHub Actions besitzen minimale `permissions:` und externe Actions sind auf Commit-SHAs gepinnt;
- kein Trailing-Whitespace in zentralen Text-/Codeformaten;
- dokumentationsrelevante Änderungen führen über einen diff-basierten Info-Text-Impact-Guard;
- `todo.txt` bleibt schema- und prioritätsgeprüft, ohne eine künstlich feste Eintragszahl.

Sobald Produktcode entsteht, wird dieser Gate gezielt um echte Unit-/Integrations-/GUI-Tests erweitert.

## Aktuelle Reihenfolge

1. **B00:** Designrichtung, vier Themes, Neon-/Workflow-Semantik und Accessibility-Grundregeln sind dokumentiert.
2. **B01:** B01-A Preflight und B01-B Pfad-/Symlink-Grenzen sind implementiert; der read-only Zweitgeräte-Evidence-Runner ist vorbereitet, die reale physische Ausführung bleibt offen.
3. **I10/I11:** gemeinsame Registry sowie read-only Application-/CLI-/GUI-Shell sind implementiert; reale visuelle Accessibility-Evidence bleibt OPEN.
4. **I12/B05:** immutable Preview-Vertrag ist implementiert; kein Executor und keine Schreibfreigabe.
5. **I13/B06:** Journal-/Undo-/Recovery-Zustandsvertrag ist implementiert; Persistenz und Executor bleiben weiterhin gesperrt.\n6. **I14/B04:** automatisierte Accessibility-Evidence ist reproduzierbar; aktueller expliziter Fokusvertrag ist noch nicht vollständig und reale Zielsystem-Evidence bleibt OPEN.

## Quellen der Wahrheit

1. aktuelle, explizit freigegebene Aufgabe / Change Request;
2. `AGENTS.md`;
3. akzeptierte ADRs;
4. `PROVOWARE_TODO_INPUT_POOL0.md` als Anforderungsbaseline;
5. `todo.txt` für operative Reihenfolge.

Bei Widerspruch wird nicht still geraten: Der Konflikt wird dokumentiert und die sicherere, kleinere Änderung gewählt.

## Nächster sicherer Schritt

**Den I14-Fokusbefund als separaten DELTA beheben und parallel den nächsten festen Planpunkt I15 ausschließlich read-only halten. Reale Accessibility bleibt bis zum Zielsystemlauf OPEN.**
