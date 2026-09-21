# I26 – Diagnose-Export Preflight Core

## Status

Read-only ExportPlan-/Payload-Preflight implementiert.

**Kein Writer. Keine Datei wird erzeugt, verändert, umbenannt oder gelöscht.**

## Ziel

Vor einem späteren Diagnose-Writer sollen alle fachlichen und datenschutzrelevanten Voraussetzungen bereits vollständig geprüft sein.

Der spätere Writer soll nur noch erhalten:

```text
validated ExportPlan
validated serialized payload bytes
```

## Datenmodell

### ExportPlan

Immutable:

- Zielordner;
- Dateiname;
- finaler Zielpfad;
- Format;
- Payload-Größe;
- SHA-256;
- `overwrite_allowed=False`;
- `write_enabled=False`.

### ExportPreparation

Immutable:

- Status;
- Fehler;
- serialisierter Payload oder `None`;
- ExportPlan oder `None`.

## Unterstützte Formate

- `json`
- `text`

ZIP/Binärformate bleiben gesperrt.

## Preflight-Reihenfolge

1. Format prüfen.
2. `redaction_applied=True` verlangen.
3. `write_paths_enabled=False` verlangen.
4. Zielordner existiert.
5. Zielordner ist echter Ordner und kein Symlink.
6. Dateiname enthält keinen Pfad.
7. Suffix passt zum Format.
8. finaler Zielpfad existiert noch nicht.
9. finaler Zielpfad ist kein Symlink.
10. Payload deterministisch serialisieren.
11. Payload als UTF-8 prüfen.
12. Payload erneut durch `redact_text()` spiegeln.
13. Wenn zweite Redaction noch etwas verändern würde: BLOCKED.
14. Größe und SHA-256 berechnen.
15. immutable ExportPlan erzeugen.

## Zweites Redaction-Gate

Ein Report mit `redaction_applied=True` wird nicht blind vertraut.

Der bereits serialisierte Payload wird erneut geprüft:

```text
serialized payload
→ redact_text(payload)
→ Vergleich
```

Wenn sich der Text ändern würde:

```text
BLOCKED
→ kein ExportPlan
→ kein späterer Writer-Aufruf
```

Damit wird ein inkonsistent gesetztes Redaction-Flag nicht ausreichend, um sensible Inhalte zu exportieren.

## No-overwrite schon vor dem Writer

Der Preflight blockiert:

- vorhandene Zieldatei;
- Symlink-Zieldatei;
- falschen/verschachtelten Dateinamen;
- falsches Format/Suffix.

Der spätere Writer muss diese Regeln unmittelbar vor Commit dennoch erneut prüfen, weil zwischen Plan und Write ein Race entstehen kann.

## Determinismus

Bei identischem:

- DiagnosticReport;
- Zielordner;
- Format;
- Dateinamen

entstehen identische:

- Payload-Bytes;
- Byte-Länge;
- SHA-256;
- ExportPlan.

## Keine Schreibfreigabe

Auch bei PASS gilt:

```text
ExportPlan.write_enabled = False
ExportPlan.overwrite_allowed = False
```

PASS bedeutet ausschließlich:

> Dieser Export wäre fachlich/datenschutzseitig vorbereitet.

Nicht:

> Dieser Export darf jetzt geschrieben werden.

## Tests

Abgedeckt:

- JSON;
- Text;
- deterministische Wiederholung;
- Unicode-/Leerzeichen-Zielordner;
- vorhandene Zieldatei unverändert;
- Symlink-Zielordner;
- dangling Symlink-Zieldatei;
- Pfad im Dateinamen;
- falsches Format;
- falsches Suffix;
- unredigierter Report;
- Report mit Schreibfreigabe;
- zweites Redaction-Gate;
- immutable ExportPlan.

## Sicherheitsstatus

```text
Diagnose sammeln              🟢 read-only
Redaction                     🟢
I26 Payload/ExportPlan        🟢 read-only
Datei-Writer                  🔒
Guard-REOPEN                  🔒
Datei-Export                  🔒
Overwrite                     🔒
Netzwerk                      🔒
```

## Nicht-Ziele

- kein `diagnostic_export.py` Writer;
- kein `open(..., "x")`;
- keine Temp-Datei;
- kein fsync;
- kein Rename/Commit;
- keine Guard-Allowlist;
- keine Registry;
- keine GUI/CLI-Funktion;
- keine Nutzerbestätigung;
- kein Netzwerk.

## Nächster Writer-Gate

Vor einem echten Writer weiterhin Pflicht:

1. Writer-spezifischer Guard;
2. exakter Guard-REOPEN;
3. create-only/no-clobber Commit;
4. Partial-/Crash-Tests;
5. Race-Test;
6. ENOSPC;
7. PermissionError;
8. Evidence.

I26 öffnet keinen dieser Schritte automatisch.
