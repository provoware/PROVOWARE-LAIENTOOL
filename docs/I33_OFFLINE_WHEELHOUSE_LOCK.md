# I33 – Offline-Wheelhouse Supply-Chain-Lock

## Status

**Exakter Wheel-Datei-/Hash-Vertrag für das I32 Linux-x86_64-Offline-Paket implementiert.**

## Ausgangsproblem

I32 pinnt `PySide6==6.11.2` und hasht alle Dateien im fertigen Paket. Vor I33 wurde das Wheelhouse aber erst **nach** dem Download in das Paketmanifest aufgenommen.

Damit war ein Paket nach dem Build prüfbar, aber der Build selbst hatte noch keinen vorab festgelegten Satz erlaubter Wheel-Dateien und Hashes.

## Lock-Vertrag

`wheelhouse-lock-linux-x86_64.json` bindet exakt:

- Plattform `linux-x86_64`;
- SHA-256 von `requirements-gui.txt`;
- exakt vier Wheel-Dateinamen;
- exakte Dateigröße;
- exakten SHA-256 jeder Wheel-Datei.

Erlaubt sind nur:

- `pyside6-6.11.2-cp310-abi3-manylinux_2_34_x86_64.whl`;
- `pyside6_addons-6.11.2-cp310-abi3-manylinux_2_34_x86_64.whl`;
- `pyside6_essentials-6.11.2-cp310-abi3-manylinux_2_34_x86_64.whl`;
- `shiboken6-6.11.2-cp310-abi3-manylinux_2_34_x86_64.whl`.

Zusätzliche, fehlende, umbenannte, anders große oder hashabweichende Wheels führen fail-closed zu `FAIL`.

## Drei Prüfgrenzen

### CI vor Paketbau

Nach `pip download` und **vor** dem ZIP-Build:

```text
download
→ verify_wheelhouse_lock.py
→ erst bei PASS Paket bauen
```

### Paketvalidator

Nach dem Entpacken in den Fremdpfad wird das enthaltene Wheelhouse erneut gegen den mitgelieferten Lock geprüft.

### Nutzerstarter

Bevor `start.sh` aus einem vorhandenen lokalen Wheelhouse irgendein Paket installiert:

```text
wheelhouse vorhanden
→ Lock-Datei Pflicht
→ Hash/Größe/Dateiliste prüfen
→ PASS
→ Nutzerbestätigung
→ pip --no-index
```

Bei Lockfehler wird **nichts installiert**. Es gibt keinen Netzwerk-Fallback.

## Herkunft der initialen Hashbaseline

Die initialen vier Hashwerte stammen aus dem vollständig grünen I32-Paketlauf auf Source-Head:

`bfee18f528e6a06feb9b3b43d1da9575578f2e89`

Das I32-Artefaktmanifest bestätigte dieselben Dateinamen, Größen und SHA-256-Werte.

## Änderungsregel

Ein Dependency-/Wheel-Update benötigt künftig einen bewussten separaten Change:

1. `requirements-gui.txt` ändern;
2. neue Wheels isoliert beziehen;
3. Herkunft/Version prüfen;
4. Lock-Datei explizit aktualisieren;
5. vollständigen Portable-Package-Gate neu ausführen.

Der Lock darf nicht automatisch während eines normalen Paketbuilds umgeschrieben werden.

## Nicht-Ziele

- keine Signatur-/TUF-Infrastruktur;
- kein eigener Paketserver;
- keine automatische Abhängigkeitsaktualisierung;
- keine ARM-Wheels;
- keine Erweiterung der erlaubten Netzpfade;
- keine Änderung an I25/I31 READY-Zuständen.
