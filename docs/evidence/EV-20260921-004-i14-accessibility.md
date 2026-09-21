# EV-20260921-004 – I14 Accessibility Evidence

- **Evidence-ID:** EV-20260921-004-i14-accessibility
- **Datum/Uhrzeit:** 2026-09-21, Europe/Berlin
- **Code-Fingerprint:** `e03cb26fcadd7da9e386ef1cda4d87b630bf8fdf`
- **Bezug:** B04, AQ-006, AQ-007, AQ-017, I11, I14
- **Testumgebung:** Repository-/Quelltextprüfung; keine echte Zielsystem-Display-Session in dieser Evidence
- **Status gesamt:** **FAIL**
- **Reale Desktop-/Laiengates:** **OPEN**

## Befehl

```bash
python3 scripts/accessibility_evidence.py
python3 scripts/accessibility_evidence.py --json
```

Der Runner ist read-only und schreibt standardmäßig keine Datei.

## Erwartung

1. alle vier Theme-Familien besitzen ausreichenden Text-/Fokus-Kontrast;
2. 100/150/200-%-Stylesheetvertrag ist technisch erzeugbar;
3. alle fokussierbaren Kern-Widgets besitzen einen expliziten sichtbaren Fokusvertrag;
4. reale Bildschirm-/Laiengates werden ohne echten Lauf nicht als PASS gewertet.

## Beobachtung

### Automatisierbare Kontrastprüfung

Alle vier Theme-Familien erfüllen im Quellvertrag die geprüften Mindestwerte:

- Haupttext/Canvas ≥ 4.5:1;
- Haupttext/Surface ≥ 4.5:1;
- Sekundärtext/Surface ≥ 4.5:1;
- Fokusfarbe/Raised Surface ≥ 3:1.

**Status:** PASS

### Skalierungsvertrag

Für 100 %, 150 % und 200 % kann der Stylesheetvertrag erzeugt werden.

Dies beweist nicht, dass im realen Rendering nichts abgeschnitten wird.

**Status:** PASS

### Fokusvertrag

- `QPushButton:focus` → PASS
- `QComboBox:focus` → FAIL
- `QTextEdit:focus` → FAIL

Der eigene Stylesheetvertrag garantiert damit derzeit nicht für alle fokussierbaren Kern-Widgets einen expliziten sichtbaren Fokus.

**Status:** FAIL

## Reale manuelle Gates

Mangels echter Zielsystem-Display-Session in dieser Evidence:

- 100 % ohne Clipping → OPEN
- 150 % ohne Clipping → OPEN
- 200 % ohne Clipping → OPEN
- vollständiger Tastaturpfad → OPEN
- sichtbarer Fokus im realen Rendering → OPEN
- Reduced Motion → OPEN
- Laienverständlichkeit → OPEN

## Exit-Code

Für die Evidence-Erzeugung selbst noch nicht als Produkt-PASS interpretiert. Der Runner meldet seinen fachlichen Status im Inhalt; CI prüft separat seine reproduzierbare Ausführung und Tests.

## Bekannte Grenzen

- kein Screenshot-/Display-Nachweis;
- keine menschliche Wahrnehmungsprüfung;
- keine Behauptung über echtes 200-%-Layout;
- keine Reparatur des Fokusbefunds in derselben VERIFY-Iteration.

## Folge

Der Fokusbefund wird als DELTA der nächsten Iteration behandelt. Ein späterer echter Zielsystemlauf darf erst danach ein vollständiges Accessibility-PASS erwägen.
