# EV-20260922-011 – I33 Offline-Wheelhouse Integrität

## Evidence-ID

EV-20260922-011

## Datum/Uhrzeit

2026-09-22 · Europe/Berlin

## RC/Fingerprint

`2ed2d09cf60d88617997edbaca1c2c6d97e33e77`

Basis: `a0454749ad4c702f15cc3418fc4a439109002a0a`

## Ziel

Den I32 Linux-x86_64-Offlinepfad gegen zusätzliche Wheels, Versions-/Plattformdrift und beschädigte Wheel-Dateien härten.

## Automatische Nachweise

GitHub Actions:

- `repo-quality` Run `35668007126`: **PASS**
- `portable-package` Run `35668007152`: **PASS**
- `i31-export-evidence` Run `35668007137`: **PASS**
- `i25-gui-evidence` Run `35668007131`: **PASS**

## I33 Sicherheitsmatrix

Automatisch belegt:

- exakt vier erlaubte Distributionen;
- exakt Version 6.11.2;
- manylinux-x86_64 Pflicht;
- zusätzliche Distribution blockiert;
- falsche Version blockiert;
- falsche Plattform blockiert;
- unvollständiges Wheelhouse blockiert;
- Builder verweigert ungültiges Wheelhouse;
- fertiges ZIP prüft denselben Exact-Set-Vertrag;
- Runtime prüft Wheel-Namen, Requirements-Hash, Manifestliste, Größen und SHA-256;
- manipuliertes Wheel wird vor Installation erkannt;
- Integritätsprüfung liegt vor `pip --no-index`;
- Offline-Bootstrap im Fremdpfad bleibt PASS.

## Paketartefakt

- Name: `portable-package-2ed2d09cf60d88617997edbaca1c2c6d97e33e77`
- Größe: 253888938 Byte
- Artefakt-Digest: `sha256:a728941a16a0706c6dac053e1aeb6f3909c973b871aca616f14aa76be9294573`
- Aufbewahrung: 7 Tage

## Sicherheitsgrenze

Die Manifest-/Hashprüfung ist **Konsistenz- und Korruptionsschutz**, keine Herkunftsauthentisierung. Manifest und Wheels liegen im selben ZIP. Der externe CI-Artefakt-Digest bleibt ein separater Integritätswert; Code Signing ist nicht Bestandteil von I33.

## Status

**PASS** – I33 ist freeze-bereit.
