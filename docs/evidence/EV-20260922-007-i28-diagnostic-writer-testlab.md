# EV-20260922-007 – I28 Diagnose-Writer Testlab

## Evidence-ID

EV-20260922-007

## Datum/Uhrzeit

2026-09-22 · Europe/Berlin

## RC/Fingerprint

`be2a7ce984dd4231595c93e0c994b7f0b6b14376`

Basis: `af68d4fb6e2fb9bf652f36ef5e34cb373e0c8f64`

## Ziel

Den dedizierten Diagnose-Writer nach I24/I26/I27 ausschließlich im automatischen Testlabor gegen No-clobber-, Failure-, Race- und Crash-Anforderungen prüfen, ohne GUI/CLI/Registry freizugeben.

## Automatische Nachweise

GitHub Actions:

- `repo-quality` Run `35662196737`: **PASS**
- `i25-gui-evidence` Run `35662196672`: **PASS**

Der vollständige Repository-Gate bestätigte:

- Repository-Contract;
- gehärteten I27 Writer-Guard;
- globalen Read-only-Lock;
- vollständige Unit-/Integrationssuite;
- Core Diagnostic;
- Diagnose-Snapshot;
- Preflight Klartext/JSON;
- Info-Text-Impact.

## I28 Failure-/Safety-Matrix

Automatisch abgedeckt:

- explizite Write-Autorisierung erforderlich;
- JSON und Text;
- Unicode und Leerzeichen im Zielpfad;
- vorhandenes Ziel bleibt unverändert;
- Hash-/Größenabweichung blockiert vor Write;
- Symlink-/unsicherer Zielvertrag blockiert;
- ENOSPC klassifiziert;
- PermissionError klassifiziert;
- Ziel entsteht direkt vor Commit;
- zwei parallele Läufe mit gleichem Ziel: genau ein Gewinner;
- Crash nach Partial-Create: kein finaler Schein-Erfolg;
- Crash vor Commit: kein finaler Schein-Erfolg;
- Partial-Namenskollision: kein Retry und keine fremde Datei löschen;
- Cleanup-Fehler nach Publish wird als Partial-Rest gemeldet;
- no-clobber Publish ausschließlich über Hardlink;
- Directory-fsync vor/ nach Partial-Unlink.

## Sicherheitsgrenze

Weiterhin **nicht vorhanden**:

- GUI-/CLI-Exportadapter;
- Registry-READY;
- automatischer Nutzerexport;
- allgemeiner Executor;
- Overwrite-Fallback;
- Netzwerk;
- Rechteausweitung.

I26 erzeugt standardmäßig weiterhin `write_enabled=False`.

## Status

**PASS** – I28 ist als Testlab-Baustein freeze-bereit. Produktive Erreichbarkeit bleibt gesperrt.
