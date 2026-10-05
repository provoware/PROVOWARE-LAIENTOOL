# EV-20261001-016 – I44 Release-Gates teilweise bestanden

## Ergebnis

- **Gate-Scope-Regression:** PASS
- **Unabhängige Prüfung:** PASS
- **Vollständige RC-Abnahme:** PASS (262 Tests)
- **Qt-Laufzeit:** OPEN
- **I25-AUTO:** OPEN (nicht ausgeführt)
- **I25-HUMAN:** OPEN (nicht ausgeführt)
- **I44 GESAMT:** OPEN

Der Fix für den `.venv`-Scope des Repository-Gates ist vollständig geprüft.
Die Qt-Laufzeit bleibt nach zwei gezielten Systempaketzyklen offen, weil nun
`libEGL.so.1` fehlt. Daraus folgt weder ein Produktfehler noch eine
Copy-/Move-Freigabe.

## Nachweisdaten

- **Evidence-ID:** `EV-20261001-016`
- **Datum/Uhrzeit:** 2026-10-01 12:42 UTC
- **Commit/Fingerprint:** `0bbeec1ff5eda6365d53e27325548d99b6a5c6dd`
- **Betroffene Anforderungen/Entscheidung:** `REQ-001`, `REQ-004`, `REQ-006`,
  `REQ-BASELINE-1` und `ADR-0001`; kein zugeordneter CR
- **Testumgebung:** nicht-interaktive Linux-Shell; lokale `.venv`; Zugriff auf
  Ubuntu-Paketquellen
- **Status:** `OPEN` (drei Release-Gates PASS, Qt und I25 OPEN)

## Gate-Scope und Release Candidate

Der gezielte Regressionstest bestätigte, dass die lokale `.venv` nicht mehr
vom Text-Hygiene-Scan als Repository-Inhalt bewertet wird:

```bash
timeout 120s python3 -m unittest tests.test_repo_quality_documentation
```

- **Beobachtung:** 2 Tests bestanden.
- **Exit-Code:** `0`

Ein davon getrennter read-only Prüfer wiederholte den gezielten Test und
prüfte zusätzlich den Repository-Gate sowie den Diff:

```bash
timeout 120s python3 -m unittest -v tests.test_repo_quality_documentation
timeout 120s python3 scripts/repo_quality.py
git diff --check
```

- **Beobachtung:** 2 von 2 Tests, Repository-Gate und Diff-Prüfung bestanden.
- **Exit-Codes:** jeweils `0`

Die vollständige Ein-Befehl-Abnahme aus `docs/MAINTENANCE.md` wurde auf dem
oben genannten Release Candidate ausgeführt:

```bash
timeout 2m python3 scripts/repo_quality.py && timeout 2m python3 scripts/read_only_guard.py && timeout 5m env PYTHONPATH=src python3 -m unittest discover -s tests -v && timeout 2m python3 scripts/core_diagnostics.py && timeout 2m python3 scripts/diagnostic_snapshot.py --json && timeout 2m python3 start.py && timeout 2m python3 start.py --json
```

- **Erwartung:** Alle lokalen Release-Gates bestehen auf demselben RC.
- **Beobachtung:** Alle Teilbefehle bestanden; die Testsuite meldete 262
  bestandene Tests.
- **Exit-Code:** `0`
- **Artefaktbindung:** RC-SHA wie oben; keine dauerhaften Testartefakte

## Qt-Laufzeit – begrenzte Reparaturzyklen

### Zyklus 1 – `libGL.so.1`

**Zeit:** 2026-10-01 12:41:13–12:41:16 UTC

```bash
timeout 600s apt-get update && timeout 600s apt-get install -y --no-install-recommends libgl1
```

- **Beobachtung:** Exit-Code 0. Das externe mise-Repository antwortete beim
  Aktualisieren mit HTTP 403; die Ubuntu-Paketquellen blieben nutzbar und
  `libgl1` wurde erfolgreich installiert.
- **Exit-Code:** `0`

```bash
timeout 120s ./start.sh --setup
```

- **Beobachtung:** Der vorherige `libGL.so.1`-Fehler war behoben; die
  Qt-Validierung stoppte nun an der fehlenden `libxkbcommon.so.0`.
- **Exit-Code:** `1`

### Zyklus 2 – `libxkbcommon.so.0`

**Zeit:** 2026-10-01 12:41:30–12:41:31 UTC

```bash
timeout 300s apt-get install -y --no-install-recommends libxkbcommon0 && timeout 120s ./start.sh --setup
```

- **Beobachtung:** `libxkbcommon0` wurde erfolgreich installiert. Der
  nachfolgende Setup-Lauf erreichte den nächsten klaren Umgebungsfehler:
  `libEGL.so.1` fehlt.
- **Exit-Code:** `1` (Gesamtbefehl; Setup fehlgeschlagen)

## Erwartung und Einordnung

Jeder begrenzte Runtime-Zyklus soll genau die bestätigte fehlende
Systembibliothek bereitstellen und danach Qt erneut validieren. Beide Zyklen
beseitigten den jeweils adressierten Fehler. Nach dem zweiten Zyklus greift
die Stop-Regel: keine weitere Paketinstallation ohne neuen Plan.

`./start.sh --i25-offscreen` und `./start.sh --i25-evidence` wurden nicht
ausgeführt. Daher gibt es keine I25-Berichte, Screenshots, Hashes oder
menschliche Wahrnehmungsentscheidung. Technische Barrierefreiheit,
Laienverständlichkeit und Copy/Move-READY sind nicht belegt.

## Nächster Schritt

**STOP → neu planen:** `libEGL.so.1` und die verbleibende Qt-Laufzeit bilden
einen neuen begrenzten Runtime-Block. Erst nach erfolgreicher Qt-Validierung
darf I25-AUTO beginnen; I25-HUMAN bleibt bis zu dessen PASS gesperrt.
