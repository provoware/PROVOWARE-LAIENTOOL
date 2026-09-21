## Ziel / Scope

Ein Satz:

## Bezug

- REQ:
- CR/ADR:

## Nicht-Ziele

-

## Änderung

-

## Risiken

-

## Prüfung / Evidence

- [ ] relevante lokale Tests
- [ ] `python3 scripts/repo_quality.py`
- [ ] Diff geprüft
- [ ] Evidence-ID oder Begründung, warum nicht erforderlich

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
- [ ] `python3 scripts/info_text_guard.py --base <BASE_SHA>` ist grün

## Abschluss

**Status:** 🟢 / 🟨 / 🔴
**Offen:**
**Nächster Schritt:**
