# PROVOWARE – Current Iteration

## I30 – Diagnose-Export Application-Autorisierung

**Status:** 🟢 AUTOMATISCH PASS · FREEZE-BEREIT
**Fortschritt:** `██████████ 100 %`

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

1. 🟢 I30 Evidence an RC `29d4b3e8effbe6f43fb6c64aa7043dca2fa04c64` binden und mergen.
2. 🔵 danach I31 ausschließlich als gegateten GUI-/CLI-Adapter-Prüfmodus implementieren; Registry bleibt OPEN.
3. 🔒 READY erst nach vollständiger Auto-Evidence des sichtbaren Schreibworkflows und genau einer finalen Human-Gesamtabnahme.
