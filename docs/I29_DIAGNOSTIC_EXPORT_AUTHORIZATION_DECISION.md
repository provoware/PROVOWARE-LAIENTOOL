# I29 – Diagnose-Export Autorisierungs-/Adapter-Decision

## Status

**Entscheidung eingefroren. Keine sichtbare Exportfunktion. Kein Registry-READY. Kein neuer Schreibpfad.**

I29 legt ausschließlich fest, wie ein späterer lokaler Diagnoseexport autorisiert und in GUI/CLI angeboten werden darf. I29 ruft den I28-Writer nicht auf.

## Ausgangslage

Bereits vorhanden:

- I20: redigierter Diagnosebericht;
- I22: lokaler Export grundsätzlich erlaubt, aber nur explizit initiiert;
- I24: create-only/no-overwrite Writer-Design;
- I26: immutable ExportPlan + serialisierter Payload, standardmäßig `write_enabled=False`;
- I27: exakter Spezialguard für `diagnostic_export.py`;
- I28: isolierter Writer-Testlab mit Race/Crash/ENOSPC/PermissionError/No-clobber-PASS.

Weiter offen ist ausschließlich der Produktvertrag zwischen Nutzerentscheidung und Writer.

## Grundentscheidung

Ein späterer Nutzerexport darf nur über **einen gemeinsamen Application-Use-Case** erfolgen.

```text
GUI/CLI Adapter
    ↓
Format + vorhandenen Zielordner wählen
    ↓
I26 ExportPreparation
    ↓
Exportvorschau anzeigen
    ↓
erste ausdrückliche Bestätigung
    ↓
finale Zusammenfassung unverändert anzeigen
    ↓
zweite ausdrückliche Bestätigung
    ↓
Application-Core erzeugt autorisierten Plan
    ↓
I28 Writer
    ↓
strukturiertes Ergebnis
```

Adapter dürfen niemals `write_enabled=True` selbst setzen.

## Warum zwei Bestätigungen?

Diagnoseexport ist der erste bewusst erreichbare Schreibpfad des Produkts. Deshalb reicht ein einzelner Klick direkt nach Zielwahl nicht.

### Bestätigung 1 – Absicht

Der Nutzer bestätigt:

> „Ich möchte diese redigierte Diagnose als neue Datei speichern.“

Vorher sichtbar:

- Format;
- Zielordner;
- finaler Dateiname;
- Dateigröße;
- Hinweis: bestehende Dateien werden nicht überschrieben;
- Hinweis: ausschließlich lokaler Export, kein Upload.

### Bestätigung 2 – Commit

Unmittelbar vor der Autorisierung wird dieselbe fachliche Zusammenfassung erneut angezeigt.

Die zweite Bestätigung muss eindeutig lauten:

> **„Diagnosedatei jetzt neu erstellen“**

Nicht zulässig:

- „OK“ als alleinige Schreibbestätigung;
- vorausgewähltes Ja;
- Enter bestätigt automatisch einen gefährlichen Standard;
- Timeout-Bestätigung;
- Hintergrundfortsetzung;
- Checkbox „nicht wieder fragen“.

Zwischen beiden Bestätigungen darf keine fachliche Eingabe heimlich geändert werden.

## Änderungsregel zwischen Bestätigungen

Ändert der Nutzer nach Bestätigung 1 einen der folgenden Werte:

- Format;
- Zielordner;
- Dateiname;
- Payload/Diagnoseinhalt;

wird die erste Bestätigung **ungültig**.

Der Workflow springt zurück zur Vorschau. Beide Bestätigungen müssen erneut erfolgen.

Damit ist die Autorisierung an genau den sichtbaren Exportzustand gebunden.

## Autorisierungsobjekt

Eine spätere Implementierung soll keinen bestehenden I26-`ExportPlan` mutieren.

Empfohlener gemeinsamer Application-Vertrag:

```text
ExportAuthorization
- plan_fingerprint
- confirmed=True
- confirmation_stage=2
```

Der Application-Core verifiziert, dass die Autorisierung exakt zum unveränderten ExportPlan/Payload passt und erzeugt erst dann intern einen Writer-Aufruf mit autorisiertem Plan.

Kein Adapter erhält direkten Zugriff auf `write_diagnostic_export()`.

## Fingerprint-Bindung

Die Autorisierung muss mindestens binden:

- `final_path`;
- `export_format`;
- `payload_size_bytes`;
- `payload_sha256`;
- `overwrite_allowed=False`.

Ändert sich ein Bestandteil, ist die Autorisierung ungültig.

## Registry-Vertrag

Empfohlene spätere Use-Case-ID:

```text
diagnostics.export_local
```

Anzeigename:

**„Diagnose lokal speichern“**

Der Eintrag darf während der Implementierung höchstens `OPEN` sein.

Vor `READY` zwingend gleichzeitig:

1. gemeinsamer Application-Use-Case vorhanden;
2. GUI-Adapter vorhanden;
3. CLI-Zahlenmenü vorhanden;
4. beide nutzen denselben I26/I28-Pfad;
5. Doppelbestätigung in beiden Adaptern;
6. Cancel-/Zurück-Parität;
7. strukturierte Fehlerklassen identisch;
8. Accessibility-Auto-Evidence grün;
9. reale Human-Abnahme des sichtbaren Schreibworkflows;
10. kein anderer Writer/Executor dadurch freigegeben.

`diagnostics.snapshot` bleibt davon unabhängig read-only und CLI-only.

## Sicherheitsklasse

Der bestehende Registry-Vertrag besitzt aktuell nur:

- `read-only`;
- `preview-required`;
- `recovery-required`.

I29 entscheidet:

**Der Diagnoseexport darf nicht irreführend als eine dieser vorhandenen Klassen eingebaut werden.**

Vor Adapterimplementierung muss die Registry gezielt um eine neue Klasse erweitert werden, z. B.:

```text
explicit-write-confirmation
```

Diese Klasse bedeutet:

- echter, eng begrenzter Write;
- Preview/Exportzusammenfassung Pflicht;
- zweistufige explizite Bestätigung Pflicht;
- kein Recovery-Versprechen erforderlich, weil ausschließlich eine neue Datei erzeugt und nichts Bestehendes verändert wird;
- no-overwrite Pflicht.

Die Erweiterung erfolgt erst im Folgeblock mit eigenen Registry-Tests.

## GUI-Vertrag

Späterer Standardweg:

1. **Diagnose lokal speichern** wählen.
2. Format wählen: Klartext oder JSON.
3. vorhandenen Zielordner ausdrücklich wählen.
4. Vorschau/Exportzusammenfassung.
5. **Weiter zur Bestätigung**.
6. finale Zusammenfassung.
7. **Diagnosedatei jetzt neu erstellen**.
8. Abschlusskarte.

Pflicht:

- Standardfokus der finalen Bestätigung liegt **nicht** auf dem Schreibbutton;
- sichtbarer **Abbrechen**-Button;
- Escape bricht vor Commit ab;
- Schließen des Dialogs entspricht Abbruch;
- Schreibbutton erst aktiv, wenn die finale Zusammenfassung vollständig vorliegt;
- bei 200 % bleibt Bestätigung und Abbruch erreichbar.

Keine freie Bearbeitung des Payloads.

## CLI-Vertrag

Nur Zahlen-/explizite Auswahl, keine erforderlichen Shellkenntnisse.

Beispiel:

```text
Diagnose lokal speichern

1  Klartext
2  JSON
0  Zurück
```

Danach Zielordnerwahl und Zusammenfassung.

Bestätigung 1:

```text
1  Weiter zur finalen Bestätigung
0  Abbrechen
```

Bestätigung 2:

```text
Es wird genau eine neue Diagnosedatei erstellt.
Bestehende Dateien werden nicht überschrieben.

1  Diagnosedatei jetzt neu erstellen
0  Abbrechen
```

Keine Eingabe wie `y`, `yes`, Shellpfadglobs oder Freitextsatz als Sicherheitsbestätigung.

## Cancel-/Abbruchvertrag

Abbruch ist in **jeder Phase vor Writer-Aufruf** seiteneffektfrei.

Abbruch nach:

- Formatwahl;
- Zielwahl;
- Vorschau;
- Bestätigung 1;
- finaler Zusammenfassung;

führt zu:

```text
OPEN / CANCELLED
→ kein autorisierter Plan
→ kein Writer-Aufruf
→ keine Dateiänderung
```

Nach Writer-Start bedeutet ein UI-Abbruch **nicht**, dass ein laufender Low-Level-Commit hart unterbrochen wird. Der Writer beendet seinen kleinen atomaren Versuch und liefert danach Ergebnisstatus. Kein Adapter darf den Prozess mitten im Commit künstlich killen.

## Failure-Darstellung

Die I28-Fehlerklassen werden im gemeinsamen Application-Core in Laientexte übersetzt. Adapter dürfen sie nur darstellen.

Pflichtschema:

**Was ist passiert? → Was bedeutet das? → Was kann ich jetzt tun?**

Beispiele:

### Ziel existiert

- Was ist passiert? Der Dateiname ist bereits vorhanden.
- Was bedeutet das? PROVOWARE überschreibt die bestehende Datei nicht.
- Was kann ich tun? Wähle einen anderen Dateinamen oder Zielordner.

### Kein Speicherplatz

- Was ist passiert? Der Datenträger hat nicht genug freien Speicher.
- Was bedeutet das? Der Export wurde nicht erfolgreich abgeschlossen.
- Was kann ich tun? Schaffe Speicherplatz oder wähle einen anderen Datenträger.

### Partial-Datei blieb zurück

Muss ausdrücklich nennen:

- finale Datei erfolgreich vorhanden oder nicht;
- unvollständige Partial-Datei vorhanden;
- exakten sicheren nächsten Schritt, ohne automatisches Löschen fremder Dateien zu versprechen.

Rohe Exceptions, errno oder interne Klassennamen dürfen nicht die alleinige Nutzermeldung sein.

## Erfolgsdarstellung

Erfolg zeigt mindestens:

- **Diagnosedatei erstellt**;
- Zielpfad;
- Format;
- Größe;
- Hinweis: bestehende Dateien wurden nicht überschrieben;
- Hinweis: keine Daten wurden hochgeladen.

Keine automatische Öffnung, kein automatischer Upload, kein automatisches Anhängen an Supportdienste.

## Wiederholung

Nach PASS darf ein zweiter Export nicht automatisch erfolgen.

„Noch einmal exportieren“ startet einen **neuen** Workflow:

- neuer I26-Preflight;
- neue Vorschau;
- neue Doppelbestätigung;
- neuer Dateiname muss konfliktfrei sein.

Keine Wiederverwendung einer alten Autorisierung.

## GUI-/CLI-Parität

Gleiche fachliche Eingabe muss in beiden Adaptern zu demselben führen:

- ExportPlan;
- Fingerprint;
- Autorisierungsstatus;
- Writer-Aufruf oder Nicht-Aufruf;
- Fehlerklasse;
- Abschlussstatus.

Darstellung darf verschieden sein, Fachentscheidung nicht.

## Accessibility-/Human-Gate

Vor `READY` des sichtbaren Exports:

Automatisch:

- 100 / 150 / 200 %;
- Tab / Shift+Tab;
- Fokusreihenfolge;
- Abbruchpfade;
- beide Bestätigungsstufen;
- Schreibbutton nicht Default-Fokus;
- Failure-Darstellung;
- keine Datei bei Cancel;
- exakt eine Datei bei PASS.

Real/Human:

Genau eine finale Wahrnehmungsabnahme des kompletten sichtbaren Schreibworkflows:

> Ist jederzeit klar, **ob noch nichts geschrieben wird**, wann die Datei tatsächlich erstellt wird, wo sie landet und wie man vorher sicher abbricht?

## Nicht-Ziele von I29

- keine Änderung an `capability_registry.py`;
- kein neuer Registry-Eintrag;
- kein GUI-Button;
- kein CLI-Menüpunkt;
- kein Application-Authorization-Code;
- kein Writer-Aufruf aus einem Adapter;
- kein Startmodus;
- kein neues Dateiformat;
- kein Upload;
- kein Netzwerk;
- keine Recovery-/Undo-Erweiterung;
- keine Freigabe anderer Schreibpfade.

## Folgeblock

Erst I30 darf den **Application-Autorisierungsvertrag + Registry-Erweiterung** implementieren.

Auch I30 soll noch keine sichtbare GUI/CLI-Funktion benötigen. Ziel ist zuerst ein vollständig automatisierbarer nichtvisueller Vertrag:

```text
ExportPreparation
→ Fingerprint
→ Stage-1 Confirmation
→ Stage-2 Confirmation
→ AuthorizedExportRequest
→ I28 Writer
```

Danach erst Adapterimplementation in einem separaten Block.
