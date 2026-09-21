# EV-20260921-005 – I17 reale Accessibility-Abnahme

## Ergebnis

**I17-AUTO:** PASS
**I17-HUMAN:** PASS
**I17 GESAMT:** PASS

## Zielsystemlauf

Bestätigter Produktstand:

`1678f050083f9e172fd9122f2808b0a7c45dea05`

Der reale I17-D-Lauf wurde über den offiziellen Starter ausgeführt:

```bash
./start.sh --i17
```

Der Chromium-Bericht zeigte:

- 100 % Layout: PASS;
- 150 % Layout: PASS;
- 200 % Layout: PASS;
- Tab / Shift+Tab / Fokus: PASS;
- synthetische Dateivorschau: PASS;
- fünf automatisch erzeugte Screenshots vorhanden;
- I17-AUTO: PASS.

Nach Sichtung des realen Berichts und der Screenshots wurde die finale Frage zur Laienverständlichkeit mit **Ja · PASS** bestätigt.

## Evidence-Grenze

Die vollständigen automatisch erzeugten lokalen HTML-/JSON-/TXT-Dateien und Screenshots bleiben auf dem Zielsystem im dafür angelegten Evidence-Ordner. Dieses Repository-Dokument hält den bestätigten Status und den geprüften Commit fest, ohne private lokale Pfade zu übernehmen.

## Freeze

I17 ist für diesen Shell-Stand eingefroren. Rein kosmetische Wünsche wie größere Berichtsschrift oder zusätzliche Akzentfarbe laufen separat als `UX-POLISH-01` und öffnen I17 nicht erneut.
