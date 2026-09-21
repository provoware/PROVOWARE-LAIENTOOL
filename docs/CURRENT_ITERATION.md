# PROVOWARE – Current Iteration

## I25 – Adapter-Implementierung nach grünem I17-Freeze

**Status:** 🔵 FREIGEGEBEN FÜR PLANUNG
**Fortschritt:** `░░░░░░░░░░ 0 %`

## Abgeschlossener Vorgänger

### I17-D – Automated Qt Evidence

**Status:** 🟢 FROZEN PASS

- I17-AUTO: PASS;
- I17-HUMAN: PASS;
- realer Chromium-Zielsystemlauf: PASS;
- bestätigter Lauf auf Commit `1678f050083f9e172fd9122f2808b0a7c45dea05`;
- Legacy-I17-B-Helfer nach erfolgreichem Ersatz entfernt;
- kosmetischer Wunsch „größere Schrift / mehr Farbe“ als `UX-POLISH-01` ausgelagert, ohne I17 wieder zu öffnen.

## A – FESTER PLAN

**Ziel:** Den eingefrorenen I23-Adaptervertrag als kleinsten sichtbaren Funktionsblock umsetzen.

Erlaubter Scope:

- I18-Auswahl fachlich über gemeinsamen Application-Core;
- I21 Copy-/Move-Preview anbinden;
- GUI und Zahlenmenü verwenden denselben Core;
- Same-Root bleibt Pflicht;
- kein Executor;
- kein Overwrite;
- keine externe Zielwurzel;
- kein produktiver Datei-Write.

## B – VARIABLE FOLGEAUFGABE

**Quelle:** Repository-Hygiene nach I17-D.

- `start.sh` bleibt einziger offizieller Nutzer-Einstiegspunkt;
- Zweitgeräte-Evidence wird ebenfalls über `start.sh` geführt;
- I17-Legacy-Code ist kein aktiver Rückfallpfad mehr;
- alte Remote-Branches bleiben eine separate Repository-Verwaltungsaufgabe.

## Exit-Gates für I25

1. Scope/Non-Goals vor Implementierung festschreiben.
2. Gemeinsamer Application-Pfad.
3. GUI-/CLI-Parität.
4. targeted Tests zuerst.
5. Read-only-Lock PASS.
6. vollständige Suite PASS.
7. Pflichtcheck `repository-contract` PASS.
8. Post-Merge-CI PASS.
9. kein Executor-/Writer-REOPEN.

## Nächste drei Schritte

1. 🔵 I25-Scope aus I23/I18/I21 exakt auflösen.
2. 🔵 kleinsten GUI-/CLI-Adapterblock implementieren, weiterhin nur Preview.
3. 🔵 `UX-POLISH-01` später separat: Chromium-Evidence-Schrift etwa 10–15 % größer und etwas mehr Akzentfarbe, ohne funktionales Gate.
