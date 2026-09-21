# EV-20260922-008 – I30 Diagnose-Export Autorisierung

## Evidence-ID

EV-20260922-008

## Datum/Uhrzeit

2026-09-22 · Europe/Berlin

## RC/Fingerprint

`29d4b3e8effbe6f43fb6c64aa7043dca2fa04c64`

Basis: `3036d5ae3338521d87b17d9ca54cebe2c2ebc8f1`

## Ziel

Den nichtvisuellen Diagnoseexport-Autorisierungsvertrag vollständig automatisch prüfen: Fingerprint-Bindung, Doppelbestätigung, Cancel, Stale-/Manipulationsschutz, Replay-Schutz und höchstens einen I28-Writer-Aufruf.

## Automatische Nachweise

GitHub Actions:

- `repo-quality` Run `35664516917`: **PASS**
- `i25-gui-evidence` Run `35664516811`: **PASS**

Der vollständige Repository-Gate bestätigte:

- Repository-Contract;
- Registry-Vertrag;
- I30 Targeted-Tests innerhalb der Full Suite;
- I28 Writer-Regression;
- I27 Spezialguard;
- globalen Read-only-Lock;
- Core Diagnostic;
- Diagnose-Snapshot;
- Preflight Klartext/JSON;
- Info-Text-Impact.

## I30 Sicherheitsmatrix

Automatisch abgedeckt:

- neue Sicherheitsklasse `explicit-write-confirmation`;
- `diagnostics.export_local` bleibt `OPEN`;
- keine GUI-/CLI-Verfügbarkeit;
- stabiler Preparation-Fingerprint;
- tatsächliche Payload muss zu Größe und SHA-256 des Plans passen;
- bereits `write_enabled=True` wird abgelehnt;
- Stage 2 ohne Stage 1 blockiert;
- Änderung nach Stage 1 verwirft den Bestätigungsfortschritt;
- Cancel vor und nach Stage 1 verhindert Writer-Aufruf;
- AuthorizedExportRequest ist sessiongebunden;
- fremde Sitzung blockiert;
- manipulierter Request blockiert;
- Writer erhält intern erst nach vollständiger Autorisierung `write_enabled=True`;
- Writer wird pro Sitzung höchstens einmal aufgerufen;
- Replay derselben Anfrage endet `BLOCKED_REPLAY`.

## Sicherheitsgrenze

Weiterhin nicht vorhanden:

- GUI-Diagnoseexport;
- CLI-Diagnoseexport;
- Registry-READY;
- Startmodus für Export;
- automatischer Export;
- Persistenz der Autorisierung;
- allgemeiner Executor;
- Upload/Netzwerk.

## Status

**PASS** – I30 ist freeze-bereit. Sichtbare Adapter bleiben ein separater Folgeblock.
