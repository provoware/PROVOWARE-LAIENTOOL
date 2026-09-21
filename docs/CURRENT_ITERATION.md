# PROVOWARE – Current Iteration

## I29 – Diagnose-Export Autorisierungs-/Adapter-Decision

**Status:** 🟢 DECISION FROZEN · KEINE IMPLEMENTIERUNG
**Fortschritt:** `██████████ 100 %`

## Entscheidung

Ein späterer lokaler Diagnoseexport benötigt einen gemeinsamen Application-Use-Case mit:

- I26 ExportPreparation;
- unveränderlichem Plan-/Payload-Fingerprint;
- Bestätigung 1 für die Exportabsicht;
- unveränderter finaler Zusammenfassung;
- Bestätigung 2 für den tatsächlichen Commit;
- erst danach intern autorisiertem I28-Writer-Aufruf.

Adapter dürfen niemals selbst `write_enabled=True` setzen oder den Writer direkt aufrufen.

## Registry

Spätere ID:

`diagnostics.export_local`

Vor Implementierung wird eine neue Sicherheitsklasse benötigt:

`explicit-write-confirmation`

I29 ändert die Registry selbst noch nicht.

## Parität

GUI und CLI müssen identisch abbilden:

- Format/Ziel/Dateiname;
- ExportPlan/Fingerprint;
- beide Bestätigungen;
- Cancel;
- Fehlerklasse;
- Erfolg/Abschluss.

## Abbruch

Jeder Abbruch vor Writer-Aufruf bleibt seiteneffektfrei. Änderungen nach Bestätigung 1 verwerfen die Autorisierung und erzwingen beide Bestätigungen erneut.

## Weiter gesperrt

- Registry-Erweiterung;
- Application-Autorisierungscode;
- sichtbarer GUI-/CLI-Export;
- produktiv erreichbarer Diagnosewrite;
- allgemeiner Executor;
- Upload/Netzwerk;
- andere Schreibpfade.

## Nächste drei Schritte

1. 🟢 I29 als reines Decision Gate automatisch gegen Repository-/Doku-Verträge prüfen und mergen.
2. 🔵 I30: ausschließlich Application-Autorisierungsmodell + Registry-Sicherheitsklasse/OPEN-Eintrag implementieren und vollständig automatisch testen; noch keine sichtbaren Adapter.
3. 🔒 erst danach GUI/CLI-Adapter als eigenen Block entwickeln und vor READY technische Auto-Evidence + genau eine Human-Gesamtabnahme verlangen.
