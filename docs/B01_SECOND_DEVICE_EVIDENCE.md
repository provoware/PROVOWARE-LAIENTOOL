# B01 – Zweitgeräte-Evidence-Ablauf

## Ziel

Die noch offene physische Portabilitätsprüfung wird auf einem zweiten Ubuntu-/Kubuntu-Gerät reproduzierbar durchgeführt, ohne Pakete zu installieren, Rechte zu erhöhen oder Nutzerdaten zu verändern.

## Laienweg

Im Projektordner:

```bash
./start.sh --second-device-evidence
```

Für maschinenlesbare Ausgabe:

```bash
./start.sh --second-device-evidence-json
```

Der Standardlauf schreibt **keine Datei**. Er zeigt nur einen kompakten, bereits redigierten Bericht im Terminal.

## Herkunftsidentität

Der Runner ermittelt die Herkunft fail-closed und ohne Netz:

1. in einem Portable-Paket den 40-stelligen Commit aus `PACKAGE_MANIFEST.json`;
2. in einem echten Git-Checkout den lokalen `HEAD`;
3. wenn beides nicht verfügbar ist, einen ausdrücklich als Fallback gekennzeichneten SHA-256-Fingerprint von `start.py`.

Existiert ein Paketmanifest, enthält aber keinen gültigen Commit, wird der Evidence-Lauf **FAIL** statt auf eine schwächere Identität zurückzufallen. Damit kann ein beschädigtes oder widersprüchliches Portable-Paket nicht versehentlich als sauberer Nachweis gelten.

## Bewertung

- `PASS`: beide Preflight-Pfade liefen reproduzierbar, die JSON-Ausgabe war lesbar und die Herkunftsidentität war gültig.
- `FAIL`: der Evidence-Lauf selbst oder die Herkunftsprüfung ist technisch fehlgeschlagen.
- Ein Preflight-Profil `blocked-readonly` ist **kein automatischer Evidence-FAIL**. Es bedeutet: Gerät wurde korrekt erkannt, aber mindestens eine Voraussetzung ist dort offen.

## Datenschutz

Der Evidence-Runner übernimmt nur eine feste Menge unkritischer Capability-Felder. Vollständige Home-/Downloads-/Projektpfade werden nicht in den Bericht übernommen. Commit und SHA-256-Fingerprint enthalten keine lokalen Pfade.

## Übernahme als Evidence

Den vollständigen Terminalbericht oder die JSON-Ausgabe in die spätere Zweitgeräte-Evidence übernehmen und ergänzen:

- Gerät / Distribution / Version;
- Datum und Zeitzone;
- automatisch ermittelter Commit/Fingerprint;
- Ergebnis;
- offene Voraussetzungen;
- Abweichungen zur ersten Zielmaschine.

## Sicherheitsgrenzen

- kein Netzwerk;
- keine Paketinstallation;
- kein sudo;
- keine Rechteänderung;
- keine Änderung an Nutzerdaten;
- keine automatische Konfigurationsmigration.
