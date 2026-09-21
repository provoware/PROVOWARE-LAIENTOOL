# PROVOWARE – Current Iteration

## I34 – Plugin-Grenze

**Status:** 🟨 RC · AUTOMATISCHE GATES LAUFEN
**Fortschritt:** `████████░░ 80 %`

## A – PLAN

B09 erhält einen stabilen data-only Manifest-/Capability-Vertrag ohne Plugin-Runtime.

## B – DELTA

NONE. I25/I31 Human-Gates und B01-Zweitgerät bleiben bewusst geparkt.

## Implementiert

- immutable `PluginManifest`;
- Plugin-API-Version 1;
- ausschließlich `DISABLED`;
- Auto-Install/Auto-Enable/Netzwerk/Entry-Point gesperrt;
- Capability-Allowlist aus bestehender Registry;
- nur `READY` + `read-only` genehmigungsfähig;
- statischer Plugin-Boundary-Guard in CI.

## Exit-Gates

1. Manifest-Validierung PASS.
2. OPEN-/Write-/Unknown-Capabilities BLOCKED.
3. Auto-Install/Enable/Network/Entrypoint BLOCKED.
4. dynamische Loader-Marker durch Guard BLOCKED.
5. Full Suite PASS.
6. Repository-/Read-only-/Package-/GUI-Regressionsgates PASS.

## Nächste drei Schritte

1. I34 vollständig automatisch prüfen und Evidence binden.
2. Bei Grün mergen.
3. Danach nächsten automatisierbaren Security-/Release-Block wählen; keine Human-Einzeltests.
