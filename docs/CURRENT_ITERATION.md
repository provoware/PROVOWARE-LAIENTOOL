# PROVOWARE – Aktueller Arbeitsblock

## I39 – Zweitgeräte-Herkunftsidentität

**Status:** 🟡 AUTOMATISCHE ABNAHME LÄUFT
**Fortschritt:** `████████░░ 80 %`
**Produktfreigabe:** unverändert; Zweitgeräte- und Human-Gates bleiben offen

## A – Fester Plan

1. den P0-Zweitgeräte-Nachweis vor dem realen Lauf auf eine eindeutige Herkunftsidentität härten;
2. Portable-Paket-Commit, Git-Checkout-Commit und klar gekennzeichneten Fingerprint-Fallback unterscheiden;
3. ein vorhandenes, aber ungültiges Paketmanifest fail-closed behandeln;
4. ausschließlich den Evidence-Pfad ändern – keine Produktlogik und keine Schreibfreigabe.

## Ergebnis im Branch

- `PACKAGE_MANIFEST.json` ist für Portable-Pakete die bevorzugte Commit-Quelle;
- ein echter Git-Checkout nutzt ausschließlich seinen lokalen `HEAD`;
- ohne Manifest und ohne `.git` bleibt ein SHA-256-Fingerprint von `start.py`;
- ein ungültiges vorhandenes Paketmanifest führt zu `FAIL`;
- gezielte Regressionstests decken alle Identitätswege ab;
- B01-Dokumentation beschreibt die Priorität und den Fail-closed-Fall.

## Exit-Gates

1. gezielte Tests für `test_second_device_evidence.py` grün;
2. vollständiges `repo-quality` grün;
3. genau ein Remote-Head und Review-Diff ohne Scope-Ausweitung;
4. danach Squash-Merge und Post-Merge-Quality;
5. erst anschließend realer P0-Lauf auf einem zweiten Ubuntu-/Kubuntu-Gerät.

## Nicht Teil von I39

- kein tatsächlicher Zweitgeräte-PASS ohne zweites Gerät;
- keine GUI-Änderung;
- keine Dateioperationen;
- keine neue Paketarchitektur;
- keine automatische Freigabe von Kopieren, Verschieben oder Diagnose-Datei.
