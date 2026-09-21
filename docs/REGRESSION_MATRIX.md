# PROVOWARE – Regressionsmatrix

## Ziel

Schnellere Entwicklung ohne schwächere Abnahme.

Prinzip:

**gezielt zuerst → vollständig vor Merge**

Die Matrix reduziert unnötige lokale/agentische Testläufe. Der zentrale PR-Gate führt weiterhin die vollständige Testsuite aus.

## Änderungsart → gezielter Erstlauf

| Änderung | Erstlauf |
| --- | --- |
| Pfad-/Symlink-Sicherheit | `tests/test_path_policy.py` + betroffene Fachtests |
| Inventar | `tests/test_inventory.py` |
| Preview-Modell | `tests/test_preview_model.py` |
| Recovery-Vertrag | `tests/test_recovery_contract.py` |
| Registry/Application-Core | `tests/test_i11_shell.py` + betroffener Use-Case-Test |
| I16 Preview-Application | `tests/test_i16_preview_application.py` |
| Theme/Fokus/Skalierung | `tests/test_accessibility_evidence.py` |
| I17-D Auto-Evidence | `tests/test_i17_auto_evidence.py` |
| Diagnostic Export Preflight | `tests/test_diagnostic_export_plan.py` + Read-only-Lock |
| I18 Inventar-Komfort | `tests/test_inventory_view.py` |
| Core-Diagnostik | `tests/test_core_diagnostics.py` + `python3 scripts/core_diagnostics.py` |
| Read-only-Lock | `tests/test_read_only_guard.py` + `python3 scripts/read_only_guard.py` |
| I27 Diagnostic Writer Guard | `tests/test_diagnostic_writer_guard.py` + `tests/test_read_only_guard.py` + Preview-Reversibilitätsregression |
| I28 Diagnose-Writer Testlab | `tests/test_diagnostic_export_writer.py` + I27 Guard + Read-only-Lock; Race/Crash/ENOSPC/PermissionError/Hash/No-clobber |
| I29 Diagnose-Export Authorization Decision | Doku-/Contract-Gate; keine Produktimplementierung |
| I30 Diagnose-Export Autorisierung | `tests/test_i30_diagnostic_export_authorization.py` + Registry + I28 Writer-Regressionspfad |
| I31 Diagnose-Export Adapter-Prüfmodus | `tests/test_i31_diagnostic_export_adapters.py` + `scripts/i31_auto_evidence.py --offscreen --auto-only`; Human-Gate nur final |
| I20 Diagnose-Observability | `tests/test_diagnostics.py` + `python3 scripts/diagnostic_snapshot.py --json` |
| I21 Same-Root Copy/Move Preview | `tests/test_i21_same_root_preview.py` + `python3 scripts/core_diagnostics.py` |
| I25 Transfer-Preview Adapter | `tests/test_i25_transfer_adapters.py` + I21 + Read-only-Lock + `scripts/i25_auto_evidence.py --offscreen --auto-only`; Human-Gate nur final |
| CLI/GUI-Adapter | Paritäts-/Use-Case-Test + Accessibility-Evidence |
| Doku/Prozess | `scripts/repo_quality.py` + `scripts/info_text_guard.py` |

## Vollgate vor Merge

Unabhängig vom Erstlauf:

```bash
python3 scripts/repo_quality.py
python3 scripts/read_only_guard.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/core_diagnostics.py
python3 scripts/diagnostic_snapshot.py --json
./start.sh --preflight
./start.sh --json
```

Im PR übernimmt GitHub Actions diesen Vollgate.

## Regressionsebenen

1. **L0 – Contract:** Syntax, Pflichtstruktur, Workflow-Pinning, TODO-Schema.
2. **L1 – Targeted:** nur direkt betroffene Tests.
3. **L2 – Cross-Core:** angrenzende Sicherheits-/Paritätstests.
4. **L3 – Full Suite:** alle Tests vor Merge.
5. **L4 – Real Evidence:** nur für sichtbare GUI-/Hardware-/Zielsystemeigenschaften.

## Management-Regeln

- Ein Bug erhält einen Regressionstest oder eine reproduzierbare Evidence-Anweisung.
- Tests werden nicht abgeschwächt, um einen Patch grün zu bekommen.
- Reale GUI-Evidence darf nicht durch Headless-CI ersetzt werden.
- Nur geänderte Verantwortung wird gezielt zuerst getestet.
- Vor Merge wird immer L3 ausgeführt.
- Nach Merge muss der Main-Workflow grün sein.
- Testfehler, Produktfehler und Infrastrukturfehler werden getrennt dokumentiert.

## Effizienzgewinn

Damit bleibt der schnelle Entwicklungszyklus:

```text
READ
→ kleinster Patch
→ L1 targeted
→ L2 nur wenn relevant
→ Doku/Evidence
→ PR
→ L3 Full Suite
→ Diff
→ Merge
→ Post-Merge
```

Kein absichtlich roter Push und keine fachfremden Tests in frühen Schleifen.
\n| I32 Portable ZIP | `tests/test_i32_portable_package.py` + `scripts/build_portable_zip.py`; Reproducibility/Manifest/Fremdpfad/Offline-Check |\n