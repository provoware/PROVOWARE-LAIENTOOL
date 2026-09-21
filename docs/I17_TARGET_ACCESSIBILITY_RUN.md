# I17 – Realer Accessibility-Zielsystemlauf

## Status

**Evidence-Infrastruktur:** vorbereitet
**Realer Zielsystemnachweis:** 🟨 OPEN

I17 darf erst vollständig grün werden, wenn die sichtbaren/manuellen Gates auf einer echten PySide6-/Desktop-Session geprüft wurden.

## Ein-Befehl-Start

Auf dem Zielsystem im Repository:

```bash
python3 scripts/i17_target_evidence.py --launch-gui
```

Der Helfer:

1. prüft den automatisierten Accessibility-Vertrag erneut;
2. prüft, ob PySide6 und eine echte Display-Session vorhanden sind;
3. zeigt alle manuellen I17-Gates;
4. nennt die erforderlichen Screenshot-Dateinamen;
5. startet anschließend die echte GUI.

Er installiert nichts und ändert keine Nutzdateien.

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
- leerer Ordner;
- Ordner mit Unicode-/Leerzeichen-Datei;
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

Screenshots sollen keine unnötigen persönlichen Dateinamen, Nutzernamen oder privaten Pfade zeigen.

## README-Screenshots

Produktabbildungen im README dürfen echte I17-Screenshots verwenden, sobald der zugehörige Lauf dokumentiert wurde.

Empfohlener Repo-Pfad:

```text
docs/assets/screenshots/readme/
```

Markdown:

```md
![PROVOWARE Übersicht bei 100 %](docs/assets/screenshots/readme/i17-100-overview.png)
```

### Mockups

Mockups/Entwürfe dürfen ebenfalls im Repository liegen, aber:

- eigener Pfad, z. B. `docs/assets/mockups/`;
- sichtbare Kennzeichnung „Designentwurf / nicht aktuelle Produktoberfläche“;
- niemals als I17-Evidence verwenden.

## PASS-Regel

I17 = PASS nur wenn:

- automatisierter Vertrag PASS;
- echte PySide6-/Display-Session belegt;
- 100/150/200 % geprüft;
- Tastaturpfad geprüft;
- Fokus geprüft;
- Dateivorschau geprüft;
- Laienprofil geprüft;
- Screenshots/Evidence redigiert und nachvollziehbar.

CI allein kann I17 nicht auf PASS setzen.
