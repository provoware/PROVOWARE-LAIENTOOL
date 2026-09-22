# PROVOWARE – Aktueller Arbeitsblock

## I37 – Repository-Hygiene Deep Cleanup

**Status:** 🟡 AUTOMATISCHE ABNAHME LÄUFT
**Fortschritt:** `████████░░ 80 %`
**Produktfreigabe:** unverändert; bestehende Human-/Zweitgeräte-Gates bleiben offen

## A – Fester Plan

1. acht Altbranches gegen `main`, PRs und Unique-Commits prüfen;
2. entbehrliche/superseded Pfade eindeutig klassifizieren;
3. `scripts/repo_quality.py` regressionsneutral modularisieren.

## B – Neuer Befund

`security/i33-offline-wheelhouse-lock` enthält eine auf `main` fehlende vorab festgeschriebene SHA-256-Baseline für die vier Offline-Wheels. Dieser Branch bleibt bis zur separaten Übernahme dieser Sicherheitsinvariante geschützt.

## Ergebnis bisher

- 7 von 8 Altbranches fachlich als entbehrlich oder superseded klassifiziert;
- I33 bewusst **nicht** aussortiert;
- redundanter PR #43 bereits geschlossen;
- derzeit keine offenen Alt-Integrations-PRs;
- Repository-Gate in fünf Prüffamilien zerlegt, Einstieg `scripts/repo_quality.py` bleibt stabil.

## Grenzen

- keine Produktlogik;
- kein Executor;
- keine Änderung an Schreibfreigaben;
- kein Löschen eines Branches mit nicht übernommener Sicherheitsinvariante.

## Nächste drei Schritte

1. 🔵 I37-Refactor durch Repository-CI vollständig regressionsprüfen.
2. 🔵 Nach grünem Merge den I33-P0-Salvage als frischen Security-Block auf aktuellem `main` eröffnen.
3. 🔵 Danach die sieben als entbehrlich klassifizierten Altbranches endgültig aus der Remote-Branchliste entfernen.
