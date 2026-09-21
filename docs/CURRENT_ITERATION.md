# PROVOWARE – Current Iteration

## I30 – Diagnose-Export Application-Autorisierung

**Status:** 🟨 RC · AUTOMATISCHE GATES LAUFEN
**Fortschritt:** `████████░░ 80 %`

## Implementiert

- neue Registry-Sicherheitsklasse `explicit-write-confirmation`;
- `diagnostics.export_local` ausschließlich `OPEN`, ohne GUI/CLI-Verfügbarkeit;
- deterministischer Preparation-Fingerprint;
- zweistufige Bestätigung;
- Stale-/Manipulationssperre;
- Cancel-Semantik;
- sessiongebundener immutable `AuthorizedExportRequest`;
- One-shot Writer-Aufruf.

## Sicherheitsgrenze

Adapter können weiterhin keinen Diagnoseexport auslösen. Nur der nichtvisuelle Autorisierungs-Core darf intern aus dem unveränderten Plan ein `write_enabled=True` für exakt einen I28-Aufruf erzeugen.

## Automatische Exit-Gates

1. I30 targeted tests.
2. Registry-Vertrag.
3. I28 Writer-Regression.
4. I27 Writer-Guard.
5. globaler Read-only-Lock.
6. Full Suite.
7. Core Diagnostic/Preflight.
8. finaler Diff ohne GUI/CLI-Code.

## Weiter gesperrt

- GUI-/CLI-Export;
- Registry READY;
- Startmodus;
- automatischer Export;
- allgemeiner Executor;
- Upload/Netzwerk;
- andere Schreibpfade.

## Nächste drei Schritte

1. 🟨 I30 RC vollständig automatisch prüfen und Evidence binden.
2. 🔵 bei Grün mergen.
3. 🔒 danach I31 als gegateten GUI-/CLI-Adapter-Prüfmodus planen; READY weiterhin erst nach Auto-Evidence + einer finalen Human-Abnahme.
