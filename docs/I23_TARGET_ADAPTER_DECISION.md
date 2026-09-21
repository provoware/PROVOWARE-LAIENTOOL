# I23 – Same-Root Zielauswahl Adapter-Decision

## Status

**Adaptervertrag entschieden. Keine GUI-/CLI-Implementierung. Kein neuer READY-Use-Case.**

## Ausgangslage

Der nichtvisuelle Kern ist bereits vorhanden:

- I15: read-only Inventar;
- I18: Suche, Sortierung, Top 10/50/100;
- I19: Same-Root-Zielwahlvertrag;
- I21: `prepare_copy_preview()` und `prepare_move_preview()`.

Offen ist ausschließlich, wie Nutzer später Auswahl und Ziel in GUI und Zahlenmenü erfassen.

Der reale I17-Zielsystemlauf ist weiterhin OPEN. Deshalb darf I23 noch keine sichtbare GUI-Erweiterung implementieren.

## Entscheidung

Copy-/Move-Preview wird später als **ein gemeinsamer fachlicher Workflow** mit zwei Adaptern eingeführt.

```text
Inventory / InventoryView
        ↓
Dateiauswahl
        ↓
Aktion wählen: Kopieren | Verschieben
        ↓
Same-Root Zielordner wählen
        ↓
prepare_copy_preview() / prepare_move_preview()
        ↓
gemeinsame Preview-Darstellung
        ↓
🔒 STOP – kein Executor
```

## Registry-Gate

Ein neuer Produkt-Use-Case darf erst auf `READY` gesetzt werden, wenn gleichzeitig:

1. gemeinsamer Application-Pfad implementiert ist;
2. GUI-Adapter vorhanden ist;
3. CLI-Zahlenmenüpfad vorhanden ist;
4. fachliche Ergebnisse beider Adapter identisch getestet sind;
5. reale Accessibility-Evidence für die sichtbare GUI-Erweiterung vorliegt.

Vorher bleibt ein künftiger Registry-Eintrag `OPEN` oder wird noch gar nicht registriert.

**Keine halbfertige GUI-Funktion als READY.**

## Geplante Use-Case-Grenze

Empfohlene spätere IDs:

```text
files.preview_copy
files.preview_move
```

Beide sind fachlich Preview-Funktionen.

Sie dürfen nicht heißen:

- `files.copy`;
- `files.move`;
- `organize.execute`.

Begründung: Der Name soll nicht suggerieren, dass bereits geschrieben wird.

## Gemeinsame Eingaben

Beide Adapter müssen am Application-Core dieselben fachlichen Eingaben erzeugen:

```text
root
selected_relative_paths
target_dir
```

Keine Adapter-spezifischen Sicherheitsparameter.

Nicht erlaubt:

- GUI erzeugt eigene Zielpfade;
- CLI validiert Pfade separat statt über Core;
- Adapter entscheidet Overwrite;
- Adapter erfindet Auto-Rename;
- Adapter verändert Auswahlreihenfolge heimlich.

## GUI-Vertrag

### 1. Root

Der Nutzer wählt oder bestätigt eine Root.

Die Root wird nicht automatisch ohne sichtbare Bestätigung gewechselt.

### 2. Dateiansicht

Die GUI zeigt eine I18-basierte Liste/Kachelansicht.

Mindestens sichtbar:

- Dateiname/relativer Pfad;
- Größe;
- Auswahlzustand.

Spätere Komfortdaten dürfen ergänzt werden, aber nicht die Auswahlsemantik verändern.

### 3. Auswahl

Mehrfachauswahl ist erlaubt.

Regeln:

- Auswahlzustand immer sichtbar;
- Tastaturauswahl möglich;
- keine Vorauswahl aller Dateien ohne klare Kennzeichnung;
- „Alle sichtbaren auswählen“ darf sich nur auf die aktuell sichtbare/gefilterte Ansicht beziehen und muss Anzahl zeigen;
- Filteränderung darf Auswahl nicht heimlich erweitern.

### 4. Aktion

Zwei klar getrennte Preview-Aktionen:

- **Kopieren – Vorschau**
- **Verschieben – Vorschau**

Kein Button „Ausführen“.

### 5. Zielordner

GUI-Zielauswahl muss auf die aktuelle Root begrenzt werden.

Der gewählte Zielordner wird vor der Preview sichtbar angezeigt.

Nicht erlaubt:

- freie externe Root;
- Symlink-Ziel;
- automatisch erfundener Unterordner;
- stiller Fallback auf Downloads/Home.

### 6. Preview

Vorhandener I21-Core erzeugt den Plan.

Darstellung muss mindestens zeigen:

- Aktion;
- Zahl der Dateien;
- Gesamtgröße;
- Quelle(n);
- Zielordner;
- Kollisionen/Blocker;
- Reversibilitäts-Hinweis;
- permanente Aussage: **Es wird noch nichts verändert.**

## CLI-Zahlenmenü-Vertrag

Die Konsole bleibt laienfreundlich und nummeriert.

### Schritt 1 – Root

Explizite Root-Auswahl/-Eingabe wie im bestehenden sicheren Pfad.

### Schritt 2 – Ansicht

I18-View wird nummeriert dargestellt.

Beispiel:

```text
1  bericht.pdf          2,4 MB
2  foto.jpg             8,1 MB
3  notiz.txt            4 KB
0  Zurück
```

### Schritt 3 – Auswahl

Bevorzugter Standard:

- einzelne Nummer;
- mehrere Nummern;
- optional „alle sichtbaren“ als ausdrücklich benannte Option.

Keine Shell-Globs und keine erforderlichen Dateinamen.

### Schritt 4 – Aktion

```text
1  Kopieren – nur Vorschau
2  Verschieben – nur Vorschau
0  Zurück
```

### Schritt 5 – Ziel

Zielordner innerhalb der Root wird nummeriert angeboten.

Eine freie Pfadeingabe darf höchstens Experten-Fallback sein und muss denselben Core-Vertrag durchlaufen.

### Schritt 6 – Preview

CLI zeigt dasselbe fachliche Ergebnis wie GUI:

- Anzahl;
- Gesamtgröße;
- Quelle/Ziel;
- Blocker;
- Rückweg;
- Hinweis „Es wird nichts verändert“.

## Navigation / Abbruch

In jedem Adapter gilt:

- Abbruch vor Preview ohne Seiteneffekt;
- `0` im CLI bedeutet konsistent Zurück;
- GUI besitzt sichtbare Zurück-/Abbrechen-Möglichkeit;
- Wechsel von Root verwirft eine alte Auswahl sichtbar;
- kein stilles Beibehalten einer Auswahl aus einer anderen Root.

## Statusmodell

Empfohlen:

- `PASS`: valide Preview erzeugt;
- `OPEN`: Eingabe/Auswahl fehlt oder Nutzer hat abgebrochen;
- `BLOCKED`: Sicherheits-/Pfad-/Kollisionsvertrag verletzt.

Adapter dürfen diese Statuswerte nicht umdeuten.

## Fehlertexte

Fachfehler kommen aus dem gemeinsamen Core.

Adapter dürfen sie layouten, aber nicht fachlich ersetzen.

Sichtbar nach Laienvertrag:

```text
Was ist passiert?
Was bedeutet das?
Was kann ich jetzt tun?
```

## Accessibility-Gate

Vor `READY` der GUI-Funktion zwingend:

- realer I17-Basislauf abgeschlossen;
- neuer Workflow bei 100/150/200 % geprüft;
- vollständiger Tab/Shift+Tab-Pfad;
- sichtbare Mehrfachauswahl;
- sichtbarer Fokus;
- Zielordnerdialog per Tastatur bedienbar;
- Preview bei 200 % vollständig erreichbar;
- Reduced Motion;
- Laienprofil.

Ein automatisierter Widget-Test ersetzt diese Evidence nicht.

## Paritätstests

Spätere Implementierung muss mindestens beweisen:

1. gleiche Root + Auswahl + Ziel + Aktion → gleiche Preview;
2. gleiche Kollision → gleicher BLOCKED-Grund;
3. externe Zielwahl → in beiden Adaptern BLOCKED;
4. leere Auswahl → in beiden OPEN;
5. Abbruch → keine Dateiänderung;
6. Unicode/Leerzeichen → identisches fachliches Ergebnis;
7. keine Fachlogik in Adaptermodulen.

## Kein Executor-Übergang

Der Workflow endet nach Preview.

Es gibt in diesem Vertrag ausdrücklich keinen:

- „Jetzt kopieren“-Button;
- „Jetzt verschieben“-Button;
- Bestätigungsdialog für echten Write;
- Journal-Write;
- Recovery-Ausführung.

Ein späterer Executor benötigt einen separaten REOPEN.

## Freigegeben für spätere Implementierung

Nach realem I17-Gate:

- GUI-Dateiauswahl auf I18;
- CLI-nummerierte Auswahl auf I18;
- Copy-/Move-Preview;
- Same-Root-Zielordnerauswahl;
- gemeinsamer Application-Core;
- identische Ergebnissemantik.

## Weiter gesperrt

- sichtbare Implementierung vor realem I17;
- READY-Registry vor kompletter Parität;
- Executor;
- externe Ziele;
- Overwrite;
- Auto-Rename;
- Cross-Device Move;
- Persistenz;
- Rechteausweitung.
