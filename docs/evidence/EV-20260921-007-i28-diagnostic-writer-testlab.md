# EV-20260921-007 – I28 Diagnostic Export Writer Testlab

## Evidence-ID

EV-20260921-007

## Datum/Uhrzeit

2026-09-22 · Europe/Berlin

## Geprüfter RC

`91cb3268642e6ae5c784df5601115045432ad192`

## Ziel

Den dedizierten Diagnose-Writer ausschließlich im automatischen Testlabor gegen I24/I26/I27 prüfen, ohne GUI-/CLI-/Registry-Pfad zu öffnen.

## Sicherheitsaufbau

- I26-ExportPlan bleibt standardmäßig `write_enabled=False`;
- keine Produktfunktion erzeugt `write_enabled=True`;
- Writer liegt ausschließlich in `src/provoware_laientool/diagnostic_export.py`;
- globaler Read-only-Lock delegiert nur diesen exakten Pfad an den I27-Spezialguard;
- Zielordner wird über `O_DIRECTORY|O_NOFOLLOW` geöffnet;
- Device/Inode werden gegen den geprüften Pfad abgeglichen;
- Partial-Create, Publish und Cleanup laufen relativ zum selben `target_dir_fd`;
- Publish erfolgt no-clobber über Hardlink;
- kein `rename`, `replace`, Overwrite, Auto-Rename oder Retry.

## RC-Befund

Der erste RC stoppte korrekt am statischen Guard:

```text
os.write nur auf exklusiv erzeugtem Partial-FD zulässig
```

Ursache war kein Writer-Fehler, sondern die fehlende Guard-Rollenklassifikation für den Variablennamen `partial_fd`.

Genau eine gezielte Korrektur erweiterte die semantische Rolle um `*_partial_fd`. Der Sicherheitsumfang wurde nicht vergrößert.

## Automatische Prüfungen

Nach der Korrektur:

- Repository-Contract: PASS;
- I27 Writer-Guard: PASS;
- globaler Read-only-Lock: PASS;
- vollständige Unit-/Integrationssuite: PASS;
- I28 Writer-Failure-/Race-Matrix: PASS;
- Core Diagnostic: PASS;
- Diagnostic Snapshot: PASS;
- read-only Preflight Text/JSON: PASS;
- Info-Text-Impact: PASS;
- I25-GUI-Auto-Evidence: PASS;
- I25-Evidence-Artefakt: erzeugt.

## Failure-/Race-Abdeckung

- nicht autorisierter I26-Plan blockiert;
- erfolgreicher Export;
- Dateirechte ohne Gruppen-/Other-Zugriff;
- vorhandenes finales Ziel bleibt unverändert;
- Payload-Größen-/Hashabweichung blockiert;
- manipulierte Finalpfadbindung blockiert;
- Symlink-Zielordner blockiert;
- Partial-Kollision ohne Retry;
- ENOSPC;
- PermissionError;
- Crash vor Publish hinterlässt nur erkennbare Partial-Datei;
- zwei parallele Writer auf denselben Namen: genau ein Gewinner;
- keine produktive Erzeugung von `write_enabled=True`.

## Status

**PASS**

## Bekannte Grenze

I28 beweist den Writer-Kern im automatischen Testlabor. Es existiert weiterhin kein Nutzerpfad und keine produktive Schreibautorisierung. Eine spätere Freigabe benötigt einen separaten Autorisierungs-/Adapter-Vertrag.
