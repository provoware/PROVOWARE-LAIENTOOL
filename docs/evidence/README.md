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
