# I35 – Portable Artifact Provenance Binding

## Status

**Commit-/Manifest-/Paketname-/Checksum-Bindung implementiert. Keine Signaturbehauptung.**

## Ziel

Die bereits vorhandenen I32/I33-Paketfakten werden fail-closed miteinander verknüpft:

```text
Git-Commit
→ PACKAGE_MANIFEST.json
→ Paketwurzel
→ ZIP-Dateiname
→ .zip.sha256
→ tatsächliche ZIP-Bytes
```

## Commit-Vertrag

Der Builder akzeptiert ausschließlich einen exakt 40-stelligen hexadezimalen Git-SHA-1. Freie Versionswörter oder verkürzte Identifikatoren sind für das Paketmanifest nicht zulässig.

## Paketwurzel und ZIP-Name

Aus Manifest-Commit und Plattform entsteht deterministisch:

```text
PROVOWARE-LAIENTOOL-<commit[:12]>-<platform_tag>
```

Die einzige ZIP-Wurzel und der ZIP-Dateiname müssen exakt dazu passen.

Ein bloß umbenanntes ZIP wird dadurch als Provenienzabweichung erkannt, auch wenn seine Bytes unverändert sind.

## Checksum-Sidecar

Der Validator kann die bereits erzeugte `.zip.sha256`-Datei mitprüfen.

Er erwartet exakt:

```text
<sha256-des-zip>  <exakter-zip-dateiname>
```

Hash oder Dateiname abweichend → FAIL.

## Offline-Plattform

Wenn `--require-wheelhouse` aktiv ist, ist der Paketvertrag weiterhin ausschließlich:

`linux-x86_64`

Andere Plattformtags werden fail-closed abgelehnt.

## Automatische Manipulationstests

- ungültiger Commit-Identifier beim Build;
- gültiges ZIP + gültiges Sidecar;
- unveränderte ZIP-Bytes unter falschem Dateinamen;
- manipuliertes Checksum-Sidecar;
- Manifest-Commit ↔ Paketwurzel-Mismatch;
- Manifest-Commit ↔ ZIP-Name-Mismatch;
- Offline-Wheelhouse mit nicht freigegebener Plattform.

## Sicherheitsgrenze

I35 ist **keine digitale Signatur und kein Herkunftsnachweis gegenüber einem Angreifer, der ZIP und Sidecar gemeinsam ersetzen kann**.

Es verbessert die interne Provenienz- und Konsistenzbindung. Eine spätere kryptografische Release-Signatur benötigt einen separaten Trust-/Key-Management-Entscheid.
