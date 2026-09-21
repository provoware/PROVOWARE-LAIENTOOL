# PROVOWARE – Current Iteration

## I27 – Diagnostic Writer Guard / Branch-Hygiene

**Status:** 🟨 AUTOMATISCHER SICHERHEITS-RC
**Fortschritt:** `████████░░ 80 %`

## A – FESTER PLAN

I24 und I26 verlangen vor jedem echten Diagnose-Writer:

- exakten REOPEN nur für `src/provoware_laientool/diagnostic_export.py`;
- create-only / no-clobber;
- keinen Overwrite-Fallback;
- Writer-spezifischen statischen Guard;
- Race-/Crash-/Failure-Evidence erst im späteren Writer-Block.

I27 implementiert ausschließlich diesen Guard. Noch existiert kein `diagnostic_export.py`.

## B – DELTA AUS DER ALTBRANCH-ANALYSE

Vier Remote-Altbranches wurden gegen aktuellen `main` klassifiziert:

- `design/i24-diagnostic-export-writer`: vollständig superseded;
- `application/i21-transfer-preview`: alte Implementierung superseded durch heutigen I21/`transfer_application.py`;
- `domain/i12-preview-contract`: Architektur superseded, aber MOVE-Reversibilitätsinvariante gerettet;
- `security/i27-diagnostic-writer-guard`: Konzept relevant, alter Stand jedoch nicht ausreichend gehärtet; auf frischem Main transplantiert.

Details: `docs/evidence/EV-20260921-006-branch-hygiene-i27.md`.

## I27 Guard-Vertrag

Außerhalb des exakten Diagnose-Writers bleiben sämtliche Low-Level-Write-APIs blockiert.

Im Spezialwriter darf später nur ein statisch beweisbarer Pfad entstehen:

```text
partial_path
→ os.open(O_CREAT | O_EXCL | O_WRONLY/O_RDWR)
→ nachweislich daraus stammender Partial-FD
→ os.write/fsync
→ Hash/Größe zur Laufzeit verifizieren
→ os.link(partial_path, final_path, follow_symlinks=False)
→ eigene partial_path entfernen
```

Dynamische Flags, numerische Rohflags, `O_TRUNC`, `O_APPEND`, `O_TMPFILE`, freie FDs, freie Hardlinks, `rename`, `replace`, alternative Writer-/Escape-Bibliotheken und freie Deletes bleiben BLOCKED.

## Zusätzlich gerettete Preview-Invariante

`MOVE` und `TRASH` müssen zentral `reversible=True` besitzen. I21 erzeugte MOVE bereits korrekt; das Preview-Modell erzwingt dies nun ebenfalls fail-closed.

## Weiterhin gesperrt

- echter Diagnose-Writer;
- produktiver Diagnose-Dateiexport;
- allgemeiner Executor;
- Copy/Move-Write;
- Overwrite;
- Auto-Rename;
- Persistenz;
- Rechteausweitung;
- I25 READY ohne finale Human-Abnahme.

## Exit-Gates

1. I27-Guard-Tests PASS.
2. Read-only-Lock PASS.
3. Preview-Reversibilitätsregression PASS.
4. Repository-Contract PASS.
5. vollständige Unit-/Integrationssuite PASS.
6. Core Diagnostic PASS.
7. Diagnose/Preflight PASS.
8. finaler Diff ohne allgemeinen Write-Reopen.
9. Post-Merge-Main-Gate PASS.

## Nächste drei Schritte

1. 🟨 I27-RC automatisch vollständig prüfen und nur bei Grün mergen.
2. 🔵 danach den dedizierten Diagnose-Writer als separaten kleinen Testlab-Block planen/implementieren; zunächst ohne GUI/CLI-Adapter.
3. 🔒 Writer erst nach Race/Crash/ENOSPC/PermissionError/Hash-/No-clobber-Evidence fachlich freigeben; I25-Human-Gate bleibt unabhängig offen.
