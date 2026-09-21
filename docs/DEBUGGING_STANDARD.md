# PROVOWARE – Debugging- und Befundstandard

## Ziel

Fehler schnell dem richtigen Layer zuordnen, ohne vorschnelle Selbstreparatur oder Scope-Drift.

## Fehlerklassen

### PRODUCT

Der Produktvertrag ist verletzt.

Beispiele:

- falsches fachliches Ergebnis;
- Sicherheitsgrenze umgangen;
- Regression im Application-/Domain-Core;
- unerwartete Dateiänderung.

### TEST

Produktvertrag ist korrekt, aber Testannahme, Fixture oder Testcode ist fehlerhaft/veraltet.

Tests dürfen nur nach belegter Ursachenanalyse geändert werden.

### INFRASTRUCTURE

Fehler liegt außerhalb des Produktvertrags.

Beispiele:

- GitHub-Runner;
- Checkout;
- fehlende externe Capability;
- Display-/PySide6-Umgebung für reale Evidence.

### EVIDENCE

Automatisierte Technik ist grün, aber eine reale Wahrnehmungs-/Hardwareprüfung fehlt oder ist unvollständig.

Beispiel: I17 echter Desktoplauf.

## Triage-Reihenfolge

```text
1. exakten fehlgeschlagenen Gate lesen
2. ersten ursächlichen Fehler bestimmen
3. Fehlerklasse zuordnen
4. kleinsten reproduzierbaren Pfad isolieren
5. nur zuständigen Layer ändern
6. targeted Test
7. Cross-Core nur wenn relevant
8. Full Suite
9. Diff
10. Merge/Post-Merge
```

Keine Kaskaden-Patches auf Basis von Folgefehlern.

## Pflichtangaben eines Debug-Befunds

- Commit/Branch;
- exakter Gate-/Testname;
- Fehlerklasse;
- erwartetes Verhalten;
- beobachtetes Verhalten;
- kleinster reproduzierbarer Fall;
- betroffener Layer;
- geänderte Dateien;
- Regressionstest oder Evidence-Anweisung;
- verbleibendes Risiko.

## Read-only-Lock

`scripts/read_only_guard.py` ist ein statischer Frühwarn-Gate solange produktive Schreibpfade gesperrt sind.

Er blockiert unter anderem:

- typische `pathlib`-Schreibmethoden;
- `os`-/`shutil`-Schreiboperationen;
- schreibende `open()`-Modi;
- Import-Aliase solcher APIs;
- dynamische `open()`-Modi, die nicht statisch als read-only belegbar sind.

Ein späterer Executor darf diesen Guard nicht beiläufig umgehen. Die Öffnung des Schreibpfads benötigt einen ausdrücklichen Gate-/Vertragswechsel.

## Core Diagnostic

`scripts/core_diagnostics.py` ist ein datensparsamer End-to-End-Smoke.

Er darf:

- nur temporäre Dateien verwenden;
- Pfad-/Inventar-/View-/Preview-Verträge gemeinsam prüfen;
- Klartext und JSON liefern.

Er darf nicht:

- reale Nutzerordner scannen;
- Netzwerk verwenden;
- Installationen durchführen;
- Produktfehler automatisch reparieren;
- reale GUI-Evidence ersetzen.

## Diagnose-Snapshot

`scripts/diagnostic_snapshot.py` liefert einen read-only Bericht auf stdout.

Verbindlich:

- Redaction vor Ausgabe;
- keine Recovery-IDs;
- keine Datei-Persistenz;
- kein Upload/Netzwerk;
- Collection-Status und Health-Status getrennt;
- Ausgabe als Klartext oder JSON.

Der Snapshot ist Diagnosehilfe, kein automatischer Reparaturmechanismus.

## Datenschutz

Logs und Evidence vermeiden:

- reale Home-Pfade;
- persönliche Dateinamen;
- Secrets;
- komplette Umgebungsdumps ohne Bedarf.

Bei notwendigen Pfadangaben bevorzugt redigieren oder temporäre reproduzierbare Fixtures verwenden.

## Begrenzte Ausführung und Anti-Schleifen-Regel

Debugging darf nicht in eine unbegrenzte Reparatur- oder Testschleife übergehen.

### Laufzeitgrenzen

- CI-Jobs erhalten ein festes `timeout-minutes`.
- Lokale Tests/Diagnosen werden mit einer angemessenen Zeitgrenze gestartet; für den aktuellen kleinen Repository-Stand sind 2 Minuten pro Einzelgate und 5 Minuten für die vollständige Testsuite der Standard.
- Ein legitimer Test, der mehr Zeit benötigt, bekommt eine **begründete, dokumentierte Ausnahme** statt eines pauschal höheren Limits.
- Exit-Code `124` eines GNU-`timeout`-Aufrufs bedeutet **TIMEOUT/INFRASTRUCTURE bis zur Ursachenklärung**, nicht automatisch PRODUCT.

### Wiederholungsbudget

1. Erster Fehlerlauf: Ursache klassifizieren.
2. Ein identischer zweiter Lauf ist nur zur Reproduktionsbestätigung erlaubt.
3. Ohne Zustandsänderung gibt es keinen dritten identischen Lauf.
4. Pro bestätigter Root Cause höchstens zwei gezielte Reparaturzyklen.
5. Danach: STOP, Befund dokumentieren, Scope/Plan neu bestimmen.

### Testökonomie

`targeted → relevantes Cross-Core-Gate → Full Suite → CI`

- Full Suite nicht als Suchwerkzeug verwenden.
- Nach einem Full-Suite-Fehler zuerst den kleinsten fehlgeschlagenen Test isolieren.
- Nach reiner Doku-/Prozessänderung keine fachfremden Produkt-Smokes hinzufügen.
- Keine "vorsorglichen" Testwiederholungen bei bereits grünem, unverändertem Stand.
- Flaky-Verhalten wird als Befund behandelt; es wird nicht durch automatische Wiederholung verdeckt.

## Stop-Regel

Ein VERIFY-/Diagnose-Schritt darf einen gefundenen Produktfehler nicht im selben Prüferauftrag heimlich reparieren.

Befund → Klasse → expliziter nächster Write-Batch.


## Diagnose-Export – künftige Writer-Triage

Ein späterer Diagnose-Export ist ein bewusst eng begrenzter Sonderfall zum allgemeinen Read-only-Lock.

Vor jedem Writer-REOPEN gilt:

1. Redaction/Payload-Validierung muss bereits vor dem Write abgeschlossen sein.
2. Bestehende Zieldateien dürfen niemals verändert werden.
3. Partial-Write, ENOSPC, PermissionError und Parallelrace sind eigenständige Pflichtbefunde.
4. Ein Writer-Fehler darf nicht automatisch erneut schreiben.
5. Eine zurückgebliebene Partial-Datei ist ein sichtbarer Befund und kein erfolgreicher Export.
6. Der allgemeine Produktkern bleibt weiterhin read-only.

Die vollständige Writer-Architektur steht in `docs/I24_DIAGNOSTIC_EXPORT_WRITER_DESIGN.md`.
