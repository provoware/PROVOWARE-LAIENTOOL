# I31 – Diagnose-Export GUI-/CLI-Prüfmodus

## Status

**GUI- und CLI-Adapter implementiert, aber ausschließlich als gegateter Prüfmodus. Registry bleibt OPEN.**

Der normale `--gui`- und `--menu`-Weg zeigt `diagnostics.export_local` weiterhin nicht.

## Gemeinsamer Pfad

```text
synthetischer DiagnosticReport
→ I26 ExportPreparation
→ I30 Fingerprint / Stage 1 / Stage 2
→ I28 one-shot Writer
→ gemeinsames AdapterResult
→ GUI oder CLI Darstellung
```

GUI und CLI besitzen keine eigene Autorisierungs- oder Writerlogik.

## Prüfstarts

```bash
./start.sh --i31-evidence
./start.sh --i31-offscreen
./start.sh --i31-cli-evidence
```

- `--i31-offscreen`: nur automatische Evidence;
- `--i31-evidence`: automatische Evidence, danach höchstens eine finale Human-Gesamtabnahme;
- `--i31-cli-evidence`: interaktiver Zahlenmenü-Prüfmodus.

Alle I31-Prüfstarts verwenden ausschließlich synthetische Diagnosedaten und temporäre Testordner.

## GUI-Vertrag

Der Prüfmodus zeigt:

- Format;
- synthetischen Test-Zielordner;
- Exportvorschau;
- Bestätigung 1: **Weiter zur finalen Bestätigung**;
- unveränderte finale Zusammenfassung;
- Bestätigung 2: **Diagnosedatei jetzt neu erstellen**;
- Abbrechen;
- Ergebnis/Fehler nach Laientextvertrag.

Der finale Schreibbutton:

- ist vor Stage 1 deaktiviert;
- besitzt keinen Default-Fokus;
- wird erst nach Stage 1 aktiviert;
- kann nur den gemeinsamen I30-Pfad auslösen.

## CLI-Vertrag

Nummerierter Ablauf:

1. Klartext oder JSON;
2. Vorschau;
3. `1 Weiter zur finalen Bestätigung / 0 Abbrechen`;
4. finale Zusammenfassung;
5. `1 Diagnosedatei jetzt neu erstellen / 0 Abbrechen`;
6. gemeinsames Ergebnis.

Keine Shell-Globs, kein freier Bestätigungstext.

## Automatische Evidence

I31-AUTO prüft:

- GUI bei 100 / 150 / 200 %;
- sichtbare Kernwidgets;
- Tab-Fokusbewegung;
- Stage-1- und Stage-2-Freigabe;
- finaler Schreibbutton nicht als Default-Fokus;
- Cancel nach Stage 1 → keine Datei;
- GUI PASS → exakt eine neue Datei;
- bestehendes Ziel → BLOCKED und unverändert;
- Fehlertext: Was ist passiert / Was bedeutet das / Was kann ich tun;
- CLI PASS → exakt eine neue Datei;
- CLI Cancel → keine Datei;
- beide Bestätigungsformulierungen im CLI;
- ausschließlich synthetische Daten/temporäre Zielordner;
- Screenshots + JSON/TXT als CI-Artefakt.

## Registry

`diagnostics.export_local` bleibt:

- `status=OPEN`;
- `gui_available=False`;
- `cli_available=False`.

Der Prüfmodus ist bewusst kein normaler Registry-Adapter.

## Human-Gate

Erst nach vollständig grünem Auto-Gate bleibt genau eine Wahrnehmungsfrage:

> War jederzeit klar, dass nur synthetische Testdaten verwendet werden, wann tatsächlich eine Datei erstellt wird, wo sie landet und wie man vorher sicher abbricht?

Bis zu einem realen PASS bleibt der normale Produktweg gesperrt.

## Nicht-Ziele

- kein Registry READY;
- kein Export im normalen GUI-/Menüweg;
- keine echten Nutzdaten als Evidence-Fixture;
- kein Upload;
- kein allgemeiner Executor;
- kein Overwrite;
- keine persistente Autorisierung.
