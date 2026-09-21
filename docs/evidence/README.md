# Evidence-Konvention

Evidence ist ein reproduzierbarer Nachweis, kein Fließtext-Tagebuch.

## Ablage

Dateiname: `EV-YYYYMMDD-NNN-kurzname.md`

## Pflichtfelder

- Evidence-ID
- Datum/Uhrzeit und Zeitzone
- Commit/Fingerprint
- betroffene REQ/CR/ADR
- Testumgebung
- Befehl oder manueller Ablauf
- Erwartung
- Beobachtung
- Exit-Code, falls vorhanden
- Status: `PASS | FAIL | OPEN | SKIPPED`
- Artefakte/Hashes, falls relevant
- bekannte Grenzen

## Regeln

- fehlende Prüfung = `OPEN`;
- `SKIPPED` braucht Begründung;
- Fakten, Annahmen und Vermutungen nicht vermischen;
- keine Secrets oder unnötigen personenbezogenen Pfade;
- nach RC-Freeze Evidence ergänzen, aber RC nicht reparieren.

- `EV-20260921-005-i17-real-accessibility.md` – realer I17-D-Zielsystemlauf: AUTO PASS + HUMAN PASS, Freeze-Nachweis.

- `EV-20260921-006-branch-hygiene-i27.md` – Altbranch-Klassifikation, gerettete MOVE-Reversibilitätsinvariante und gehärteter I27-Transplant.

- `EV-20260922-007-i28-diagnostic-writer-testlab.md` – automatischer I28 No-clobber-/Race-/Crash-/Failure-Nachweis auf dem Writer-RC.

- `EV-20260922-008-i30-diagnostic-export-authorization.md` – I30 Fingerprint-/Doppelbestätigungs-/Replay-/One-shot-Autorisierungsnachweis.

- `EV-20260922-009-i31-diagnostic-export-adapter-evidence.md` – I31 GUI-/CLI-AUTO-Nachweis mit 100/150/200 %, Tastatur, Doppelbestätigung, Cancel, BLOCKED und exakt-eine-Datei-PASS.

- `EV-20260922-010-i32-portable-offline-package.md` – I32 deterministisches Linux-x86_64-ZIP, Offline-Wheelhouse, Fremdpfad- und Bootstrap-Nachweis.
