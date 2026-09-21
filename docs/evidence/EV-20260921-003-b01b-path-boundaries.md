# EV-20260921-003 – B01-B Pfad-/Symlink-Grenzen

- **Datum:** 2026-09-21
- **Status:** PASS nach grünem CI
- **Commit/Fingerprint:** wird durch den Merge-Commit gebunden
- **Bezug:** REQ-001; AQ-003, AQ-004
- **Umgebung:** GitHub Actions Ubuntu 24.04

## Erwartung

Ein dependency-freier, read-only Pfadvalidator bindet alle Kandidaten fail-closed an eine explizite Wurzel.

## Prüfung

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Negativfälle

- Traversal nach außen;
- absoluter Außenpfad;
- Symlink standardmäßig;
- Symlink-Flucht nach außen;
- defekter Symlink;
- nicht vorhandene Wurzel;
- fehlender Zielpfad ohne Planungsfreigabe.

## Positivfälle

- normale Datei innerhalb der Wurzel;
- Unicode und Leerzeichen;
- fehlender zukünftiger Zielname nur mit `must_exist=False`.

## Sicherheitsgrenze

Noch keine Dateioperation. B06 mit Preview, Journal, Undo und Recovery bleibt separates P0-Gate.
