# I14 – Shell-/Accessibility-Evidence

## Status

**Automatisierbarer Teil:** 🔴 FAIL
**Realer Desktop-/Laiennachweis:** 🟨 OPEN

I14 ist eine Prüfiteration. Sie repariert die geprüfte I11-GUI nicht im selben Prüfauftrag.

## Ziel

Die I11-Shell gegen den verbindlichen Laien-/Accessibility-Vertrag prüfen:

- 100 / 150 / 200 %;
- Tastatur;
- sichtbarer Fokus;
- Kontrast;
- Reduced Motion;
- verständlicher Standardweg.

## Reproduzierbarer Runner

```bash
python3 scripts/accessibility_evidence.py
python3 scripts/accessibility_evidence.py --json
```

Der Runner ist read-only und schreibt standardmäßig keine Datei.

## Automatisch prüfbar

### Kontrast

Geprüft werden pro Theme:

- Haupttext gegen Canvas;
- Haupttext gegen Surface;
- Sekundärtext gegen Surface;
- Fokusfarbe gegen Raised Surface.

Schwellen:

- normaler Text: mindestens **4.5:1**;
- Fokus-/UI-Indikator: mindestens **3:1**.

Aktueller Befund: **PASS für alle vier Themes**.

### Skalierungsvertrag

Für 100 %, 150 % und 200 % wird reproduzierbar geprüft, dass ein Stylesheet erzeugt wird.

Das beweist **nicht**, dass auf einem realen Bildschirm nichts abgeschnitten wird.

### Expliziter Fokusvertrag

Der eigene Stylesheet-Vertrag wird auf Fokusregeln für Kern-Widgets geprüft.

Aktueller Befund:

- `QPushButton:focus` → PASS
- `QComboBox:focus` → **FAIL**
- `QTextEdit:focus` → **FAIL**

Damit ist I14 aktuell objektiv **nicht vollständig grün**.

## Warum dieser FAIL nicht sofort repariert wird

Der UX-/Accessibility-Prüfer arbeitet gemäß `AGENTS.md` read-only. Ein Befund darf nicht im selben Prüfauftrag still selbst repariert werden.

Der fehlende explizite Fokusvertrag wird daher als nächster DELTA-Block vorgemerkt.

## Reale Prüfung bleibt OPEN

Folgende Punkte können nicht seriös aus Quelltext oder CI allein als PASS behauptet werden:

1. 100 % ohne abgeschnittene Kernaktion;
2. 150 % ohne abgeschnittene Kernaktion;
3. 200 % ohne abgeschnittene Kernaktion;
4. vollständiger Tastaturpfad;
5. Fokus am echten Bildschirm jederzeit klar sichtbar;
6. Kontrast im realen Qt-Rendering plausibel;
7. Reduced Motion / keine notwendige Bewegungsinformation;
8. Laienverständlichkeit des Standardwegs.

Dafür muss die echte PySide6-Shell auf einer Zielmaschine ausgeführt werden.

## Lauf auf Zielsystem

Der historische I14-Runner bleibt als interner, read-only Diagnoseweg erhalten. Der aktuelle Nutzerweg für die reale Zielsystem-Evidence ist inzwischen:

```bash
./start.sh --i17
```

I17-D automatisiert 100/150/200 %, Tab/Shift+Tab, Fokus, synthetische Dateivorschau und Screenshots. Chromium zeigt anschließend den Bericht und genau eine finale menschliche Laienabnahme.

Der historische I14-Befund wird dadurch nicht rückwirkend umgeschrieben; neue Zielsystem-Evidence gehört zu I17-D.

## Evidence-Regel

Technisches PASS ersetzt kein Laien-PASS.

Ein Repository-/CI-PASS für den Evidence-Runner bedeutet nur:

- der Runner funktioniert reproduzierbar;
- die automatischen Befunde sind reproduzierbar.

Es bedeutet ausdrücklich **nicht**, dass I14 als Accessibility-Gesamtgate bestanden ist.


## I15-Folgekorrektur

Der in I14 dokumentierte Fokusbefund wird in I15 als separater DELTA behandelt.

Im I15-Branch wurden explizite `QComboBox:focus`- und `QTextEdit:focus`-Regeln ergänzt. Der historische I14-Befund bleibt unverändert gültig für den damaligen Stand.

Die reale Desktop-/Laienprüfung bleibt weiterhin **OPEN**. Erst ein grüner automatisierter Re-Check plus späterer echter Zielsystemlauf darf den Fokusvertrag höherstufen.
