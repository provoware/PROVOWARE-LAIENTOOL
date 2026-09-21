# I11 – Read-only GUI-/CLI-Shell

## Status

Technischer Shell-/Paritätsvertrag implementiert. Die reale Accessibility-Gesamtabnahme wurde im späteren I17-D-Zielsystemlauf erfolgreich als **PASS** bestätigt.

## Ziel

Der erste sichtbare PROVOWARE-Prototyp verwendet einen gemeinsamen Application-Core und eine gemeinsame Capability-/Use-Case-Registry.

```text
                 ┌─ GUI / PySide6
Registry → Core ─┤
                 └─ CLI / Zahlenmenü
```

Kein Adapter enthält eigene Fachlogik.

## Aktuelle read-only Use Cases

1. **Übersicht**
2. **System prüfen**
3. **Hilfe**

Alle drei sind gleichzeitig:

- in der Registry als `READY` eingetragen;
- im GUI-Adapter verfügbar;
- im CLI-Zahlenmenü verfügbar;
- read-only;
- ohne Preview-/Recovery-Pflicht, weil sie keine Nutzerdaten verändern.

## Startwege

Der dauerhafte offizielle Nutzer-Einstiegspunkt ist ausschließlich `start.sh`.

Bestehender B01-Preflight:

```bash
./start.sh --preflight
./start.sh --json
```

Laienfreundliches Zahlenmenü:

```bash
./start.sh --menu
```

PySide6-GUI:

```bash
./start.sh --gui
```

Der Starter validiert die projektlokale Venv und installiert nichts still. Direkte `python3 start.py ...`-Aufrufe sind nur interne Entwicklerwege.

## CLI-Vertrag

- Hauptfunktionen ausschließlich über Zahlen;
- `0` beendet;
- ungültige Eingabe erklärt den nächsten sicheren Schritt;
- jede Funktion stammt aus derselben Registry wie die GUI;
- permanente Lese-Modus-Anzeige.

## GUI-Vertrag

Die Shell enthält:

- große PROVOWARE-Kopfzeile;
- permanente Anzeige: `🔒 Sicherer Lese-Modus`;
- linke Funktionsnavigation;
- ruhige Hauptkarte für Ergebnis/Hilfe;
- Theme-Auswahl;
- Größenwahl 100/125/150/175/200 %;
- sichtbaren Qt-Tastaturfokus;
- read-only Ergebnisfeld.

## Vier Themes

1. Purple Neon
2. Turquoise Neon
3. Graphite Electric
4. Crimson / Copper

Die Themes verändern ausschließlich Darstellung. Navigation und Fachlogik bleiben identisch.

## Paritätsgate

Automatisch geprüft wird:

- jede `READY`-GUI-Funktion besitzt einen CLI-Pfad;
- beide Adapter beziehen Anzeigenamen und Verfügbarkeit aus derselben Registry;
- Registry-Vertrag bleibt grün;
- genau vier Theme-Familien existieren;
- Skalierungswerte werden auf 100–200 % begrenzt.

## Sicherheitsgrenzen

I11 darf nicht:

- Dateien verschieben, kopieren oder löschen;
- Einstellungen persistent schreiben;
- Pakete installieren;
- Netzwerkzugriff ausführen;
- Berechtigungen erhöhen;
- zukünftige Datei-Use-Cases als READY vortäuschen.

## Reale Folge-Evidence

Die technische Struktur allein ersetzte kein reales Laien-/Accessibility-PASS. Dieser Nachweis wurde später durch I17-D erbracht.

Vor vollständigem B04-/Shell-PASS sind auf echter GUI-Umgebung noch zu belegen:

- 100 %;
- 150 %;
- 200 %;
- vollständiger Tastaturpfad;
- sichtbarer Fokus;
- Kontrast;
- Reduced Motion;
- verständlicher Standardweg.
