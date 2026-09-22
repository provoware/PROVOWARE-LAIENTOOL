# PROVOWARE – Aktueller Arbeitsblock

## I39 – Zweitgeräte-Herkunftsidentität

**Status:** 🟢 ABGESCHLOSSEN
**Fortschritt:** `██████████ 100 %`
**Produktfreigabe:** unverändert; Zweitgeräte- und Human-Gates bleiben offen

## Ergebnis

- der P0-Zweitgeräte-Nachweis besitzt jetzt eine eindeutige, offline ermittelte Herkunftsidentität;
- Portable-Pakete verwenden bevorzugt den 40-stelligen Commit aus `PACKAGE_MANIFEST.json`;
- echte Git-Checkouts verwenden den lokalen `HEAD`;
- ohne Manifest und ohne `.git` bleibt ein ausdrücklich gekennzeichneter SHA-256-Fingerprint von `start.py`;
- ein vorhandenes, aber ungültiges Paketmanifest führt fail-closed zu `FAIL`;
- Manifest-, Git-, Fallback- und Invalid-Manifest-Pfade sind regressionsgetestet;
- PR #59 wurde per Squash nach `main` gemergt;
- Post-Merge-`repo-quality` ist vollständig grün.

## Verifizierter Abschlusszustand

- `main`: `6d038c6fce5e16067623ad3d0590852a75dfe62a`
- Remote-Branches nach I39-Merge: ausschließlich `main`
- keine GUI-Änderung
- keine Dateioperation
- keine neue Paketarchitektur
- keine Änderung an Schreibfreigaben
- kein tatsächlicher Zweitgeräte-PASS ohne zweites Gerät

## Nächster verbindlicher Schritt

**P0 – realer Zweitgeräte-Nachweis**

Auf einem zweiten Ubuntu-/Kubuntu-Gerät im Projektordner genau einmal:

```bash
./start.sh --second-device-evidence-json
```

Den vollständigen redigierten JSON-Bericht als Evidence übernehmen. Erst ein realer zweiter Zielrechner kann dieses P0-Gate schließen.

Danach folgen weiterhin:

1. P1 – einmalige Human-Abnahme für Kopieren/Verschieben über `./start.sh --i25-evidence`;
2. P1 – einmalige Human-Abnahme für Diagnose-Datei über `./start.sh --i31-evidence`;
3. P2 – Erscheinungsbild nur gemeinsam mit der nächsten sichtbaren Bedienänderung nachschärfen.
