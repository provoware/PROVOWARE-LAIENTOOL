# I38 – Vorab festgeschriebene Wheelhouse-Baseline

## Ziel

Die in der I37-Branch-Forensik gefundene Sicherheitsinvariante aus dem alten I33-Branch wird auf aktuellem `main` gerettet: Das Offline-Wheelhouse muss **vor dem Paketbau** gegen eine eingecheckte exakte Baseline geprüft werden.

## Vertrag

`wheelhouse-lock-linux-x86_64.json` bindet exakt:

- Plattform `linux-x86_64`;
- SHA-256 von `requirements-gui.txt`;
- exakt vier Wheel-Dateinamen;
- exakte Dateigröße;
- exakten SHA-256 jedes Wheels.

Die vier Hashwerte entsprechen den veröffentlichten PySide6-6.11.2-Dateien für Linux x86-64 und stammen aus dem bereits belegten I33-Altstand.

## CI-Reihenfolge

```text
pip download
→ verify_wheelhouse_baseline.py
→ nur bei PASS build_portable_package.py
→ bestehende Paket-/Runtime-Prüfungen
```

Damit kann ein unerwartet ausgetauschtes oder neu veröffentlichtes Wheel nicht erst durch das frisch erzeugte Paketmanifest legitimiert werden.

## Fail-closed

Der Baseline-Prüfer beendet mit Fehler bei:

- fehlender oder unlesbarer Baseline;
- verändertem `requirements-gui.txt`;
- fehlenden oder zusätzlichen Wheels;
- abweichendem Dateinamen;
- abweichender Dateigröße;
- abweichendem SHA-256;
- ungültigem Baseline-Schema.

## Nicht-Ziele

- keine neue Paketarchitektur;
- keine Änderung am Runtime-Installer;
- kein neuer Netzwerkpfad;
- keine Signatur-/TUF-/Sigstore-Infrastruktur;
- keine automatische Aktualisierung der Hashbaseline;
- keine Änderung an I25/I31 Human-Gates.
