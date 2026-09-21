# I10 – Gemeinsame Capability-/Use-Case-Registry

## Ziel

GUI und Konsole beziehen ihre fachlich verfügbaren Funktionen aus derselben unveränderlichen Registry. Dadurch entsteht kein zweiter Funktionskatalog und keine Oberfläche kann still eine eigene Sicherheits- oder Verfügbarkeitslogik erfinden.

## Datenmodell

Jeder Eintrag enthält:

- stabile Funktions-ID;
- laienfreundlichen Anzeigenamen;
- GUI-Verfügbarkeit;
- CLI-Verfügbarkeit;
- Kennzeichen für erlaubte reine Diagnose-CLI;
- Sicherheitsklasse;
- Preview-Pflicht;
- Recovery-Pflicht;
- erforderliche Capability;
- Status `READY | OPEN | BLOCKED`.

## Aktueller Registry-Inhalt

Aktuell wird bewusst nur der bereits tatsächlich vorhandene Use Case registriert:

- `system.preflight` → **System prüfen**
  - CLI: READY
  - GUI: noch nicht vorhanden
  - rein diagnostischer CLI-Weg: erlaubt
  - Sicherheitsklasse: read-only

Es werden keine zukünftigen Produktfunktionen vorgetäuscht. Neue Einträge kommen erst hinzu, wenn ein fachlicher Use Case wirklich freigegeben wurde.

## Paritätsregeln

Der Validator blockiert unter anderem:

- doppelte Funktions-IDs;
- unbekannte Statuswerte;
- unbekannte Sicherheitsklassen;
- GUI-Fachfunktionen ohne CLI-Pfad;
- widersprüchliche Diagnose-CLI-Markierungen;
- Recovery-Pflicht ohne Preview-Pflicht;
- READY ohne verfügbaren Adapter.

## Architektur

```text
GUI Adapter ─┐
             ├─ Capability Registry ─ Application / Domain Core
CLI Adapter ─┘
```

Die Registry beschreibt Verfügbarkeit und Vertrag. Sie führt keine Fachlogik und keine Dateioperation aus.

## Nicht-Ziele

- keine GUI;
- kein Konsolenmenü;
- keine Dateisuche;
- keine Dateioperation;
- keine Plugins;
- kein dynamisches Nachladen von Funktionen.

## Gate

```bash
PYTHONPATH=src python3 -m unittest tests.test_capability_registry -v
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
