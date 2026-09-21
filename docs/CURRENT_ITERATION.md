# PROVOWARE – Current Iteration

## I22 – Diagnose-Export Decision Gate

**Status:** 🟨 ENTSCHEIDUNG DOKUMENTIERT / CI-ABNAHME AUSSTEHEND
**Fortschritt:** `████████░░ 80 %`

## A – FESTER PLAN

**Ziel:** entscheiden, ob und unter welchen harten Grenzen ein späterer redigierter Diagnosebericht lokal als Datei exportiert werden darf.

**Entscheidung:**

- 🟢 späterer expliziter lokaler Export grundsätzlich zulässig
- 🟢 nur nach ausdrücklicher Nutzeraktion
- 🟢 Redaction zwingend vor jedem Write
- 🟢 nur bestehender `DiagnosticReport`
- 🟢 zunächst JSON/Klartext
- 🟢 explizit gewählter vorhandener Zielordner
- 🟢 no-overwrite
- 🟢 keine automatische Konfliktumbenennung
- 🟢 keine automatische Rechteausweitung
- 🟢 eigener Writer-/REOPEN-Gate erforderlich
- 🟢 Read-only-Guard darf nicht global abgeschaltet werden
- 🟢 Partial-Write-/Crash-Strategie vor Implementierung Pflicht
- 🔒 heute keine Implementierung
- 🔒 kein Upload/Netzwerk
- 🔒 keine Telemetrie
- 🔒 keine Crash-Dumps
- 🔒 keine Log-Bundles
- 🔒 kein allgemeiner Writer

## B – VARIABLE FOLGEAUFGABE

**Quelle letzter Lauf:** I21 wurde gemergt und Post-Merge-CI vollständig grün, während `CURRENT_ITERATION.md` Merge/Post-Merge noch als offen auswies.

**Maßnahme:** Statusdrift beim Wechsel auf I22 synchronisiert.

**Status:** 🟢 erledigt.

## Warum der Read-only-Lock unverändert bleibt

I22 ist ausschließlich ein Decision Gate.

Ein späterer Export-Writer benötigt einen **gezielten REOPEN**, der nur diesen kleinen Writer-Bereich erlaubt. Der allgemeine Produktkern bleibt weiter read-only und der Guard darf nicht global abgeschaltet werden.

## Nicht-Ziele

- keine Exportfunktion;
- keine Datei schreiben;
- keine Registry-Änderung;
- keine GUI-/CLI-Erweiterung;
- keine Guard-Allowlist;
- keine atomare Writer-Implementierung;
- kein Netzwerk;
- kein Upload;
- keine Telemetrie;
- kein Executor.

## Exit-Gates

1. Exportgrenzen eindeutig dokumentiert.
2. Datenschutz-/Redaction-Reihenfolge eindeutig.
3. no-overwrite eingefroren.
4. Writer-/Guard-REOPEN ausdrücklich als späteres Pflichtgate dokumentiert.
5. Repository-Contract PASS.
6. Info-Text-Impact PASS.
7. vollständige Regression-Suite PASS.
8. Read-only-Lock unverändert PASS.
9. finaler Diff ohne Scope-Drift.
10. Post-Merge-CI PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I23 – Same-Root Zielauswahl Adapter-Decision
Entscheiden, wie vorhandene I18-Auswahl und I21-Zielpreview später laiengerecht in GUI/Zahlenmenü angebunden werden. Reale I17-Evidence bleibt Voraussetzung für sichtbaren GUI-Ausbau.

### 2. 🔵 I24 – Diagnose-Export Writer Design
Nur wenn ausdrücklich freigegeben: atomare/create-only Writer-Strategie und Guard-REOPEN als reine technische Planung; noch keine Implementierung.

### 3. 🔵 I17-B – realer GUI-Zielsystemlauf
100/150/200 %, Tastatur, Fokus und Screenshots weiterhin auf echter PySide6-/Desktop-Umgebung abschließen.
