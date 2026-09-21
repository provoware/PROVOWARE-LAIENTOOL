# PROVOWARE – Current Iteration

## I31 – Diagnose-Export GUI-/CLI-Prüfmodus

**Status:** 🟨 RC · AUTO-EVIDENCE AUSSTEHEND
**Fortschritt:** `████████░░ 80 %`

## Implementiert

- gemeinsamer GUI-/CLI-Adapter auf I26/I30/I28;
- normaler Produktweg bleibt unverändert;
- Registry `diagnostics.export_local` bleibt OPEN und in normalen Adaptern verborgen;
- drei kanonische Prüfstarts über `start.sh`;
- synthetische Diagnosedaten und temporäre Zielordner;
- automatisierte GUI-Evidence bei 100/150/200 %;
- Tastatur-/Fokusvertrag;
- Doppelbestätigung;
- Cancel;
- Failure-Darstellung;
- exakt eine Datei bei PASS;
- CI-Evidence-Artefakt.

## Sicherheitsgrenze

Der I31-Prüfmodus schreibt ausschließlich in eigens erzeugte temporäre Testordner. Keine echten Nutzdateien werden als Fixture verwendet. Der normale GUI-/CLI-Produktpfad kann den OPEN-Use-Case weiterhin nicht aufrufen.

## Exit-Gates

1. I31 Adaptertests.
2. I30 Autorisierungsregression.
3. I28 Writer-Regression.
4. I27 Spezialguard + globaler Read-only-Lock.
5. I31 offscreen 100/150/200.
6. GUI Cancel / PASS / BLOCKED.
7. CLI Cancel / PASS.
8. exakt eine neue Testdatei bei PASS.
9. Full Suite/Core Diagnostic/Preflight.
10. Registry bleibt OPEN.

## Danach

Bei komplett grünem AUTO-Stand bleibt ausschließlich eine finale Human-Gesamtabnahme. Vor deren PASS wird kein normaler Exportweg freigeschaltet.
