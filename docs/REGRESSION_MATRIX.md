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
| I17 Evidence-Helfer | `tests/test_i17_target_evidence.py` |
| CLI/GUI-Adapter | Paritäts-/Use-Case-Test + Accessibility-Evidence |
| Doku/Prozess | `scripts/repo_quality.py` + `scripts/info_text_guard.py` |

## Vollgate vor Merge

Unabhängig vom Erstlauf:

```bash
python3 scripts/repo_quality.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 start.py
python3 start.py --json
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
