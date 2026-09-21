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

## Bewertung

- `PASS`: beide Preflight-Pfade liefen reproduzierbar und die JSON-Ausgabe war lesbar.
- `FAIL`: der Evidence-Lauf selbst ist technisch fehlgeschlagen.
- Ein Preflight-Profil `blocked-readonly` ist **kein automatischer Evidence-FAIL**. Es bedeutet: Gerät wurde korrekt erkannt, aber mindestens eine Voraussetzung ist dort offen.

## Datenschutz

Der Evidence-Runner übernimmt nur eine feste Menge unkritischer Capability-Felder. Vollständige Home-/Downloads-/Projektpfade werden nicht in den Bericht übernommen.

## Übernahme als Evidence

Den vollständigen Terminalbericht oder die JSON-Ausgabe in die spätere Zweitgeräte-Evidence übernehmen und ergänzen:

- Gerät / Distribution / Version;
- Datum und Zeitzone;
- Commit/Fingerprint;
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
