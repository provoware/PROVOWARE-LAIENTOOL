# PROVOWARE – Current Iteration

## I31 – Diagnose-Export GUI-/CLI-Prüfmodus

**Status:** 🟢 AUTO PASS · HUMAN-GATE OPEN
**Fortschritt:** `█████████▌ 95 %`

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

## AUTO-Ergebnis

Der technische I31-Pfad ist vollständig grün. Verbleibend ist ausschließlich die finale Human-Gesamtabnahme des sichtbaren Prüfmodus.

## Nächste drei Schritte

1. 🟢 I31 Evidence an RC `2a90de7a45ca900d9cc203f4d6db4c4ee806e6c3` binden und mergen.
2. 🟨 irgendwann genau eine Human-Gesamtabnahme über `./start.sh --i31-evidence`; keine weiteren Einzeltests.
3. 🔒 erst bei Human-PASS einen separaten Freeze-/READY-Decision-Block eröffnen; bis dahin bleibt der normale Produktweg gesperrt.
