# ADR-0001: GUI-/CLI-Grundlage

- **Status:** Akzeptiert
- **Datum:** 2026-09-21
- **Bezug:** REQ-001, REQ-002, REQ-004, REQ-005, REQ-006; AQ-006, AQ-018

## Kontext

Das Produkt benötigt eine moderne, große, skalierbare Dateiansicht mit Thumbnails/Vorschauen und gleichzeitig einen gut erklärten Linux-Konsolenweg. Die Fachlogik darf nicht in zwei Bedienoberflächen auseinanderlaufen.

## Entscheidung

1. **PySide6/Qt** ist die geplante GUI-Grundlage.
2. **Tkinter ist im Produktionscode ausgeschlossen.**
3. Datei- und Tabellenansichten verwenden Qt-Modelle und Delegates.
4. Thumbnails/Vorschauen werden bedarfsgesteuert geladen und dürfen den UI-Thread nicht blockieren.
5. GUI und CLI sind Adapter desselben Application-/Domain-Kerns.
6. Die CLI basiert auf Standardbibliotheksmechanismen wie `argparse`, solange kein begründeter Bedarf für eine weitere Dependency besteht.
7. Ein read-only Preflight soll möglichst ohne optionale GUI-Abhängigkeiten ausführbar bleiben.
8. Jede nicht rein visuelle GUI-Funktion erhält verpflichtend einen fachlich äquivalenten CLI-Weg.
9. Der CLI-Standardweg verwendet ein laienfreundliches Zahlen-Auswahlmenü; Shell-Kenntnisse dürfen für Kernfunktionen nicht vorausgesetzt werden.
10. GUI und CLI müssen dieselben Use Cases, Validierungen, Sicherheitsgrenzen, Preview-/Recovery-Regeln und Fachresultate verwenden.
11. Rein visuelle Ausnahmen müssen ausdrücklich als solche dokumentiert sein.

## Konsequenzen

### Positiv
- Dateivorschauen und skalierbare Tabellen sind ohne Tkinter-Sonderwege planbar.
- Sicherheitsregeln bleiben zentral.
- CLI kann Diagnose und Recovery unterstützen, ohne zweite Fachlogik zu werden.
- optionale GUI-Dependencies können vom minimalen Preflight getrennt bleiben.

### Kosten
- Qt erhöht Paketgröße und Packaging-Aufwand.
- Thumbnail-/Preview-Pipelines benötigen Threading/Task-Grenzen und Caching.
- GUI-/CLI-Parität muss als Contract getestet werden.
- Eine neue GUI-Fachfunktion bleibt `OPEN`, solange kein gleichwertiger CLI-Pfad oder eine begründete rein visuelle Ausnahme vorliegt.

## Verbotene Abkürzungen

- kein Tkinter-Fallback;
- keine direkten Dateioperationen aus Widgets;
- keine nur in der GUI existierende Sicherheitsentscheidung;
- keine GUI-Fachfunktion ohne äquivalenten CLI-Zahlenmenüpfad;
- keine doppelte Fachlogik in GUI und CLI;
- kein synchrones Massenscannen/Thumbnail-Decoding im UI-Thread.

## Revisit-Trigger

Diese Entscheidung wird nur neu geöffnet, wenn PySide6 auf einer festgelegten Zielplattform nicht reproduzierbar paketierbar ist oder ein belegter Accessibility-/Stabilitätsblocker entsteht.
