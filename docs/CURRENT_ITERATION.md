# PROVOWARE – Aktueller Arbeitsblock

## I38 – Vorab festgeschriebene Wheelhouse-Baseline

**Status:** 🟡 AUTOMATISCHE ABNAHME LÄUFT
**Fortschritt:** `████████░░ 80 %`
**Produktfreigabe:** unverändert; bestehende Human-/Zweitgeräte-Gates bleiben offen

## A – Fester Plan

1. I37-Sicherheitsfund aus `security/i33-offline-wheelhouse-lock` isoliert übernehmen;
2. exakte Wheel-Datei-/Größen-/SHA-256-Baseline vor den bestehenden Paketbau setzen;
3. erst nach grünem I38-CI die alten Remote-Branches endgültig bereinigen.

## Ergebnis bisher

- feste Linux-x86_64-Baseline eingecheckt;
- eigener dependency-freier Baseline-Prüfer;
- Paketworkflow prüft die Baseline direkt nach `pip download` und vor dem ZIP-Build;
- bestehende I32/I33-Builder-, Manifest- und Runtime-Prüfungen bleiben unverändert;
- Negativtests für manipuliertes Wheel, Zusatz-Wheel und Requirements-Drift ergänzt.

## Grenzen

- keine neue Paketarchitektur;
- keine Änderung an Produktlogik oder Schreibfreigaben;
- kein automatisches Umschreiben der Baseline;
- keine Branch-Löschung vor grünem I38.

## Nächste Schritte

1. 🔵 I38 durch Repository- und Portable-Package-CI prüfen.
2. 🔵 Bei Grün per Squash nach `main` mergen.
3. 🔵 Danach die sieben superseded Altbranches und zuletzt `security/i33-offline-wheelhouse-lock` entfernen.
