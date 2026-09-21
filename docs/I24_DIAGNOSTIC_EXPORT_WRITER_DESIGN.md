# I24 – Diagnose-Export Writer Design

## Status

**Writer-Architektur entschieden. Keine Implementierung. Kein Schreibpfad geöffnet.**

## Ausgangslage

I20 erzeugt einen redigierten Diagnosebericht in-memory bzw. auf stdout.

I22 hat einen späteren lokalen Export grundsätzlich zugelassen, aber nur unter einem eigenen Writer-/REOPEN-Gate.

Der aktuelle Produktbaum bleibt durch `scripts/read_only_guard.py` vollständig write-locked.

## Ziel von I24

Die spätere Export-Implementierung so klein und prüfbar definieren, dass:

- kein allgemeiner Writer entsteht;
- kein bestehender Export überschrieben wird;
- Rohdaten niemals vor Redaction geschrieben werden;
- ein Crash/Fehler keine scheinbar gültige halbe Exportdatei hinterlässt;
- der Read-only-Guard nur für genau diesen einen Writer gezielt REOPENed wird;
- alle übrigen Produktmodule weiter unverändert write-locked bleiben.

## Geplante Modulgrenze

Ein späterer Writer darf ausschließlich in einem dedizierten Modul liegen:

```text
src/provoware_laientool/diagnostic_export.py
```

Andere Produktmodule bleiben weiter durch den bestehenden Guard vollständig gesperrt.

Nicht erlaubt:

- Schreiblogik in `diagnostics.py`;
- Schreiblogik in `application_core.py`;
- Schreiblogik in GUI/CLI-Adaptern;
- allgemeine Filesystem-Helfer mit Write-Funktion;
- globale Guard-Deaktivierung.

## Geplanter Datenfluss

```text
read-only Fakten
    ↓
DiagnosticReport
    ↓
Redaction vollständig
    ↓
Export-Payload validieren
    ↓
ExportPlan erzeugen
    ↓
Nutzer bestätigt Ziel
    ↓
dedizierter create-only Writer
    ↓
finale neue Datei
```

Der Writer darf ausschließlich bereits validierten, serialisierten Inhalt erhalten.

## ExportPlan

Vor jedem späteren Write wird ein immutable Plan erzeugt.

Geplante Mindestfelder:

- Zielordner;
- finaler Dateiname;
- Format: `json | text`;
- Byte-Länge des bereits serialisierten Payloads;
- Payload-Hash für Diagnose/Evidence;
- `overwrite_allowed=False`;
- `write_enabled=False` bis zur späteren expliziten Nutzerfreigabe.

Der Plan enthält keine Rohdatenquelle und keine unredigierten Inhalte.

## Dateiname

Zulässiges Schema:

```text
PROVOWARE-Diagnose-YYYYMMDD-HHMMSS.json
PROVOWARE-Diagnose-YYYYMMDD-HHMMSS.txt
```

Nicht enthalten:

- Nutzername;
- Hostname;
- Dateiname aus Nutzerdaten;
- Recovery-ID;
- Token;
- beliebige Metadaten aus Diagnosedaten.

## Zielprüfung

Vor dem späteren Writer:

1. Zielordner existiert.
2. Zielordner ist ein echter Ordner.
3. Zielordner ist kein Symlink.
4. finaler Zielpfad liegt direkt in diesem Zielordner.
5. finaler Zielpfad existiert noch nicht.
6. kein Auto-Rename.
7. kein Overwrite.
8. keine Rechteausweitung.

Fehler => `BLOCKED`.

## Create-only / No-overwrite

Die spätere finale Datei muss create-only geöffnet werden.

Vertrag:

```text
existiert Ziel bereits
→ BLOCKED
→ kein Write
```

Kein:

- `w` auf bestehende Datei;
- `replace()`;
- `rename()` über bestehendes Ziel;
- stilles `(1)`-Suffix;
- automatische Konfliktbehebung.

## Partial-Write-Strategie

Direktes Schreiben in den finalen Dateinamen ist nicht ausreichend robust.

Geplante sichere Strategie:

1. temporäre Exportdatei **im selben Zielordner** create-only erzeugen;
2. vollständigen bereits redigierten Payload schreiben;
3. flush;
4. fsync der temporären Datei;
5. Größe/Hash gegen ExportPlan prüfen;
6. finalen Zielnamen unmittelbar vor Commit erneut auf Nicht-Existenz prüfen;
7. temporäre Datei atomar in finalen Namen überführen, **nur wenn no-overwrite garantiert ist**;
8. Verzeichnis-Metadaten soweit plattformgerecht synchronisieren;
9. Ergebnis zurückgeben.

### Kritische Einschränkung

Ein simples `os.replace()` ist **nicht zulässig**, weil es ein bestehendes Ziel überschreiben könnte.

Die spätere Implementierung muss eine create-only/no-clobber Commit-Strategie verwenden, die auf den unterstützten Zielplattformen nachweisbar ist.

Falls diese Garantie nicht portabel belegbar ist:

- Export bleibt BLOCKED;
- kein Fallback auf overwrite-fähige APIs.

## Temp-Datei

Temporäre Exportdateien:

- ausschließlich im gewählten Zielordner;
- eindeutiger, nicht sensibler Name;
- keine personenbezogenen Bestandteile;
- klar als unvollständig erkennbar;
- niemals als erfolgreicher Export gemeldet.

Beispiel:

```text
.PROVOWARE-Diagnose.partial-<random>
```

Der zufällige Anteil darf keine Nutzdaten kodieren.

## Crash / Fehler

Fehler vor finalem Commit:

- bestehende Dateien bleiben unverändert;
- finaler Exportname darf nicht existieren;
- Partial-Datei darf zurückbleiben, muss aber eindeutig als Partial erkennbar sein;
- kein automatischer Retry.

Fehler nach finalem Commit:

- Writer prüft, ob finaler Export vollständig/hash-konsistent vorliegt;
- kein zweiter Write;
- kein automatisches Überschreiben.

## Cleanup

Automatisches Cleanup einer Partial-Datei ist nur erlaubt, wenn eindeutig bewiesen ist, dass:

- sie vom aktuellen Writerlauf erzeugt wurde;
- sie nie als erfolgreicher Export veröffentlicht wurde;
- kein anderer Prozess sie übernommen hat.

Unsichere Zuordnung => nicht löschen, sondern Befund zurückgeben.

## Mehrfachstart / Race

Vor Implementierung zwingend testen:

- zwei parallele Exporte mit gleichem Zielnamen;
- Ziel entsteht zwischen Planung und Commit;
- Partial-Datei kollidiert;
- Prozessabbruch nach Create;
- Prozessabbruch nach Write;
- Prozessabbruch vor Commit.

Genau **ein** Lauf darf gewinnen. Der andere muss sauber `BLOCKED` enden.

## Payload-Vertrag

Der Writer erhält nur:

```text
serialized_payload: bytes
export_plan: ExportPlan
```

Nicht erlaubt:

- Writer baut selbst den DiagnosticReport;
- Writer redigiert erst beim Schreiben;
- Writer sammelt zusätzliche Systemdaten;
- Writer liest Logs/Dateibäume nach;
- Writer greift auf Recovery-IDs zu.

## Guard-REOPEN

Der aktuelle `read_only_guard.py` darf nicht global deaktiviert werden.

Spätere Änderung:

- explizite Allowlist **nur** für `src/provoware_laientool/diagnostic_export.py`;
- diese Datei erhält eine eigene strengere Writer-Prüfung;
- alle anderen Produktdateien bleiben unter dem bisherigen vollständigen Write-Verbot.

Die Allowlist muss:

- exakten Repository-Pfad verwenden;
- keine Verzeichnismuster erlauben;
- keine Wildcards erlauben;
- keine zweite Datei implizit freigeben.

## Writer-spezifischer Guard

Der spätere Writer-Guard muss mindestens blockieren:

- Overwrite-fähiges `open(..., "w")`;
- `Path.write_text()` / `write_bytes()`;
- `os.replace()` als finalen Commit ohne No-clobber-Beweis;
- `shutil.copy*`;
- beliebige Deletes außerhalb eigener Partial-Datei;
- Netzwerk;
- Rechteänderungen;
- freie Zielpfade ohne Planvalidierung.

## Tests vor REOPEN

Mindesttests:

1. existierendes Ziel => BLOCKED, unverändert;
2. normaler create-only Export;
3. JSON und Text;
4. Redaction bereits vor Writer;
5. Hash-/Größenabweichung => BLOCKED;
6. Symlink-Zielordner => BLOCKED;
7. Symlink-Zieldatei => BLOCKED;
8. Parallelrace gleicher Name;
9. Crash nach Partial-Create;
10. Crash nach Payload-Write;
11. Ziel entsteht kurz vor Commit;
12. Unicode-Zielordner;
13. Leerzeichen im Zielordner;
14. PermissionError;
15. voller Datenträger / ENOSPC;
16. kein Netzwerk;
17. kein Overwrite;
18. Read-only-Guard bleibt für alle anderen Module grün.

## Fehlerklassen

Writer-Fehler werden differenziert:

- `BLOCKED_TARGET_EXISTS`
- `BLOCKED_TARGET_UNSAFE`
- `BLOCKED_PAYLOAD_INVALID`
- `WRITE_PERMISSION_ERROR`
- `WRITE_NO_SPACE`
- `WRITE_PARTIAL_REMAINS`
- `WRITE_COMMIT_RACE`
- `WRITE_VERIFY_FAILED`

Keine rohe Exception als alleinige Nutzermeldung.

## Evidence

Spätere Writer-Evidence muss mindestens enthalten:

- Commit;
- Plattform/Dateisystem;
- getestetes Format;
- Zieltyp;
- Parallelrace;
- ENOSPC-Simulation;
- PermissionError;
- no-overwrite-Nachweis;
- Partial-Write-Nachweis;
- Guard-Nachweis;
- Hash/Größenprüfung;
- Ergebnis `PASS | FAIL | OPEN`.

## Nicht-Ziele von I24

- kein `diagnostic_export.py`;
- keine Guard-Allowlist;
- kein neues Registry-Feature;
- keine GUI/CLI-Exportfunktion;
- kein Dateisystem-Write;
- keine Temp-Datei;
- kein Executor;
- kein Upload/Netzwerk.

## Freeze-Entscheidung

I24 friert folgende Reihenfolge ein:

```text
I24 Design
→ späterer read-only ExportPlan/Payload-Validator
→ Writer-spezifischer Guard
→ Writer-Implementierung
→ Failure/Race/ENOSPC-Tests
→ GUI/CLI-Adapter
```

Kein Schritt darf übersprungen werden.
