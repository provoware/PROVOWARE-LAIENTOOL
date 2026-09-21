# I32 – Portable Offline-Paketierung

## Status

**Reproduzierbarer Linux-Paketbau implementiert. Physische Zweitgeräte-Evidence bleibt separat OPEN.**

## Ziel

Ein CI-erzeugtes ZIP soll aus einem beliebigen entpackten Fremdpfad starten können und für die gepinnte GUI-Abhängigkeit keinen PyPI-Zugriff benötigen.

## Paketinhalt

Das Portable-ZIP enthält:

- `start.sh` als kanonischen Starter;
- `PROVOWARE.desktop` als KDE-/Desktop-Klickstarter, der ausschließlich `start.sh --gui` delegiert;
- `start.py`;
- `requirements-gui.txt`;
- Runtime-Code unter `src/`;
- Runtime-/Evidence-Skripte unter `scripts/`;
- Nutz-/Technikdokumentation unter `docs/`, historische Evidence ausgenommen;
- lokales `wheelhouse/` mit den zu `PySide6==6.11.2` aufgelösten Wheels;
- `PACKAGE_MANIFEST.json` mit Commit, Plattform, Größen und SHA-256 jedes Paketbestandteils.

Entwicklungs-/CI-Dateien, Tests, lokale Venvs und historische Evidence werden nicht paketiert.

## Offline-first Bootstrap

`start.sh` prüft vor einer bestätigten PySide6-Installation:

1. existiert `wheelhouse/` mit Wheels?
2. falls ja: Installation ausschließlich mit `--no-index --find-links wheelhouse/`;
3. keinerlei Fallback auf PyPI, wenn das lokale Wheelhouse vorhanden aber unvollständig ist;
4. fehlt Wheelhouse: bisheriger ausdrücklich bestätigter PyPI-Weg bleibt verfügbar.

Es gibt weiterhin keine stille Installation.

## Reproduzierbarkeit

`scripts/build_portable_package.py`:

- verwendet nur Git-getrackte Runtime-/Dokudateien;
- sortiert Einträge deterministisch;
- setzt feste ZIP-Zeitstempel;
- erhält definierte Ausführbarkeitsbits;
- erzeugt Manifest und ZIP-SHA-256;
- bindet den Git-Commit in den Paketnamen und das Manifest.

Gleicher Commit + gleiche Wheel-Dateien sollen bytegleiches ZIP ergeben.

## Validierung

`scripts/validate_portable_package.py` prüft:

- genau eine Paketwurzel;
- keine absoluten/Traversal-Pfade;
- keine doppelten ZIP-Namen;
- Pflichtdateien;
- keine Tests/.github/.venv/build/dist;
- Manifest-Dateiliste exakt;
- Größe + SHA-256 jedes Eintrags;
- Wheelhouse-Flag und Wheel-Anzahl;
- Ausführbarkeit von `start.sh` und Desktop-Launcher;
- Launcher delegiert an `./start.sh --gui`;
- Extraktion in Fremdpfad mit Leerzeichen + Unicode;
- read-only Preflight aus dem entpackten Paket;
- Offline-`--setup` mit `PIP_NO_INDEX=1`;
- anschließendes `./start.sh --check`.

## CI

`.github/workflows/portable-package.yml` läuft gezielt bei Paketierungsänderungen:

```text
pinned requirements
→ pip download wheelhouse
→ deterministic ZIP
→ structural validation
→ extract to foreign path
→ offline setup
→ start.sh --check
→ ZIP + SHA256 + validation JSON artifact
```

## Plattformgrenze

Das in GitHub Actions erzeugte Wheelhouse ist zunächst ein **Linux-x86_64-Paket** für die CI-Plattform.

Das ist keine Behauptung über ARM oder andere Betriebssysteme. Weitere Architekturpakete brauchen eigene Builds/Evidence.

## Klickstart

`PROVOWARE.desktop` ist Bestandteil des ZIP und ruft nur den kanonischen `start.sh` auf.

Ob ein konkreter Dateimanager beim ersten Doppelklick zusätzlich „Ausführen/Vertrauen“ verlangt, ist Desktop-/Distributionseigenschaft und wird nicht als automatischer CI-PASS behauptet.

## Nicht-Ziele

- keine Systeminstallation;
- kein `sudo` im Nutzerstarter;
- kein apt im Nutzerstarter;
- kein AppImage/Snap/Flatpak;
- keine automatische Desktop-Registrierung;
- keine ARM-Freigabe;
- keine physische Zweitgeräte-Freigabe.

## Folgegate

Nach grünem I32-AUTO kann B07 für **CI-Linux-x86_64** als technisch reproduzierbar gelten. Die vollständige Portabilitätsfreigabe bleibt an die bereits offene B01-Zweitgeräte-Evidence gebunden.
