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

## Datenschutz

Logs und Evidence vermeiden:

- reale Home-Pfade;
- persönliche Dateinamen;
- Secrets;
- komplette Umgebungsdumps ohne Bedarf.

Bei notwendigen Pfadangaben bevorzugt redigieren oder temporäre reproduzierbare Fixtures verwenden.

## Stop-Regel

Ein VERIFY-/Diagnose-Schritt darf einen gefundenen Produktfehler nicht im selben Prüferauftrag heimlich reparieren.

Befund → Klasse → expliziter nächster Write-Batch.
