# AGENTS.md — PROVOWARE-LAIENTOOL

Gilt repository-weit für Menschen, Codex und Subagenten.

## 1. Prioritäten

1. Datensicherheit und Reversibilität
2. fachliche Korrektheit
3. Scope-Disziplin
4. Accessibility und Laienverständlichkeit
5. Wartbarkeit und Testbarkeit
6. Performance
7. Komfort

Geschwindigkeit rechtfertigt niemals stilles Schreiben, Rechteausweitung, Netzabhängigkeit oder abgeschwächte Tests.

## 2. Quellen der Wahrheit

Reihenfolge bei Konflikten:

1. aktuelle explizite Aufgabe / freigegebener CR;
2. diese Datei;
3. akzeptierte ADRs;
4. `PROVOWARE_TODO_INPUT_POOL0.md`;
5. `todo.txt`;
6. README als Übersicht.

Widersprüche nicht durch Annahmen überdecken. Kleinste sichere Interpretation wählen und Konflikt im Abschluss nennen.

## 3. Verbindlicher Arbeitszyklus

`READ → DECIDE → ONE WRITE BATCH → LOCAL TEST → LOCAL EVIDENCE → ONE REMOTE HEAD → TARGETED CI → DIFF → MERGE → POST-MERGE QUALITY`

Vor dem Schreiben festhalten:

- Ziel in einem Satz;
- zugehörige `REQ-*` / `CR-*` / ADR;
- betroffene Dateien;
- Nicht-Ziele;
- Risiken;
- objektive Erfolgskriterien;
- Rückweg bei Fehler.

Regeln:

- keine Nebenrefactors;
- keine globale Neuformatierung;
- kein "vorsorgliches" Dependency-Wachstum;
- kein zweiter Write-Batch, solange der erste nicht geprüft ist;
- fehlende Prüfung = `OPEN`, niemals implizit `PASS`;
- Fehler nicht durch Abschalten oder Aufweichen von Tests lösen.

## 4. Sicherheitsgrenzen

- Keine stille Installation oder Downloads.
- Keine versteckte Rechteausweitung; kein `chmod 777`.
- Keine Dateioperation außerhalb explizit ausgewählter und verifizierter Grenzen.
- Pfade, Unicode, Leerzeichen, Symlinks und Traversal als untrusted input behandeln.
- Schreibpfade benötigen Preview + Wirkungserklärung + Rückweg.
- Löschung bevorzugt reversibel; irreversible Schritte separat und ausdrücklich freigeben.
- Diagnose darf keine Secrets enthalten; Pfade/Dateinamen gelten als potenziell sensibel.
- Plugins niemals automatisch installieren oder aktivieren.

## 5. Architekturgrenzen

- GUI: PySide6/Qt; kein Tkinter im Produktionscode.
- GUI und CLI verwenden denselben Application-/Domain-Kern.
- UI entscheidet nicht selbst über Datei- oder Sicherheitsregeln.
- Thumbnail-/Preview-Laden blockiert den UI-Thread nicht.
- CLI bleibt laienverständlich und ist kein zweiter Fachkern.
- Neue größere Architekturentscheidung als ADR dokumentieren.
- Produktverzeichnisse nicht leer "auf Vorrat" anlegen.

## 6. Dateibudget und Codesparsamkeit

Standard: kleinster kohärenter Diff.

Vor Erweiterung prüfen:

1. Kann vorhandener Code wiederverwendet werden?
2. Ist eine neue Datei wirklich eine neue Verantwortung?
3. Kann dieselbe Wirkung mit weniger Schnittstellen erreicht werden?
4. Erhöht die Änderung Test- oder Wartungsfläche unnötig?

Gemeinsame Modelle und zentrale Schnittstellen bleiben beim Hauptagenten.

## 7. Triggerbasierte Subagenten

Subagent standardmäßig **AUS**. Aktivierung nur, wenn alle Bedingungen erfüllt sind:

- konkrete unabhängige Frage;
- klarer exklusiver Scope;
- Ergebnis separat nutzbar;
- Kommunikationskosten kleiner als erwarteter Nutzen;
- keine konkurrierende Schreibhoheit an derselben Datei.

### Explorer 🔎
Trigger: unbekannter Codepfad, mehrere mögliche Besitzer oder Architekturfrage vor einem Patch.
Modus: read-only.
Stop: relevante Dateien, Datenfluss und maximal drei Risiken benannt.

### Implementierer 🛠️
Trigger: fachlich abtrennbares Modul mit exklusivem Dateibesitz und stabiler Schnittstelle.
Modus: write nur im zugewiesenen Scope.
Stop: Patch + direkte Tests + geänderte Dateien + Restrisiken.

### Testprüfer 🧪
Trigger: nicht-trivialer Patch, Regression oder Release-Gate.
Modus: bevorzugt read-only; repariert eigene Befunde nicht selbst.
Stop: PASS/FAIL/OPEN mit reproduzierbarer Prüfanweisung.

### UX-/Accessibility-Prüfer ♿
Trigger: sichtbare GUI-, Fokus-, Navigation-, Theme-, Skalierungs- oder Textänderung.
Modus: read-only Bewertung.
Stop: Befunde für 100/150/200 %, Tastatur, Fokus, Kontrast, Reduced Motion.

### Sicherheitsprüfer 🛡️
Trigger: Pfade, Schreiben/Löschen/Verschieben, Recovery, Diagnose, Paketierung, Plugins, Netzwerk oder Berechtigungen.
Modus: read-only Gegenprüfung.
Stop: Angriff-/Fehlerpfade, vorhandene Gates, offene Blocker.

### Minimaler Auftrag
Jeder Subagent erhält nur:
`Ziel | Scope | erlaubte Dateien | Nicht-Ziele | Prüfung | Rückgabeformat | Stop-Bedingung`

Übergabe:
`STATUS | max. 3 Befunde | geänderte Dateien | exakte Prüfungen | verbleibende Risiken`

## 8. Teststrategie

Pro Änderung nur relevante Tests zuerst; vor Merge vollständiger passender Gate.

Mindestens prüfen, sobald fachlich relevant:

- Normalfall und Fehlereingabe;
- Unicode/Leerzeichen;
- Rechtefehler;
- Abbruch und Wiederholung;
- Symlink/Traversal;
- Parallelstart;
- Offline-Verhalten;
- beschädigte Konfiguration;
- knapper Speicher;
- Recovery.

Bugs erhalten Regressionstest oder reproduzierbare Prüfanweisung.

## 9. Evidence

Evidence enthält mindestens:

- ID, Datum, Commit/Fingerprint;
- REQ/CR;
- Umgebung;
- Befehl/Ablauf;
- Erwartung;
- Beobachtung;
- Exit-Code, falls vorhanden;
- `PASS | FAIL | OPEN | SKIPPED`;
- relevante Artefakte/Hashes.

Konvention siehe `docs/evidence/README.md`.

## 10. GitHub

- PR klein und thematisch eindeutig.
- Betroffene REQ/CR im PR nennen.
- CI vollständig grün oder Abweichung explizit erklären.
- Actions mit minimalen `permissions:`.
- Externe Actions auf unveränderlichen Commit-SHA pinnen.
- Kein Secret in Repo, PR, Issue, Log oder Evidence.
- Kein Force-Push auf `main`.
- Squash-Merge bevorzugen, wenn ein PR eine logische Änderung bildet.

## 11. Abschlussformat

Jeder Arbeitsblock endet mit:

- Ziel;
- geändert;
- nicht geändert;
- Tests/Evidence;
- offene Punkte;
- neue Risiken;
- Status 🟢 / 🟨 / 🔴;
- genau einem empfohlenen nächsten Schritt.
