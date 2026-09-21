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

gestartet und zeigt die beiden Aktionen sichtbar als **Prüfmodus**. Mehrfachauswahl ist aktiviert; Ziel- und Sicherheitsentscheidung verbleiben im gemeinsamen Core.

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

## Reale Evidence vor READY

Noch erforderlich:

- 100 / 150 / 200 %;
- Tab / Shift+Tab;
- sichtbarer Fokus;
- Mehrfachauswahl;
- Zielordnerwahl;
- Preview vollständig erreichbar;
- verständlicher Abbruch;
- Laienverständlichkeit.

Erst bei realem PASS dürfen die Registry-Einträge in einem separaten kleinen Freeze-Batch auf `READY` wechseln.

## Prozessbefund

Der erste RC stoppte ausschließlich am vorgezogenen Info-Text-Impact, bevor Produktgates liefen. Deshalb läuft Info-Text nun als finales hartes PR-Gate nach Repository-, Safety-, Test-, Diagnose- und Preflight-Prüfungen. Die Dokumentationspflicht wird nicht abgeschwächt; die technische RC-Diagnose wird nur entkoppelt.
