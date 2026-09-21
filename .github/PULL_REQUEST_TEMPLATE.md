## Ziel / Scope

Ein Satz:

## Bezug

- REQ:
- CR/ADR:

## Nicht-Ziele

-

## Änderung

-

## Kollisionsschutz / Dateibesitz

- [ ] jede geänderte Datei hat genau einen schreibenden Besitzer
- [ ] Prüfer waren read-only und haben eigene Befunde nicht repariert
- [ ] kollidierende Änderungen wurden serialisiert

## Risiken

-

## Prüfung / Evidence

- [ ] relevante targeted Tests
- [ ] `python3 scripts/repo_quality.py`
- [ ] `python3 scripts/read_only_guard.py` solange Schreibpfade gesperrt sind
- [ ] `python3 scripts/core_diagnostics.py` falls Core/Safety betroffen
- [ ] vollständige Suite vor Merge
- [ ] Diff geprüft
- [ ] Evidence-ID oder Begründung, warum nicht erforderlich

## Testbudget / Schleifenschutz

- [ ] targeted Tests vor Full Suite
- [ ] kein identischer Fehltest mehr als einmal ohne Zustandsänderung wiederholt
- [ ] höchstens zwei Reparaturzyklen pro Root Cause
- [ ] Timeouts/Hänger als eigener Befund klassifiziert
- [ ] keine unbegrenzte Poll-/Retry-/Wait-Schleife eingeführt
- [ ] jeder Retry besitzt Limit und Abbruchbedingung

## Debugging / Triage

- Fehlerklasse bei Befund: `PRODUCT | TEST | INFRASTRUCTURE | EVIDENCE | NONE`
- erster ursächlicher Fehler:
- kleinster reproduzierbarer Fall:
- [ ] kein Folgefehler als Primärursache behandelt
- [ ] keine Testabschwächung ohne belegte Testursache

## Sicherheitsgate

- [ ] keine stille Installation / kein stiller Netzwerkzugriff
- [ ] keine Rechteausweitung
- [ ] keine neuen Schreibpfade ODER Preview/Rückweg belegt
- [ ] keine Secrets / unnötigen sensiblen Pfade in Logs

## UX / Accessibility

- [ ] nicht betroffen ODER `docs/LAIEN_QUALITY_STANDARD.md` gegen Standardweg geprüft
- [ ] Tastatur/Fokus/Skalierung 100/150/200 %/Kontrast geprüft
- [ ] wichtige Zustände nicht nur über Farbe vermittelt

## Info-Text-Impact

- [ ] README/TODO/Docs/Evidence sind nicht betroffen ODER passend zum realen Ist-Stand aktualisiert
- [ ] README/TODO kopieren keinen flüchtigen PR-/Merge-/CI-Livestatus
- [ ] neue Iterationsdokumente sind in `docs/README.md` auffindbar
- [ ] `python3 scripts/info_text_guard.py --base <BASE_SHA>` ist grün

## GUI / CLI Parität

- [ ] nicht betroffen ODER jede neue GUI-Fachfunktion besitzt denselben Core-Use-Case und einen CLI-Zahlenmenüpfad
- [ ] rein visuelle Ausnahme ist dokumentiert

## Abschluss

**Iteration:**
**Status:** 🟢 / 🟨 / 🔴 / 🔵 / 🔒
**Fortschritt:** `████████░░ 80 %`
**A – FESTER PLAN:**
**B – VARIABLE FOLGEAUFGABE:**
**Offen:**
**Nächster Schritt:**
**Vorausplanung 1:**
**Vorausplanung 2:**
**Vorausplanung 3:**
