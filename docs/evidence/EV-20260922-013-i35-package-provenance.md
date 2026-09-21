# EV-20260922-013 – I35 Portable Artifact Provenance

## Evidence-ID

EV-20260922-013

## Datum/Uhrzeit

2026-09-22 · Europe/Berlin

## RC/Fingerprint

`98920d7af0d16c986c26742e859ca6f41fa18fed`

Basis: `82277df5d9154720692fcac623c25d7b42f8c931`

## Ziel

Die vorhandenen I32/I33-Releasefakten fail-closed miteinander binden: Git-Commit, Manifest, Paketwurzel, ZIP-Dateiname, SHA-256-Sidecar und tatsächliche ZIP-Bytes.

## Automatische Nachweise

GitHub Actions:

- `repo-quality` Run `35669027831`: **PASS**
- `portable-package` Run `35669027832`: **PASS**

## I35 Matrix

Automatisch belegt:

- Builder akzeptiert nur exakten 40-stelligen Git-SHA;
- Manifest-Commit und Plattform bestimmen die Paketwurzel;
- Paketwurzel und ZIP-Dateiname müssen exakt übereinstimmen;
- bloß umbenanntes ZIP wird blockiert;
- `.zip.sha256` bindet tatsächlichen Hash und exakten ZIP-Dateinamen;
- manipuliertes Sidecar wird blockiert;
- Manifest-/Root-Mismatch wird blockiert;
- Offline-Wheelhouse bleibt auf `linux-x86_64` begrenzt;
- echter Offline-Bootstrap im CI bleibt PASS.

## Paketartefakt

- Name: `portable-package-98920d7af0d16c986c26742e859ca6f41fa18fed`
- Größe: 253895260 Byte
- CI-Artefakt-Digest: `sha256:092cbbded546671101c0ee7a620d6693474c64347fb6a3de0b29596170f78f52`
- Aufbewahrung: 7 Tage

## Sicherheitsgrenze

I35 ist **keine digitale Signatur und keine Herkunftsauthentisierung gegen gemeinsames Ersetzen von ZIP und Sidecar**. Eine kryptografische Release-Signatur benötigt einen separaten Trust-/Key-Management-Block.

## Status

**PASS** – I35 ist freeze-bereit.
