# EV-20260922-011 – I33 Offline-Wheelhouse Supply-Chain-Lock

## Evidence-ID

EV-20260922-011

## Datum/Uhrzeit

2026-09-22 · Europe/Berlin

## geprüfter Source-Head

`453b8bdecfa5b9f4320a2d25884f62b22a43379a`

Basis: `a0454749ad4c702f15cc3418fc4a439109002a0a`

## Ziel

Den I32 Linux-x86_64-Offline-Paketpfad vor unerwarteten oder veränderten Wheel-Dateien schützen und dieselbe Lockprüfung vor Build, nach Extraktion und vor lokaler Installation erzwingen.

## Lockbaseline

Requirements-SHA-256:

`385e039f43c455549f3e79039a7b68169284eac3f18a35e0db4fa5ebdec01e44`

Erlaubte Wheels:

1. `pyside6-6.11.2-cp310-abi3-manylinux_2_34_x86_64.whl`
   - Größe: 572120 Byte
   - SHA-256: `dc6d03990489a5085842770718392ef5de36352d8f608d9a9fe03e60af4d7b66`
2. `pyside6_addons-6.11.2-cp310-abi3-manylinux_2_34_x86_64.whl`
   - Größe: 175062576 Byte
   - SHA-256: `a8b00956925fbdeffc7052cf933506391289f35ac4f3f71a0a167ec195cd47b4`
3. `pyside6_essentials-6.11.2-cp310-abi3-manylinux_2_34_x86_64.whl`
   - Größe: 80108947 Byte
   - SHA-256: `aaf9f25f0f324874085fa5b26a610318db8a8e243cf85bb3e5400595191c7778`
4. `shiboken6-6.11.2-cp310-abi3-manylinux_2_34_x86_64.whl`
   - Größe: 272435 Byte
   - SHA-256: `7a7a0a72a9ed26c9bf77d42246b1c736486befb8f31aa2fb29957ea4cdd1c1c2`

## Automatische Nachweise

GitHub Actions:

- `repo-quality` Run `35668063896`: **PASS**
- `portable-package` Run `35668063766`: **PASS**
- `i31-export-evidence` Run `35668063798`: **PASS**
- `i25-gui-evidence` Run `35668063796`: **PASS**

Der Portable-Package-Run bestätigte in dieser Reihenfolge:

1. exakten Source-Head Checkout;
2. Download der gepinnten PySide6-Abhängigkeiten;
3. **Verifikation der heruntergeladenen Wheels gegen den committed Lock: PASS**;
4. deterministischen ZIP-Build;
5. erneute Lockprüfung nach Extraktion;
6. `start.sh`-Lockprüfung vor Offline-pip;
7. Offline-Bootstrap mit `PIP_NO_INDEX=1`;
8. anschließenden `start.sh --check`.

## Negative Regressionen

Automatisch getestet:

- manipuliertes Wheel → FAIL;
- zusätzliches Wheel → FAIL;
- fehlendes Wheel → FAIL;
- geänderte Requirements → FAIL;
- ungültige Größe/Hash → FAIL.

## Reparaturbefund

Der erste RC-Lauf fand ausschließlich einen Python-Import-Kontextfehler im Paketvalidator:

- direkter Skriptstart benötigte absoluten Nachbarimport;
- Unittest-Modulimport benötigte relativen Paketimport.

Die Korrektur unterstützt beide Kontexte. Sicherheits-/Lockdaten wurden dabei nicht geändert.

## CI-Artefakt

- Name: `portable-package-453b8bdecfa5b9f4320a2d25884f62b22a43379a`
- Größe: 253889290 Byte
- Digest: `sha256:3cf82ca91e2ee2f2c9bb263bad390392e5b8d96e65d7603ad18fd0e861c6fe8d`
- Aufbewahrung: 7 Tage

## Sicherheitsgrenze

- Lock wird niemals automatisch aktualisiert;
- unbekannte Extra-Wheels werden nicht installiert;
- Lockfehler führt nicht zu PyPI-Fallback;
- keine ARM-Freigabe;
- keine Änderung an produktiven Write-/READY-Zuständen.

## Status

**PASS**
