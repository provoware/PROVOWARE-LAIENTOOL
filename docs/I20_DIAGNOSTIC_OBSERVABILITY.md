# I20 – Diagnose-/Recovery-Observability

## Status

Read-only Diagnosemodell und CLI-Ausgabe vorbereitet. **Kein Datei-Export, keine Persistenz, keine automatische Reparatur.**

## Ziel

Reale Fehlerfälle sollen künftig reproduzierbar und datensparsam beschrieben werden können, ohne private Pfade, IDs oder Secrets unnötig offenzulegen.

## Diagnosebericht

Das immutable Modell enthält:

- Schema-Version;
- Collection-Status;
- Health-Status;
- strukturierte Diagnoseeinträge;
- Hinweise;
- Redaction-Status;
- feste Sperre `write_paths_enabled = False`.

## Quellen

Aktuell werden ausschließlich read-only Informationen verwendet:

- Plattform-/Runtime-Fakten aus dem bestehenden Preflight;
- Capability-Zustände;
- Startprofil;
- optional ein bereits vorhandener `JournalSnapshot`;
- optional explizit übergebene Zusatzmeldungen.

## Datenschutz / Redaction

`redact_text()` entfernt oder ersetzt mindestens:

- bekannte Home-Pfade → `$HOME`;
- allgemeine `/home/<user>`-Pfade;
- E-Mail-Adressen;
- typische GitHub-Token-Muster;
- typische OpenAI-Token-Muster;
- Bearer-Tokens.

Recovery-IDs werden standardmäßig **nicht** in den Diagnosebericht übernommen.

## Recovery-Observability

Wenn ein `JournalSnapshot` übergeben wird, zeigt der Bericht nur:

- Zustand;
- Versuchszähler;
- ob die Wirkung sicher bekannt ist;
- ob automatische Wiederholung erlaubt ist;
- fail-closed Recovery-Hinweis;
- redigierten letzten Fehler, falls vorhanden.

Keine Journal-Persistenz wird geöffnet.

## CLI-only Use Case

Registry-ID:

```text
diagnostics.snapshot
```

Eigenschaften:

- CLI: READY;
- GUI: nicht verfügbar;
- `diagnostic_cli_only=True`;
- Sicherheitsklasse: read-only.

Das Zahlenmenü kann damit einen Diagnosebericht anzeigen, ohne eine neue GUI-Fachfläche einzuführen.

## Direkter Helfer

```bash
python3 scripts/diagnostic_snapshot.py
python3 scripts/diagnostic_snapshot.py --json
```

Die Ausgabe geht ausschließlich nach stdout.

## Kein Datei-Export

I20 erzeugt bewusst **keine** Diagnose-Datei.

Grund:

- Read-only-Lock bleibt vollständig aktiv;
- Exportpfad, Dateiname, Datenschutz und Benutzerfreigabe sind ein eigener späterer Vertrag;
- stdout reicht bereits für reproduzierbare Support-/Debugging-Ausgaben.

## Statusmodell

`collection_status` beantwortet:

> Konnte der Diagnosebericht technisch erstellt werden?

`health_status` beantwortet:

> Sind die beobachteten System-/Recovery-Fakten aktuell unauffällig oder bleibt etwas OPEN?

Damit wird ein sauber erstellter Bericht nicht fälschlich als Produkt-PASS interpretiert.

## Nicht-Ziele

- kein Datei-Export;
- kein Upload;
- kein Netzwerk;
- kein Telemetrieversand;
- kein Crash-Reporter;
- keine Journal-Persistenz;
- keine automatische Reparatur;
- keine Secrets;
- keine vollständigen Nutzerpfade;
- keine GUI-Erweiterung.

## Gate

Mindestens prüfen:

- Home-/E-Mail-/Token-Redaction;
- keine Recovery-IDs in Ausgabe;
- unbekannte Recovery-Wirkung sichtbar;
- kein Auto-Retry;
- JSON parsebar;
- CLI-only Registry-Vertrag;
- Zahlenmenüpfad;
- Application-Core-Ausgabe;
- Read-only-Lock;
- vollständige Suite.
