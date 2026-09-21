# EV-20260922-009 – I31 Diagnose-Export Adapter-Evidence

## Evidence-ID

EV-20260922-009

## Datum/Uhrzeit

2026-09-22 · Europe/Berlin

## RC/Fingerprint

`2a90de7a45ca900d9cc203f4d6db4c4ee806e6c3`

Basis: `1f27ed639f2f364b188816bbd9f3f78deb028408`

## Ziel

GUI und CLI ausschließlich im gegateten Prüfmodus an denselben I26 → I30 → I28-Pfad anbinden und alle technisch reproduzierbaren Eigenschaften automatisiert belegen.

## Automatische Nachweise

GitHub Actions:

- `repo-quality` Run `35665963046`: **PASS**
- `i31-export-evidence` Run `35665963214`: **PASS**
- `i25-gui-evidence` Run `35665963158`: **PASS**

## I31 Auto-Matrix

Belegt:

- GUI bei 100 / 150 / 200 %;
- sichtbare Kernwidgets;
- Tastaturfokus und Tab-Bewegung;
- Bestätigung 1;
- Bestätigung 2;
- finaler Schreibbutton nicht als Default-Fokus;
- GUI Cancel nach Stage 1 → keine Datei;
- GUI PASS → exakt eine neue Testdatei;
- bestehendes Ziel → BLOCKED und unverändert;
- Failure-Darstellung nach Was ist passiert / Was bedeutet das / Was kann ich tun;
- CLI PASS → exakt eine neue Testdatei;
- CLI Cancel → keine Datei;
- identische Doppelbestätigungsformulierungen;
- normaler Registry-/Produktweg bleibt geschlossen;
- ausschließlich synthetische Diagnosedaten;
- ausschließlich temporäre Test-Zielordner.

## CI-Artefakt

- Name: `i31-evidence-1c231be2244ee371689c1db79f743e608cb6a9d2`
- Größe: 639625 Byte
- SHA-256: `c0c305f5fe6548a11551a136aae79353df5ebed7ad57f64f92086a03e51f552c`
- Aufbewahrung: 14 Tage

Das Artefakt enthält Screenshots sowie JSON/TXT-Evidence.

## Sicherheitsgrenze

Weiterhin:

- `diagnostics.export_local = OPEN`;
- `gui_available=False`;
- `cli_available=False`;
- kein Export im normalen `--gui`-/`--menu`-Pfad;
- keine echten Nutzdaten als Evidence-Fixture;
- kein Upload/Netzwerk;
- kein Overwrite;
- kein allgemeiner Executor.

## Offener Human-Anteil

Technisch verbleibt nichts weiter zu testen.

Offen ist ausschließlich eine finale Wahrnehmungsfrage im realen Prüfmodus:

> War jederzeit klar, dass nur synthetische Testdaten verwendet werden, wann tatsächlich eine Datei erstellt wird, wo sie landet und wie man vorher sicher abbricht?

Bis zu diesem PASS bleibt die Registry OPEN.

## Status

**AUTO PASS · HUMAN OPEN**
