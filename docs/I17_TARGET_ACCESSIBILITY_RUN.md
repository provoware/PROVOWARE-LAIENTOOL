# I17 – Automatisierte Qt-Evidence mit Chromium-Abnahme

## Status

**I17-AUTO:** 🔵 maschinell reproduzierbare Qt-Evidence
**I17-HUMAN:** 🟨 genau eine finale Laienabnahme in Chromium
**Gesamt:** PASS nur bei AUTO PASS + HUMAN PASS

## Verbindlicher Start

Der offizielle Nutzerstart erfolgt ausschließlich über:

```bash
./start.sh --i17
```

Direkte Aufrufe von Python-Skripten sind nur interne Entwickler-/Diagnosewege. Wenn sich Runtime, Venv oder I17 ändern, muss `start.sh` im selben Change-Batch angepasst und getestet werden.

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

Chromium zeigt:

- alle automatischen Gates;
- konkrete Fehlerdetails;
- die fünf Screenshots;
- Commit und Plattform;
- I17-AUTO / I17-HUMAN / Gesamtstatus;
- genau eine finale Human-Abnahme.

Es gibt keinen externen Netzwerkdienst und keine Cloud-Übertragung. Der lokale Server wartet maximal zehn Minuten und beendet sich anschließend.

## I17-HUMAN

Nur bei technischem AUTO-PASS erscheint in Chromium genau eine Frage:

> Ist die Oberfläche insgesamt verständlich, ruhig und ohne zusätzliche Erklärung für einen Laien bedienbar?

- **Ja · PASS** → HUMAN PASS
- **Nein · FAIL** → HUMAN FAIL
- **Unsicher · OPEN** → HUMAN OPEN

Die Browserantwort aktualisiert lokal HTML, TXT und JSON.

## Weitere start.sh-Modi

```bash
./start.sh --i17
./start.sh --i17-auto
./start.sh --i17-offscreen
./start.sh --i17-guided
```

- `--i17` und `--i17-auto`: echter Desktop + Chromium-Abnahme.
- `--i17-offscreen`: technische Qt-Pipeline ohne Human-PASS; bleibt für Gesamt-I17 nicht ausreichend.
- `--i17-guided`: alter geführter I17-B-Vergleichspfad, nicht mehr Standard.

## Sicherheitsgrenze

- ausschließlich synthetische Testdaten;
- kein Produkt-Executor;
- kein Copy/Move/Trash;
- keine Änderungen an Nutzerdaten;
- kein automatisches Human-PASS;
- kein externer Webserver;
- lokaler Server nur auf `127.0.0.1`;
- maximale Wartezeit zehn Minuten;
- jeder Evidence-Lauf erhält einen neuen Ordner;
- ältere Evidence wird nicht überschrieben.

## PASS-Regel

```text
I17-AUTO PASS
    +
I17-HUMAN PASS
    =
I17 GESAMT PASS
```

Ein AUTO-FAIL kann niemals durch die Human-Abnahme überstimmt werden.
