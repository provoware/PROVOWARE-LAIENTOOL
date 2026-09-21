# I33 – Offline-Wheelhouse Integrität

## Status

**Supply-Chain-/Korruptionsschutz für das I32-Wheelhouse implementiert.**

## Vertrag

Ein I32 Linux-x86_64-Wheelhouse darf exakt vier Wheels enthalten:

- PySide6 6.11.2;
- PySide6_Addons 6.11.2;
- PySide6_Essentials 6.11.2;
- shiboken6 6.11.2.

Zusätzliche Distributionen, andere Versionen, doppelte Distributionen oder nicht-manylinux-x86_64 Plattformen sind fail-closed.

## Build-Gate

`build_portable_package.py` verweigert ein Offline-Paket bereits beim Build, wenn der Wheelhouse-Vertrag nicht exakt erfüllt ist.

## Archiv-Gate

`validate_portable_package.py` prüft denselben exakten Vertrag zusätzlich im fertigen ZIP.

## Runtime-Gate

Vor jedem lokalen `pip --no-index` führt `start.sh` aus:

`scripts/verify_wheelhouse_integrity.py`

Geprüft werden:

- exakte Wheel-Namen/-Versionen/-Plattformen;
- `requirements-gui.txt == PySide6==6.11.2`;
- Wheel-Anzahl;
- Manifest-Wheelliste;
- Wheel-Größen;
- Wheel-SHA-256;
- requirements-SHA-256.

Bei Abweichung wird vor der Installation beendet.

## Sicherheitsgrenze

Die Manifestprüfung erkennt Drift/Beschädigung innerhalb des Pakets. Sie ist **keine kryptografische Herkunftssignatur**, weil Manifest und Wheels gemeinsam im ZIP liegen. Der externe ZIP-SHA-256 aus der CI bleibt der unabhängige Integritätswert des Artefakts.

## Automatische Angriffs-/Fehlertests

- zusätzliches fremdes Wheel;
- falsche PySide6-Version;
- falsche Plattform;
- unvollständiges Wheelhouse;
- manipuliertes Wheel nach Extraktion;
- Runtime-Prüfung liegt vor `pip --no-index`.

## Nicht-Ziele

- Code Signing;
- GPG/Sigstore;
- ARM-Freigabe;
- Windows/macOS-Paket;
- physische Zweitgeräte-Evidence;
- Änderungen an I25/I31 Human-Gates.
