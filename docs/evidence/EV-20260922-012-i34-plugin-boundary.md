# EV-20260922-012 – I34 Plugin-Grenze

## Evidence-ID

EV-20260922-012

## Datum/Uhrzeit

2026-09-22 · Europe/Berlin

## RC/Fingerprint

`61c83eb21cfede0510eb4d78726726b5ccae128d`

Basis: `39262387a6adac5e42907dfe331f1fe5fb7ef183`

## Ziel

B09 als reine Daten-/Capability-Grenze automatisiert absichern, ohne einen ausführbaren Plugin-Loader, Installer oder Netzwerkpfad einzuführen.

## Automatische Nachweise

GitHub Actions:

- `repo-quality` Run `35668658598`: **PASS**
- `i25-gui-evidence` Run `35668658426`: **PASS**

Der Repository-Gate bestätigte:

- Repository-Contract;
- Plugin-Boundary-Guard;
- globalen Read-only-Lock;
- vollständige Unit-/Integrationssuite;
- Core Diagnostic;
- Diagnose-Snapshot;
- Preflight Klartext/JSON;
- Info-Text-Impact.

## I34 Sicherheitsmatrix

Automatisch belegt:

- Plugin-Manifest bleibt immutable/data-only;
- Status ausschließlich `DISABLED`;
- nur bestehende `READY` + `read-only` Use-Cases genehmigungsfähig;
- OPEN-/Write-/Unknown-Capabilities blockiert;
- doppelte Capability-Anforderungen blockiert;
- Auto-Install blockiert;
- Auto-Enable blockiert;
- Netzwerkbedarf blockiert;
- Entry-Point blockiert;
- `__import__` blockiert;
- `import_module`, `spec_from_file_location`, `exec_module`, `entry_points` blockiert;
- typische Plugin-Loader-Dateien und `plugins/`-Runtime-Verzeichnisse blockiert.

## CI-Fund und Reparatur

Der erste Guard-Stand blockierte pauschal `importlib.util` und damit den bestehenden read-only Preflight-Aufruf `importlib.util.find_spec("PySide6")`.

Das war ein **Guard-Fehlpositiv**, kein Produktfehler.

Die Reparatur:

- erlaubt statischen `importlib.util`-Import;
- erlaubt `find_spec()` zur Capability-Erkennung;
- blockiert weiterhin die tatsächlichen dynamischen Ladeoperationen;
- enthält dafür einen eigenen Regressionstest.

## Sicherheitsgrenze

Weiterhin nicht vorhanden:

- Plugin-Loader;
- Plugin-Installer/Downloader;
- Plugin-Verzeichnis-Scanner;
- Auto-Aktivierung;
- Plugin-Netzwerkzugriff;
- Plugin-Persistenz;
- Sandbox-/Isolation-Versprechen.

## Status

**PASS** – I34 ist freeze-bereit.
