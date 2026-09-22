# PROVOWARE – Register der Informationsdateien

## Zweck

Dieses Register zeigt, welche Datei welche Aussage führt, wie sicher ihr Stand ist und wann sie gepflegt werden muss. Es ersetzt keine Fachdatei. Der automatische Repository-Gate prüft, dass jede hier als Pflichtquelle genannte Datei vorhanden und eingetragen ist.

## Zustandszeichen

- 🟢 **bestätigt:** Inhalt beschreibt einen geprüften oder stabil beschlossenen Stand.
- 🟡 **offen:** Datei ist gültig, enthält aber ausdrücklich offene Prüfungen.
- 🔒 **eingefroren:** historische Ausgangslage; Änderung nur mit ausdrücklicher Freigabe.

## Führende Informationsdateien

| Datei | Führt diese Information | Zustand | Pflege bei | Besitzer |
| --- | --- | --- | --- | --- |
| `README.md` | einfacher Einstieg, Voraussetzungen und Gesamtüberblick | 🟡 drei Freigaben offen | geänderter Start, neue Abhängigkeit oder dauerhafter Fähigkeitsstand | Dokumentation |
| `AGENTS.md` | verbindliches Arbeits- und Sicherheitsverfahren | 🟢 bestätigt | geänderter Entwicklungs- oder Prüfablauf | Hauptverantwortung |
| `todo.txt` | geordnete offene Arbeit | 🟡 drei Einträge zur Freigabe, ein späterer Komfortpunkt | neuer bestätigter Befund oder geschlossener Punkt | Organisation |
| `PROVOWARE_TODO_INPUT_POOL0.md` | ursprüngliche Anforderungen | 🔒 eingefroren | nur durch ausdrücklich freigegebene Anforderungsänderung | Hauptverantwortung |
| `requirements-gui.txt` | direkte Python-Abhängigkeit mit genauer Version | 🟢 bestätigt | bewusstes Hochstufen von PySide6 | Umsetzung und Prüfung |
| `docs/README.md` | Wegweiser durch alle Informationsbereiche | 🟢 bestätigt | neue, verschobene oder entfernte Dokumentation | Dokumentation |
| `docs/CURRENT_ITERATION.md` | genau ein aktueller Arbeitsblock | 🟢 I36 | Beginn oder Abschluss einer Iteration | Organisation |
| `docs/INFO_TEXT_GOVERNANCE.md` | Regeln gegen veraltete Information | 🟢 bestätigt | neue Informationsklasse oder neuer Pflegewächter | Dokumentation |
| `docs/MAINTENANCE.md` | dauerhafte Wartungs- und Prüfregeln | 🟢 bestätigt | geänderte Wartungsgrenze | Hauptverantwortung |
| `docs/REGRESSION_MATRIX.md` | menschlich lesbare Auswahl der Prüfungen | 🟢 bestätigt | neuer Prüfbereich oder neue Fehlerfamilie | Prüfung |
| `docs/REGRESSIONSMANIFEST.json` | maschinenlesbare Fehlerfamilien und kleinste Prüfungen | 🟢 automatisch geprüft | bestätigter Fehler oder geänderter Prüfpfad | Prüfung |
| `docs/evidence/README.md` | Form und Ablage von Prüfnachweisen | 🟢 bestätigt | geänderte Nachweispflicht | Prüfung und Dokumentation |

## Aktualisierungsregel

1. Vor einer Änderung wird die führende Datei aus der Tabelle gewählt.
2. Nur diese Quelle erhält den Detailstand; andere Dateien verweisen darauf.
3. Nach einer Änderung werden Zustand und Pflegegrund dieser Tabellenzeile geprüft.
4. `python3 scripts/repo_quality.py` prüft vorhandene Pflichtdateien, Registereinträge und Verweise.
5. Ein offener Punkt bleibt 🟡 und wird niemals allein durch eine Formulierung grün.
