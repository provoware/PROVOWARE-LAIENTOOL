# PROVOWARE-LAIENTOOL

Laienoptimiertes, sicherheitsorientiertes Desktop-Werkzeug zur Organisation und später kontrollierten Bereinigung des Download-Ordners auf Ubuntu/Kubuntu.

## Projektstatus

**Gesamtstatus:** 🟨 PLANUNG / REPOSITORY-FOUNDATION
**Schreibende Dateioperationen:** 🔒 GESPERRT
**Produktkern:** 🟨 read-only B01-Kern vorhanden (`preflight` + Pfadgrenzen); noch keine produktive GUI und keine Schreiboperationen

| Bereich | Stand | Anzeige |
|---|---:|---|
| Anforderungsbaseline | 9/9 Originalanforderungen erfasst | 🟢 `██████████` 100 % |
| Qualitätsanforderungen | 20 definiert | 🟢 dokumentiert |
| Entwicklungsblöcke | B00–B11 definiert | 🟢 12 Blöcke |
| B00 Visuelle Orientierung | Designsystem definiert | 🟢 `██████████` 100 % |
| B01 Projektkern/Sicherheitsgrenzen | B01-A Preflight + B01-B Pfadgrenzen implementiert; Zweitgeräte-Evidence offen | 🟨 `████████░░` 80 % |
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

GUI und Linux-Konsole sind zwei Adapter desselben Fachkerns. Jede fachliche GUI-Funktion benötigt einen gleichwertigen laienfreundlichen Konsolenweg über ein Zahlen-Auswahlmenü; rein visuelle Ausnahmen müssen ausdrücklich begründet sein. Beide Adapter verwenden dieselben Use Cases, Sicherheitsregeln, Preview-/Recovery-Verträge und Fachresultate.

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

Produktcode unter `src/` und zugehörige Tests werden nur blockweise angelegt, wenn Scope und Abnahme definiert sind. Aktuell existieren der read-only B01-Preflight und die Pfad-/Symlink-Grenzen samt Unit-Tests; leere Architektur wird nicht auf Vorrat erzeugt.

## Entwicklungsdisziplin

Verbindlicher Standard:

`READ → DECIDE → ONE WRITE BATCH → LOCAL TEST → LOCAL EVIDENCE → ONE REMOTE HEAD → TARGETED CI → DIFF → MERGE → POST-MERGE QUALITY`

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
2. **B01:** B01-A Preflight und B01-B Pfad-/Symlink-Grenzen sind implementiert; reale Zweitgeräte-Evidence bleibt offen.
3. Erst anschließend UX-Shell und weitere Fachblöcke schrittweise freigeben.
4. **B06 bleibt P0-Gate:** keine produktiven Schreiboperationen vor belegtem Preview-, Journal-, Undo- und Recovery-Vertrag.

## Quellen der Wahrheit

1. aktuelle, explizit freigegebene Aufgabe / Change Request;
2. `AGENTS.md`;
3. akzeptierte ADRs;
4. `PROVOWARE_TODO_INPUT_POOL0.md` als Anforderungsbaseline;
5. `todo.txt` für operative Reihenfolge.

Bei Widerspruch wird nicht still geraten: Der Konflikt wird dokumentiert und die sicherere, kleinere Änderung gewählt.

## Nächster sicherer Schritt

**B01 zunächst auf Zweitgeräte-Evidence schließen; danach den nächsten freigegebenen Planpunkt über den Update-Organisator bestimmen.**
