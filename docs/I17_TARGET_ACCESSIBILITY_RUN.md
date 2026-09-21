# I17 – Realer Accessibility-Zielsystemlauf

## Status

**Evidence-Infrastruktur:** 🟢 geführter I17-B-Assistent vorbereitet
**Realer Zielsystemnachweis:** 🟨 OPEN

I17 darf erst vollständig grün werden, wenn die sichtbaren/manuellen Gates auf einer echten PySide6-/Desktop-Session geprüft wurden. CI allein kann diesen Nachweis nicht ersetzen.

## Empfohlener Ein-Befehl-Start

Auf dem echten Kubuntu-/PySide6-Zielsystem im Repository:

```bash
./start.sh --i17
```

Der Starter validiert davor automatisch die projektlokale `.venv`, die Python-Version und PySide6/Qt. Fehlt `.venv` oder PySide6 6.11.2, fragt er ausdrücklich nach, bevor er lokal einrichtet bzw. aus PyPI installiert. System-Python bleibt unverändert.

Der geführte Assistent:

1. prüft den automatisierten Accessibility-Vertrag;
2. prüft PySide6 und die echte Display-Session;
3. legt einen **neuen, separaten** lokalen Evidence-Ordner unter `~/PROVOWARE-I17-Evidence/` an;
4. erzeugt ausschließlich synthetische Testordner für leeren Ordner sowie Unicode/Leerzeichen;
5. öffnet den Evidence-Ordner im Standard-Dateimanager, soweit verfügbar;
6. startet die echte PySide6-GUI;
7. führt begrenzt durch alle manuellen Gates;
8. akzeptiert `Ja / Nein / Offen / Abbrechen`;
9. beendet ungültige Eingabewiederholungen nach drei Versuchen mit `OPEN`;
10. prüft die fünf vorgeschriebenen Screenshot-Dateien;
11. erzeugt `I17_AUSWERTUNG.txt` und `I17_EVIDENCE.json`;
12. öffnet die Textauswertung im Standardprogramm, soweit verfügbar.

Der I17-Assistent selbst installiert nichts. Die vorgelagerte `start.sh`-Einrichtung darf nach ausdrücklicher Bestätigung ausschließlich `.venv` und deren Python-Pakete anlegen/aktualisieren; kein `sudo`, kein `apt`, keine Systeminstallation. Der Produktkern bleibt read-only. Der Assistent schreibt nur in seinen neu angelegten Evidence-Ordner und überschreibt keine vorhandenen Evidence-Läufe.

### Rückgabecodes

| Code | Bedeutung |
| ---: | --- |
| 0 | vollständiger realer PASS |
| 2 | automatisierter Accessibility-Vertrag FAIL |
| 3 | echte GUI-/Display-Voraussetzung fehlt |
| 4 | GUI konnte nicht gestartet werden |
| 5 | realer Lauf ist OPEN oder manuell FAIL |

## Legacy-/Diagnosewege

Nur Vorprüfung:

```bash
python3 scripts/i17_target_evidence.py
```

JSON-Vorprüfung:

```bash
python3 scripts/i17_target_evidence.py --json
```

GUI ohne geführte Evidence:

```bash
python3 scripts/i17_target_evidence.py --launch-gui
```

## Manuelle Prüfmatrix

### 100 %

- Übersicht lesbar;
- permanente Anzeige „Sicherer Lese-Modus“ sichtbar;
- alle Kernaktionen erreichbar;
- keine abgeschnittene Kernaktion.

### 150 %

Dieselben Punkte erneut prüfen.

### 200 %

Dieselben Punkte erneut prüfen. Zusätzlich:

- Ordnerauswahl für „Dateivorschau“ erreichbar;
- Ergebnisbereich bedienbar;
- Navigation bleibt sichtbar oder sinnvoll erreichbar;
- kein notwendiger Button verschwindet.

## Tastatur

Ohne Maus:

1. Tab durch Theme-Auswahl;
2. Tab durch Skalierung;
3. Tab durch alle READY-Funktionen;
4. Dateivorschau auslösen;
5. Dialog abbrechen;
6. erneut öffnen und Ordner auswählen;
7. Shift+Tab zurück;
8. Fokus bleibt jederzeit sichtbar.

Ein nicht sichtbarer Fokus ist FAIL.

## Laienprofil

Nach jedem Kernschritt müssen vier Fragen eindeutig beantwortbar sein:

1. Was passiert als Nächstes?
2. Werden gerade Dateien verändert?
3. Kann ich zurück oder abbrechen?
4. Was tue ich, wenn etwas nicht klappt?

Unklare Antwort = UX-Befund.

## Dateivorschau

Mindestens testen:

- Ordnerdialog abbrechen;
- den vom Assistenten erzeugten leeren Ordner;
- den vom Assistenten erzeugten Ordner mit Unicode-/Leerzeichen-Dateien;
- normale erfolgreiche Vorschau;
- sichtbar: Anzahl, Gesamtgröße, Wirkung und Executor-Sperre.

Keine echte Trash-/Copy-/Move-Aktion darf möglich sein.

## Screenshots

Verbindliche Dateinamen:

```text
i17-100-overview.png
i17-150-overview.png
i17-200-overview.png
i17-keyboard-focus.png
i17-file-preview.png
```

Die Dateien werden im neu angelegten Evidence-Ordner erwartet. Der Assistent prüft deren Vorhandensein, aber **nicht automatisch den Bildinhalt**. Die manuelle Datenschutzprüfung bleibt deshalb ein eigenes Gate.

## README-Screenshots

Produktabbildungen im README dürfen echte I17-Screenshots verwenden, sobald der zugehörige Lauf dokumentiert und auf private Inhalte geprüft wurde.

Empfohlener Repo-Pfad nach bewusster Auswahl geeigneter Bilder:

```text
docs/assets/screenshots/readme/
```

Mockups bleiben getrennt unter `docs/assets/mockups/` und zählen niemals als I17-Evidence.

## PASS-Regel

I17 = PASS nur wenn:

- automatisierter Vertrag PASS;
- echte PySide6-/Display-Session belegt;
- 100/150/200 % geprüft;
- Tastaturpfad geprüft;
- Fokus geprüft;
- Dateivorschau geprüft;
- Kontrast/Reduced Motion geprüft;
- Laienprofil geprüft;
- Screenshot-Datenschutz manuell bestätigt;
- alle fünf Screenshot-Dateien vorhanden.

Ein `OPEN` wird niemals automatisch zu PASS hochgestuft.
