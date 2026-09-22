# I39 – Zweitgeräte-Herkunftsidentität

## Status

**Kleiner P0-Evidence-Hardening-Block. Produktfreigabe bleibt unverändert.**

## Problem

Der B01-Zweitgeräte-Runner lieferte bereits einen SHA-256-Wert von `start.py`, der Evidence-Vertrag verlangt jedoch explizit Commit/Fingerprint. Bei einem Portable-Paket existiert normalerweise kein `.git`; bei einem Git-Checkout ist dagegen der lokale `HEAD` die präzisere Identität.

## Vertrag

Die Herkunft wird in dieser Reihenfolge bestimmt:

1. `PACKAGE_MANIFEST.json` mit exakt 40-stelligem Commit;
2. lokaler Git-`HEAD`, aber nur wenn im Projektwurzelverzeichnis tatsächlich `.git` existiert;
3. SHA-256 von `start.py` als ausdrücklich gekennzeichneter Fallback.

Ein vorhandenes, aber ungültiges Paketmanifest ist ein harter Fehler. Es wird nicht still auf Git oder Fingerprint zurückgefallen.

## Sicherheitsnutzen

- kein versehentliches Vertrauen in ein beschädigtes Portable-Manifest;
- keine falsche Git-Zuordnung über ein übergeordnetes Repository;
- reproduzierbare Identität auch ohne Git-Metadaten;
- keine Netzwerkabfrage und keine Secret-/Pfadausgabe.

## Non-Goals

- keine kryptografische Signatur;
- keine Änderung am I35-Provenienzmodell;
- keine Paketinstallation;
- keine Produkt- oder Executor-Änderung;
- kein Ersatz für den realen Zweitgeräte-Lauf.

## Exit-Gates

- Manifest-, Git-, Fallback- und Invalid-Manifest-Tests grün;
- Repository-Quality vollständig grün;
- Review-Diff bleibt auf Evidence-Herkunft und Dokumentation begrenzt.
