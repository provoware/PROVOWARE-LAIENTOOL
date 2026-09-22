# PROVOWARE-LAIENTOOL

Ein sicheres Programm zum Ordnen des Download-Ordners unter Ubuntu und Kubuntu. Das Programm zeigt Änderungen zuerst nur als Vorschau. Im normalen Programmweg wird derzeit **keine Datei verschoben, gelöscht oder überschrieben**.

## Auf einen Blick

| Zeichen | Bedeutung | Stand |
| --- | --- | --- |
| 🟢 | automatisch geprüft | Programmstart, Vorschau, Diagnose und Schutzregeln |
| 🟡 | Prüfung durch einen Menschen fehlt | Bedienung für Verschieben/Kopieren und Diagnose-Ausgabe |
| 🔴 | nicht verfügbar | keine bekannten Hauptfehler |
| 🔒 | bewusst gesperrt | alle schreibenden Dateiaktionen |

**Freigabefortschritt:** `███░░░░░░░ 25 %` — **3 offene Freigaben**

Die Prozentzahl bildet genau vier Freigaben ab: automatische Prüfung, Bedienprüfung für Kopieren und Verschieben, Bedienprüfung für die Diagnose-Ausgabe und Prüfung auf einem zweiten Rechner. Die automatische Prüfung ist abgeschlossen. Die übrigen drei Prüfungen sind offen. Eine fertige Planung zählt nicht als fertige Funktion.

## Schnellstart in drei Stufen

### Stufe 1 – Erst prüfen

1. Öffnen Sie ein Terminal im Projektordner.
2. Prüfen Sie, ob die nötige lokale Umgebung bereits vorhanden ist:

   ```bash
   ./start.sh --check
   ```

3. Zeigt die Prüfung gelb oder rot, richten Sie die lokale Umgebung ein:

   ```bash
   ./start.sh --setup
   ```

   Das Programm fragt vor dem Anlegen der Umgebung und vor einem Herunterladen nach. Es nutzt keine Systemrechte.

### Stufe 2 – Programm starten

1. Starten Sie das Fensterprogramm:

   ```bash
   ./start.sh --gui
   ```

2. Falls kein Fenster möglich ist, starten Sie das einfache Zahlenmenü:

   ```bash
   ./start.sh --menu
   ```

3. Lesen Sie jede Vorschau vollständig. Schreibende Dateiaktionen bleiben gesperrt.

### Stufe 3 – Hilfe bei einem Problem

1. Zeigen Sie eine bereinigte Diagnose an:

   ```bash
   ./start.sh --diagnostics
   ```

2. Für eine gut weitergebbare strukturierte Ausgabe verwenden Sie:

   ```bash
   ./start.sh --diagnostics-json
   ```

3. Beide Befehle zeigen nur Text an. Sie schreiben keine Datei und nutzen kein Netz.

## Voraussetzungen und Abhängigkeiten

| Benötigt | Wofür | Wo festgelegt |
| --- | --- | --- |
| Ubuntu oder Kubuntu auf einem Rechner mit 64-Bit-Linux | Zielsystem | Paket- und Plattformprüfung |
| Python ab 3.10 und vor 3.15 | lokale Ausführung | `start.sh` |
| Python-Modul für lokale Umgebungen | getrennte Projektumgebung | Systempaket der Linux-Verteilung |
| PySide6 genau in Version 6.11.2 | Fenster und Bedienelemente | `requirements-gui.txt` |
| eine grafische Sitzung | Fensterprogramm | Linux-Arbeitsfläche |

Nur PySide6 ist eine direkte Python-Abhängigkeit. `start.sh` installiert niemals mit Systemrechten und nie unbemerkt. Ist ein geprüftes Paketverzeichnis `wheelhouse/` vorhanden, erfolgt die Einrichtung ohne Netz. Andernfalls wird vor dem möglichen Herunterladen ausdrücklich gefragt.

## Was bereits funktioniert

- sichere Prüfung von Plattform, Pfaden und symbolischen Verweisen;
- nur lesendes Erfassen, Suchen und Sortieren von Dateien;
- Vorschauen für Papierkorb, Kopieren und Verschieben innerhalb derselben Wurzel;
- gemeinsamer Programmkern für Fenster und Zahlenmenü;
- bereinigte Diagnose als Text oder strukturierte Ausgabe;
- automatische Prüfungen für Tastatur, Vergrößerung, Abstürze, knappen Speicherplatz, Rechtefehler und gleichzeitige Zugriffe;
- tragbares Paket mit Inhaltsliste und Prüfsummen.

## Was bewusst noch nicht funktioniert

1. **Zweiter Rechner:** Die echte Prüfung auf einem weiteren Zielgerät fehlt.
2. **Kopieren und Verschieben:** Die abschließende verständliche Bedienprüfung fehlt; der normale Programmweg bleibt gesperrt.
3. **Diagnose-Datei:** Die abschließende verständliche Bedienprüfung fehlt; die Funktion bleibt im normalen Programmweg gesperrt.

Die genaue Reihenfolge steht in [`todo.txt`](todo.txt). Der aktuelle Arbeitsblock steht in [`docs/CURRENT_ITERATION.md`](docs/CURRENT_ITERATION.md).

## Befehle in einfacher Sprache

| Vollständiger Befehl | Wirkung |
| --- | --- |
| `./start.sh --help` | zeigt alle angebotenen Startarten |
| `./start.sh --check` | prüft die lokale Umgebung, ohne sie zu verändern |
| `./start.sh --setup` | richtet die lokale Umgebung nach Rückfrage ein |
| `./start.sh --gui` | öffnet das Fensterprogramm |
| `./start.sh --menu` | öffnet das Zahlenmenü im Terminal |
| `./start.sh --preflight` | prüft Rechner und Arbeitsfläche nur lesend |
| `./start.sh --diagnostics` | zeigt eine bereinigte Diagnose als Text |
| `./start.sh --diagnostics-json` | zeigt dieselbe Diagnose in einer festen Datenform |
| `./start.sh --second-device-evidence-json` | erstellt den Nachweis für die Prüfung auf einem zweiten Rechner |

`start.sh` ist der einzige offizielle Einstieg für Nutzer. Direkte Python-Aufrufe sind nur für Entwicklung und automatische Prüfung gedacht.

## Bildschirmfoto

Ja, ein Bildschirmfoto kann hier eingefügt werden. Es fehlt derzeit bewusst, weil nur ein echtes, bereinigtes Bild aus einer bestätigten Bedienprüfung gezeigt werden darf. Der vorgesehene Ort ist `docs/assets/screenshots/readme/`. Ein Entwurf muss unter `docs/assets/mockups/` liegen und deutlich mit **Entwurf – nicht das fertige Programm** beschriftet sein.

Vor der Aufnahme müssen persönliche Ordnernamen, Nutzernamen und Dateinamen entfernt werden. Ein Bildschirmfoto ersetzt keine Bedienprüfung.

## Projektaufbau

| Bereich | Inhalt |
| --- | --- |
| `src/` | eigentliche Programmlogik |
| `tests/` | automatische Prüfungen |
| `scripts/` | Entwicklungs- und Nachweiswerkzeuge |
| `docs/` | Entscheidungen, Regeln und Prüfnachweise |
| [`docs/README.md`](docs/README.md) | Verzeichnis aller Informationsdateien und ihres Standes |
| [`docs/REGRESSIONSMANIFEST.json`](docs/REGRESSIONSMANIFEST.json) | maschinenlesbare Zuordnung ähnlicher Fehler zu passenden Prüfungen |
| [`AGENTS.md`](AGENTS.md) | verbindliche Regeln für Menschen und Hilfsagenten |

## Entwicklungsverfahren

Jede Änderung folgt derselben kurzen Kette:

**verstehen → planen → einmal zusammenhängend ändern → passend prüfen → vollständig prüfen → Unterschied ansehen → abschließen**

Verbesserungen für Arbeitsaufwand und Codequalität sind bereits möglich und festgelegt:

- ähnliche Fehler werden über das Regressionsmanifest einer bestehenden Fehlerfamilie zugeordnet;
- zuerst läuft nur die kleinste passende Prüfung;
- die vollständige Prüfung läuft einmal am unveränderten Freigabestand;
- Dokumentation erhält einen eindeutigen Besitzer und einen festgelegten Aktualisierungsgrund;
- neue Hilfsschichten entstehen nur bei mindestens zwei echten Nutzern oder einer klaren Sicherheitsgrenze;
- nach zwei erfolglosen Reparaturversuchen wird neu geplant statt weiterprobiert.

Die Einzelheiten stehen in der [Regressionsmatrix](docs/REGRESSION_MATRIX.md), im [Wartbarkeitsvertrag](docs/MAINTENANCE.md) und in den [Arbeitsregeln](AGENTS.md).

## Verlässliche Informationsquellen

1. die aktuelle ausdrücklich freigegebene Aufgabe;
2. [`AGENTS.md`](AGENTS.md);
3. angenommene Architekturentscheidungen unter `docs/adr/`;
4. die eingefrorene Ausgangsliste `PROVOWARE_TODO_INPUT_POOL0.md`;
5. [`todo.txt`](todo.txt) für offene Arbeit;
6. diese Übersicht.

Bei einem Widerspruch gilt die kleinere und sicherere Auslegung. Schreibende Dateiwege bleiben bis zu einer eigenen Freigabe gesperrt.
