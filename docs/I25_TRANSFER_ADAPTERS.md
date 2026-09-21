# I25 – Transfer-Preview Adapter

## Status

**Implementiert, aber noch nicht READY.**

Die Fach- und Adapterimplementierung ist vorhanden. Die Registry-Einträge `files.preview_copy` und `files.preview_move` bleiben gemäß I23 bewusst `OPEN`, bis die neue sichtbare GUI-Erweiterung real geprüft wurde.

## Datenfluss

```text
Root
  ↓
I18 prepare_inventory_view()
  ↓
explizite Mehrfachauswahl
  ↓
Copy- oder Move-Preview
  ↓
I21 prepare_copy_preview() / prepare_move_preview()
  ↓
I12 PreviewPlan + validate_preview()
  ↓
Darstellung in CLI oder GUI
  ↓
🔒 STOP – kein Executor
```

## Adapter

CLI: nummerierte I18-Dateiansicht, Einzel-/Mehrfachauswahl, Copy/Move-Vorschau und gemeinsames Core-Ergebnis.

GUI: OPEN-Funktionen bleiben im normalen Nutzerweg verborgen. Der reale Prüfmodus wird ausschließlich über

```bash
./start.sh --i25-evidence
```

gestartet und zeigt die beiden Aktionen sichtbar als **Prüfmodus**. Mehrfachauswahl ist aktiviert. Zielordner werden nicht mehr über einen freien Dateidialog gewählt, sondern ausschließlich aus einer vom Core erzeugten Liste vorhandener, symlinkfreier Ordner innerhalb der Root. Der Core validiert das Ziel danach trotzdem erneut.

## Sicherheitsgrenzen

Weiter gesperrt:

- produktiver Copy-/Move-Write;
- Overwrite;
- Auto-Rename;
- externe Zielwurzel;
- Cross-Device Move;
- Persistenz;
- Journal-Writer;
- Rechteausweitung.

Der Read-only-Lock bleibt aktiv.

## Automatisierte Gates

- Registry bleibt OPEN;
- Application-Core Copy/Move Preview;
- deterministische Auswahlreihenfolge;
- externes Ziel BLOCKED;
- leere Auswahl OPEN;
- CLI-Parität;
- GUI-Prüfmodus/Mehrfachauswahl-Vertrag;
- Startervertrag `--i25-evidence`;
- I21-Regression;
- vollständige Suite;
- Read-only-Lock;
- Core Diagnostic.

## Evidence vor READY

Die technischen Punkte werden jetzt automatisch über `scripts/i25_auto_evidence.py` geprüft:

- 100 / 150 / 200 %;
- Tab / Shift+Tab und sichtbarer Fokus;
- Mehrfachauswahlvertrag;
- Same-Root-Zielwahlliste;
- Auswahl- und Ziel-Dialoge bei 100 / 150 / 200 % innerhalb des Test-Viewports;
- Tastaturfokus in Datei- und Zielauswahl inklusive Tab/Shift+Tab bzw. Pfeiltasten;
- deterministisches Cancel/Rejected-Verhalten beider Dialoge;
- externe/Symlink-Ziele nicht auswählbar;
- Copy-/Move-Preview;
- unveränderte Quelldateien;
- verständliche Abbruch-/Statuspfade;
- Screenshots und maschinenlesbare Auswertung.

Der Nutzerstart `./start.sh --i25-evidence` führt diese Prüfungen automatisch aus und zeigt nur bei technischem PASS noch genau eine finale Chromium-Frage zur Gesamtverständlichkeit. `./start.sh --i25-offscreen` führt nur den technischen Teil aus.

Erst bei technischem PASS plus finalem Human-PASS dürfen die Registry-Einträge in einem separaten kleinen Freeze-Batch auf `READY` wechseln.

## Prozessbefund

Der erste RC stoppte ausschließlich am vorgezogenen Info-Text-Impact, bevor Produktgates liefen. Deshalb läuft Info-Text nun als finales hartes PR-Gate nach Repository-, Safety-, Test-, Diagnose- und Preflight-Prüfungen. Die Dokumentationspflicht wird nicht abgeschwächt; die technische RC-Diagnose wird nur entkoppelt.


## Automatischer GitHub-GUI-Gate

Für I25-relevante Änderungen existiert zusätzlich ein separater GitHub-Actions-Gate. Er wird nur bei Änderungen an Produkt-GUI/Core, I25-Evidence, Tests, Starter oder GUI-Abhängigkeit ausgelöst.

Der Job:

1. erstellt eine isolierte CI-Venv;
2. installiert ausschließlich die gepinnte GUI-Abhängigkeit aus `requirements-gui.txt`;
3. startet `scripts/i25_auto_evidence.py --offscreen --auto-only`;
4. verlangt technischen PASS ohne menschliche Abnahme.

Dadurch müssen 100/150/200 %, Fokus, Dialogverträge und synthetischer Transfer-Workflow nicht mehr vom Nutzer wiederholt getestet werden.
