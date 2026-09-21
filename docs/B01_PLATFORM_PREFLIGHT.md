# B01-A – Zielplattform, Capability-Erkennung und read-only Start-Preflight

**Status:** implementiert, physische Zweitgeräte-Prüfung noch OPEN
**Bezug:** REQ-001, REQ-003, REQ-004; AQ-003, AQ-010, AQ-013, AQ-020

## Ziel

Der Start ermittelt die lokal vorhandenen Voraussetzungen selbst, validiert sie und wählt daraus den besten sicheren Startmodus. Portabilität wird durch **Erkennen und Nutzen vorhandener Fähigkeiten** erreicht, nicht durch stille Nachinstallation.

## Initiale Plattform-Baseline

- Ubuntu 24.04 LTS
- Kubuntu 24.04 LTS
- Linux
- Python >= 3.10

Andere Versionen bleiben `OPEN`, bis reale Evidence vorliegt.

## Automatisch ermittelte Aspekte

Der Preflight prüft read-only:

- Betriebssystem und Kernel;
- Distribution und Version;
- CPU-Architektur;
- Python-Version;
- Runtime-Quelle: bundled / venv / system;
- Desktop und X11/Wayland-Sitzung;
- lokale PySide6-Verfügbarkeit;
- Dateisystem-Encoding;
- Erreichbarkeit von Home;
- XDG-Downloads-Ziel bzw. Fallback `~/Downloads`;
- Lesbarkeit des Projektordners.

Keine vollständigen persönlichen Pfade werden für die Startentscheidung benötigt.

## Startprofil-Auflösung

Priorität ist deterministisch:

1. **bundled Runtime**, falls das Paket bereits mit eigener Runtime läuft;
2. vorhandene lokale virtuelle Umgebung;
3. vorhandenes System-Python;
4. niemals automatischer Download als Fallback.

Danach wird ein Profil gewählt:

- `gui-ready`: Kern + grafische Sitzung + PySide6 lokal verfügbar;
- `preflight-cli`: Kern geeignet, GUI-Komponente fehlt; sichere Diagnose bleibt nutzbar;
- `blocked-readonly`: wesentliche lokale Voraussetzung fehlt; nur Anzeige/Diagnose.

Die aktuelle B01-A-Implementierung startet noch keine produktive GUI. `gui-ready` bedeutet ausschließlich, dass die lokalen Voraussetzungen für den späteren GUI-Adapter vorhanden sind.

## Sicherheitsvertrag

Erlaubt sind lokale Lesezugriffe auf Runtime-/Systemmetadaten und XDG-Konfiguration.

Verboten sind:

- Dateiänderungen;
- Paketinstallation;
- Netzwerkzugriffe;
- sudo/Rechteausweitung;
- automatische Konfigurationsmigration;
- automatisches Nachladen fehlender GUI-Abhängigkeiten.

## Start

```bash
python3 start.py
python3 start.py --json
```

Exitcodes:

- `0`: sicher nutzbarer `gui-ready`- oder `preflight-cli`-Kern;
- `3`: `blocked-readonly` / Voraussetzungen OPEN;
- `2`: ungültige Option.

## Portabilitätsregel

Ein transportiertes Paket darf auf einer anderen Maschine zunächst nur **inventarisieren und entscheiden**. Erst wenn die dort vorhandenen Voraussetzungen verifiziert sind, wird ein verfügbarer Startpfad gewählt. Fehlende Komponenten werden erklärt, nicht heimlich installiert.

## Zweitgeräte-Evidence

Für die reale zweite Zielmaschine steht nun ein dependency-freier, read-only Prüfweg bereit:

```bash
python3 scripts/second_device_evidence.py
python3 scripts/second_device_evidence.py --json
```

Der Runner übernimmt nur eine feste Menge unkritischer Capability-Felder und verwirft Pfade/Notizen. Details siehe `docs/B01_SECOND_DEVICE_EVIDENCE.md`.

## Noch offen

Die reale zweite Zielmaschine ist weiterhin nicht physisch durch Repository-Evidence belegt. Die Vorbereitung des Prüfwegs ist implementiert; der tatsächliche Lauf auf dem zweiten Gerät bleibt `OPEN`.
