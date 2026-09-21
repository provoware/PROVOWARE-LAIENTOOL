# I17 – Automatisierte Qt-Evidence mit Chromium-Abnahme

## Status

**I17-AUTO:** 🟢 PASS
**I17-HUMAN:** 🟢 PASS
**I17 GESAMT:** 🟢 FROZEN PASS

Realer Zielsystemlauf bestätigt auf Commit `1678f050083f9e172fd9122f2808b0a7c45dea05`.

Der automatische Bericht zeigte für 100 %, 150 %, 200 %, Tab/Shift+Tab/Fokus und synthetische Dateivorschau jeweils PASS. Die finale menschliche Laienabnahme wurde anschließend in Chromium mit **Ja · PASS** bestätigt.

## Verbindlicher Start

Der offizielle Nutzerstart erfolgt ausschließlich über:

```bash
./start.sh --i17
```

Direkte Python-Aufrufe sind interne Entwickler-/Diagnosewege. Runtime-, Venv- oder Startänderungen müssen `start.sh` im selben Change-Batch aktualisieren und testen.

## I17-AUTO

Die Pipeline prüft die echte Produktions-GUI automatisch:

1. projektlokale Venv und PySide6/Qt;
2. reale Qt-/Display-Runtime;
3. 100 %, 150 % und 200 % Skalierung;
4. Sichtbarkeit und Geometrie der Kernwidgets;
5. Tab-Reihenfolge;
6. Shift+Tab-Reihenfolge;
7. Fokussetzung;
8. Abbruch/keine Ordnerauswahl;
9. leeren synthetischen Ordner;
10. Unicode-/Leerzeichen-Fixtures;
11. read-only Dateivorschau;
12. unveränderte Testdateien;
13. fünf automatisch erzeugte Screenshots.

Erzeugte Evidence:

```text
i17-100-overview.png
i17-150-overview.png
i17-200-overview.png
i17-keyboard-focus.png
i17-file-preview.png
I17_REPORT.html
I17_AUSWERTUNG.txt
I17_EVIDENCE.json
```

## Chromium als sichtbare Oberfläche

Nach erfolgreicher automatischer Prüfung startet die Pipeline einen ausschließlich lokalen HTTP-Server auf `127.0.0.1` und öffnet Chromium.

Chromium zeigt alle automatischen Gates, Befunde, die fünf Screenshots, Commit/Plattform und genau eine finale Human-Abnahme. Der Server bindet nur an `127.0.0.1`, wartet maximal zehn Minuten und beendet sich anschließend.

## I17-HUMAN

Nur bei technischem AUTO-PASS erscheint genau eine Frage:

> Ist die Oberfläche insgesamt verständlich, ruhig und ohne zusätzliche Erklärung für einen Laien bedienbar?

Der reale Zielsystemlauf wurde mit **Ja · PASS** abgeschlossen.

## Verfügbare start.sh-Modi

```bash
./start.sh --i17
./start.sh --i17-auto
./start.sh --i17-offscreen
```

Der frühere manuell geführte I17-B-Helfer wurde nach dem erfolgreichen I17-D-Lauf aus dem aktiven Repository entfernt.

## Sicherheitsgrenze

- ausschließlich synthetische Testdaten;
- kein Produkt-Executor;
- kein Copy/Move/Trash;
- keine Änderungen an Nutzerdaten;
- kein automatisches Human-PASS;
- kein externer Webserver;
- lokaler Server nur auf `127.0.0.1`;
- maximale Wartezeit zehn Minuten;
- jeder Evidence-Lauf erhält einen neuen lokalen Ordner;
- ältere lokale Evidence wird nicht überschrieben.

## Freeze-Regel

I17 wird nicht wegen rein kosmetischer Wünsche wieder geöffnet. Visuelle Komfortverbesserungen laufen separat als `UX-POLISH-01`, sofern sie keine Accessibility-Regression oder Funktionsänderung darstellen.
