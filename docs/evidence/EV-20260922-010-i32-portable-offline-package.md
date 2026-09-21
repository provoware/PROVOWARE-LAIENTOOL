# EV-20260922-010 – I32 Portable Offline-Paket

## Evidence-ID

EV-20260922-010

## Datum/Uhrzeit

2026-09-22 · Europe/Berlin

## Source-Head

`bfee18f528e6a06feb9b3b43d1da9575578f2e89`

Basis: `40c0d073d1048aeade2c71298ca159fd1a0b3185`

## Ziel

B07 für die CI-Plattform Linux x86_64 technisch reproduzierbar machen: deterministisches Portable-ZIP, lokales PySide6-Wheelhouse, Manifest/Hashes, Fremdpfad-Test und Offline-Bootstrap über den kanonischen `start.sh`.

## Automatische Nachweise

GitHub Actions auf Source-Head `bfee18f528e6a06feb9b3b43d1da9575578f2e89`:

- `repo-quality` Run `35667459322`: **PASS**
- `portable-package` Run `35667459252`: **PASS**
- `i31-export-evidence` Run `35667459290`: **PASS**
- `i25-gui-evidence` Run `35667459360`: **PASS**

## Portable-Package-Gate

Automatisch bestanden:

- exakter PR-Source-Head ausgecheckt;
- gepinnte PySide6-Abhängigkeit als lokales Wheelhouse geladen;
- deterministisches ZIP erzeugt;
- `PACKAGE_MANIFEST.json` erzeugt;
- SHA-256/Größe sämtlicher Paketdateien geprüft;
- keine Tests, CI-Metadaten, lokale Venv oder Build-/Dist-Reste im Paket;
- keine unsicheren absoluten/Traversal-ZIP-Pfade;
- `start.sh` und `PROVOWARE.desktop` ausführbar markiert;
- Desktop-Launcher delegiert ausschließlich an `./start.sh --gui`;
- Paket in temporären Fremdpfad mit Leerzeichen + Unicode extrahiert;
- read-only Preflight aus dem extrahierten Paket gestartet;
- `PIP_NO_INDEX=1` gesetzt;
- `./start.sh --yes --setup` vollständig aus lokalem `wheelhouse/` erfolgreich;
- anschließendes `./start.sh --check` erfolgreich.

## CI-Artefakt

- Name: `portable-package-bfee18f528e6a06feb9b3b43d1da9575578f2e89`
- Größe des GitHub-Artefakts: 253885146 Byte
- Artefakt-Digest: `sha256:f20cfe0c08ebd0d72856ad2bc3a21854d38115da68483f71b6b6b590c139df0f`
- Aufbewahrung: 7 Tage

Das CI-Artefakt enthält das Portable-ZIP, die ZIP-SHA-256-Sidecar-Datei und `package-validation.json`.

## Reproduzierbarkeitskorrektur

Der erste Paketlauf war funktional grün, verwendete bei `pull_request` aber den temporären GitHub-Merge-Commit als Paketfingerprint.

Daraufhin wurde der Workflow gehärtet:

- Checkout explizit auf `github.event.pull_request.head.sha`;
- Artefaktname an denselben Source-Head gebunden.

Der hier dokumentierte PASS stammt ausschließlich aus dem korrigierten Lauf.

## Grenzen

Nicht automatisch belegt:

- physisches zweites Ubuntu-/Kubuntu-Gerät;
- ARM;
- Windows/macOS;
- Verhalten eines konkreten Dateimanagers beim ersten Vertrauensdialog für `.desktop`.

Diese Punkte werden nicht als PASS behauptet.

## Status

**PASS für CI-Linux-x86_64.**

B01 physische Zweitgeräte-Evidence bleibt **OPEN**.
