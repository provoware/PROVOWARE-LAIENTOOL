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

`ORGANIZE → PLAN → IMPLEMENT → VERIFY → DOC → EVIDENCE → CI → DIFF → MERGE → POST-MERGE VERIFY → NEXT-PLAN`

Vor jeder Iteration erzeugt der Organisator ein kollisionsfreies Update-Paket. Planung, Implementierung, Prüfung und Dokumentation bleiben personell bzw. rollenlogisch getrennt.

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

### Anti-Endlosschleifen- und Retry-Regeln

Für Tests, Diagnose, Agentenläufe und Reparaturschleifen gilt zusätzlich:

- jeder automatisierte Lauf erhält eine endliche Laufzeit oder ein übergeordnetes Timeout;
- identischer fehlgeschlagener Befehl darf ohne Code-, Fixture-, Umgebungs- oder Konfigurationsänderung höchstens **einmal** zur Reproduktionsbestätigung wiederholt werden;
- derselbe ursächliche Fehler erhält höchstens **zwei** gezielte `WRITE → TARGETED TEST`-Reparaturzyklen; danach **STOP → neu planen**, statt weiter zu patchen;
- Full Suite erst nach grünem targeted Test; nicht nach jedem Zwischenpatch erneut die gesamte Suite starten;
- ein Timeout ist ein eigener Befund und wird nicht automatisch als Produktfehler gewertet;
- automatische Retries benötigen explizites `max_attempts`, begrenzten Backoff und eine sichtbare Abbruchbedingung;
- Endlosschleifen bzw. unbegrenzte Poll-/Wait-Schleifen sind in Tests und Entwicklungswerkzeugen verboten;
- Tests dürfen nicht durch Abschwächung, Skip oder höhere Retry-Zahl "grün gemacht" werden;
- jeder Wiederholungslauf muss eine konkrete Hypothese prüfen oder neue Evidence erzeugen. Reine Wiederholung ohne Informationsgewinn ist verboten;
- bei Hänger/Timeout zuerst Prozess, Child-Prozesse und Ressourcenlage prüfen; nicht sofort denselben Test erneut starten.

**Stop-Signale:** gleicher Fehler zweimal unverändert, Timeout zweimal am selben Punkt, wachsender Scope oder mehr als zwei Reparaturzyklen ohne Ursachenbeleg. Dann wird der Block als `OPEN`/`FAIL` beendet und neu geplant.


### Effizienzstandard: Release Candidate + Finalisierung

Ziel ist **maximaler Informationsgewinn pro Lauf bei minimaler Repository-Bewegung**. Sicherheit und Nachweisstärke bleiben unverändert.

Verbindlicher Standard:

`READ → DECIDE → ONE COHERENT WRITE BATCH → TARGETED → FULL GATE → RC → FINALIZE DOC/EVIDENCE → ONE REMOTE HEAD → CI → DIFF → MERGE → POST-MERGE VERIFY`

Dabei gilt:

- **kein Commit pro Einzelgate** und kein eigener Commit nur für „Test grün“, „Status aktualisiert“ oder „Evidence ergänzt“, wenn diese Informationen in einem gemeinsamen Finalisierungsbatch gebunden werden können;
- Produkt-/Teständerungen werden lokal bzw. im Arbeitsstand gesammelt, bis ein kohärenter **Release Candidate (RC)** vorliegt;
- vor dem ersten Review-Push möglichst zuerst targeted Tests, danach genau ein vollständiger lokaler Gate-Lauf auf demselben RC;
- Evidence darf den **geprüften RC-SHA/Fingerprint** referenzieren. Ein anschließender reiner Dokumentations-/Evidence-Commit macht den RC-Nachweis nicht ungültig und erzwingt keine Fingerprint-Endlosschleife;
- nach grünem RC folgt höchstens **ein Finalisierungsbatch** für README/TODO/CURRENT_ITERATION/Evidence/PR-Text, soweit betroffen;
- ein reiner Finalisierungsbatch löst lokal nur die dafür relevanten Repository-/Dokumentationsgates aus; die zentrale PR-CI bleibt der vollständige unabhängige Endnachweis;
- `docs/CURRENT_ITERATION.md` wird an **Iterationsgrenzen** aktualisiert, nicht nach jedem Untergate;
- ein PR soll im Normalfall aus **einem fachlichen Commit plus optional einem Finalisierungscommit** bestehen. Zusätzliche Reparaturcommits sind nur zulässig, wenn CI oder Review neue Information erzeugt;
- kein inkrementelles Remote-Pushen nur zur Fehlersuche, wenn derselbe Fehler lokal reproduzierbar ist;
- vor Merge wird der finale Diff einmal als Ganzes gegen Scope, Nicht-Ziele, Statusdrift und unnötige Dateien geprüft;
- nach erfolgreichem Merge werden überholte Arbeitsbranches entfernt, sobald keine bewusst zu bewahrenden einzigartigen Änderungen mehr darauf liegen.

### Testökonomie

Tests werden nach Änderungswirkung gewählt, nicht nach Gewohnheit:

1. **L0 Repository/Contract** bei Prozess-, Doku- und Strukturänderungen;
2. **L1 Targeted** für direkt betroffene Fachlogik;
3. **L2 Cross-Core** nur bei realer Kopplung/Sicherheitswirkung;
4. **L3 Full Gate** einmal auf dem RC vor Merge;
5. **L4 Real Evidence** nur für Eigenschaften, die CI nicht objektiv belegen kann.

Ein bereits grüner unveränderter RC wird nicht erneut vollständig getestet, nur weil anschließend reine Dokumentation ergänzt wurde. Die PR-CI prüft den finalen Branch unabhängig vollständig.

### Architekturökonomie

- neue Abstraktion nur bei mindestens zwei realen Nutzern oder klarer Sicherheits-/Testgrenze;
- keine Datei-/Klassenzerlegung nur wegen Zeilenzahl;
- bei Modulen an der Beobachtungsschwelle zuerst **Kohäsion messen**: neue Verantwortung abtrennen, bestehende zusammengehörige Verantwortung zusammenlassen;
- Adapter dürfen keinen wachsenden Application-Core durch UI-spezifische Verzweigungen erzwingen;
- neue Komfortfunktion bevorzugt über vorhandene Use-Cases/Modelle anbinden statt neue Parallelpfade zu schaffen.


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

### Verbindlicher Startvertrag

- `start.sh` ist dauerhaft der einzige offizielle Nutzer-Einstiegspunkt.
- Neue nutzerseitige Startmodi müssen in `start.sh` integriert werden.
- Runtime-, Venv-, GUI- oder Evidence-Änderungen aktualisieren `start.sh` im selben Change-Batch, falls die Startlogik betroffen ist.
- Direkte Aufrufe von `python3 start.py` oder `python3 scripts/...` sind interne Entwickler-/Diagnosewege und keine Nutzeranleitung.
- Repository-Gate und Tests müssen die zentralen `start.sh`-Modi gegen versehentliches Entfernen absichern.
- `start.sh` bleibt Venv-first, fail-fast und ohne stille Rechteausweitung/Systeminstallation.

- GUI: PySide6/Qt; kein Tkinter im Produktionscode.
- GUI und CLI verwenden denselben Application-/Domain-Kern.
- Jede GUI-Fachfunktion benötigt einen gleichwertigen laienfreundlichen Konsolenweg gemäß `docs/GUI_CLI_PARITY.md`; rein visuelle Funktionen müssen als solche begründet sein.
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

### Rollenprinzip

Subagenten werden nicht nur nach Fachgebiet, sondern auch nach **Berechtigungsart** getrennt:

- **ORGANIZE:** organisiert und priorisiert; kein Produktcode, keine Fachimplementierung.
- **PLAN:** plant und zerlegt; read-only gegenüber Produktdateien.
- **VERIFY:** prüft unabhängig; read-only und repariert eigene Befunde nicht.
- **DOC:** dokumentiert ausschließlich freigegebene Ergebnisse; darf nur Dokumentations-/Evidence-Dateien ändern.
- **IMPLEMENT:** implementiert ausschließlich den zugewiesenen Scope mit exklusivem Dateibesitz.

Ein Agent darf in derselben Iteration nicht gleichzeitig **IMPLEMENT** und **VERIFY** für denselben fachlichen Block sein.

### Kollisionsschutz und Dateibesitz

Vor jedem Write-Batch wird eine Datei-Besitzmatrix festgelegt. Für jede veränderte Datei gilt:

- genau ein schreibender Besitzer je Iteration;
- beliebig viele read-only Prüfer;
- Prüfer berichten nur und verändern den geprüften Block nicht;
- Planer planen, aber implementieren nicht;
- Dokumentar schreibt erst nach bestätigter Prüfung;
- bei kollidierendem Dateibedarf werden Arbeiten serialisiert statt parallelisiert;
- gemeinsame Kernverträge werden vor GUI-/CLI-Adaptern festgelegt.

Ein zweiter schreibender Agent darf dieselbe Datei erst übernehmen, nachdem der vorherige Write-Batch abgeschlossen, geprüft und ausdrücklich übergeben wurde.


Subagent standardmäßig **AUS**. Aktivierung nur, wenn alle Bedingungen erfüllt sind:

- konkrete unabhängige Frage;
- klarer exklusiver Scope;
- Ergebnis separat nutzbar;
- Kommunikationskosten kleiner als erwarteter Nutzen;
- keine konkurrierende Schreibhoheit an derselben Datei.

### Update-Organisator 🧭

**Berechtigung:** ORGANIZE, read-only gegenüber Produktcode.

Trigger: vor jeder neuen Update-Iteration und nach jedem abgeschlossenen Lauf.

Aufgaben:

1. letzten Merge-/CI-/Evidence-Stand lesen;
2. festen nächsten Planpunkt aus Roadmap/TODO bestimmen;
3. neue Befunde, Reparaturen, Risiken oder sinnvolle Folgeaufgaben aus dem letzten Lauf extrahieren;
4. daraus genau zwei Update-Anteile bilden:
   - **A – PLAN:** nächster verbindlicher Punkt aus dem bestehenden Plan;
   - **B – DELTA:** genau ein neu entstandener, sinnvoller Folgebedarf aus dem letzten Lauf;
5. Konflikte, Reihenfolge und Abhängigkeiten festlegen;
6. unnötige Parallelität verhindern;
7. Scope, Nicht-Ziele, Gates und Stop-Bedingungen für beide Anteile ausgeben;
8. Datei-Besitzmatrix für alle geplanten Writes erstellen;
9. nach Abschluss zusätzlich die nächsten drei wahrscheinlichen Schritte mit Ziel, Abhängigkeit und Gate vorplanen.

Der Organisator darf **keine neue Fachanforderung erfinden**. Wenn aus dem letzten Lauf kein sinnvoller DELTA-Anteil entsteht, lautet B ausdrücklich **NONE**.

Prioritätsregel für B:
**Blocker/Regression > Sicherheitsbefund > Test-/Evidence-Lücke > Wartbarkeitsfolge > Komfort/Optimierung.**

Wenn B den Plananteil A blockiert, wird **B zuerst** ausgeführt. Wenn B unabhängig ist, bleibt **A zuerst**. Wenn B Scope oder Freeze-Grenzen verletzt, wird B nur dokumentiert und auf eine spätere Iteration verschoben.

Stop: Zwei-Spuren-Updatepaket mit Reihenfolge, Begründung, Datei-Besitzmatrix, erlaubten Dateien, Gates, eindeutigem Abschlusskriterium und Drei-Schritte-Vorausplanung.

### Planer 📐

**Berechtigung:** PLAN, read-only gegenüber Produktcode.

Trigger: neuer Block, unklare Abhängigkeit, Architektur-/Sicherheitsentscheidung oder größere Scope-Frage.

Aufgabe: kleinsten umsetzbaren Block bestimmen, Nicht-Ziele und Exit-Gates festlegen, aber nichts implementieren.

Stop: umsetzbarer Plan mit Dateien, Schnittstellen, Tests, Risiken und Rückweg.

### Dokumentar 📝

**Berechtigung:** DOC.

Trigger: bestätigte Entscheidung, grüner Teststand, Evidence-/ADR-/README-/TODO-Aktualisierung.

Darf ändern:
- `docs/**`
- `README.md`
- `todo.txt`
- freigegebene Metadaten-/Evidence-Dateien

Darf nicht ändern:
- Produktlogik unter `src/**`
- Tests zur inhaltlichen Ergebnisbeeinflussung
- Workflow-/Security-Gates ohne eigenen freigegebenen Scope

Stop: Dokumentation stimmt mit geprüftem Ist-Stand überein; keine Behauptung über ungeprüfte Funktion.

Zusätzlich gilt der diff-basierte Info-Text-Vertrag aus `docs/INFO_TEXT_GOVERNANCE.md`: Änderungen mit Informationswirkung müssen im selben Änderungspaket passende Status-, Prozess-, UX- oder Evidence-Texte nachführen. Der CI-Guard erkennt fehlende Nachführung, schreibt aber niemals selbst Dokumentation.

### Explorer 🔎
Trigger: unbekannter Codepfad, mehrere mögliche Besitzer oder Architekturfrage vor einem Patch.
Modus: read-only.
Stop: relevante Dateien, Datenfluss und maximal drei Risiken benannt.

### Implementierer 🛠️
Trigger: fachlich abtrennbares Modul mit exklusivem Dateibesitz und stabiler Schnittstelle.
Modus: write nur im zugewiesenen Scope.
Stop: Patch + direkte Tests + geänderte Dateien + Restrisiken.

### Testprüfer 🧪

**Berechtigung:** VERIFY, strikt read-only gegenüber dem geprüften Fachblock.

Trigger: nicht-trivialer Patch, Regression oder Release-Gate.

Regeln:
- repariert eigene Befunde nicht selbst;
- verändert keine erwarteten Ergebnisse, um Tests grün zu machen;
- trennt Produktfehler, Testfehler und Infrastrukturfehler;
- meldet PASS/FAIL/OPEN mit reproduzierbarer Prüfanweisung.

Stop: unabhängiger Prüfbericht mit maximal drei Hauptbefunden plus exakten Reproduktionsschritten.

### UX-/Accessibility-Prüfer ♿

**Berechtigung:** VERIFY, read-only.

Trigger: sichtbare GUI-, Fokus-, Navigation-, Theme-, Skalierungs- oder Textänderung.

Stop: Befunde für 100/150/200 %, Tastatur, Fokus, Kontrast und Reduced Motion; keine Reparaturen im selben Prüfauftrag. Sichtbare Kernworkflows werden zusätzlich gegen `docs/LAIEN_QUALITY_STANDARD.md` geprüft; technisches PASS ersetzt kein Laien-PASS.

### Sicherheitsprüfer 🛡️

**Berechtigung:** VERIFY, strikt read-only.

Trigger: Pfade, Schreiben/Löschen/Verschieben, Recovery, Diagnose, Paketierung, Plugins, Netzwerk oder Berechtigungen.

Stop: Angriff-/Fehlerpfade, vorhandene Gates und offene Blocker; keine Selbstreparatur im selben Prüfauftrag.

### Zwei-Anteile-Regel für jeden Update-Prozess

Jede neue Iteration startet mit einem vom Update-Organisator erzeugten Paket:

**A – PLAN-Anteil**
- kommt ausschließlich aus Roadmap, TODO, freigegebenem Masterplan oder offenem Exit-Gate;
- ist der feste Fortschrittsanteil;
- darf nicht durch spontane Optimierungen ersetzt werden.

**B – DELTA-Anteil**
- stammt ausschließlich aus dem unmittelbar vorherigen Lauf;
- wird grundsätzlich für die nächste Iteration eingeplant, außer er blockiert Korrektheit oder Sicherheit der laufenden Iteration;
- Beispiele: CI-Befund, neue Testlücke, erkannte Portabilitätskante, notwendige Doku-/Evidence-Korrektur, klarer technischer Folgepunkt;
- maximal ein DELTA-Thema pro Iteration;
- falls nichts Relevantes entstand: `B = NONE`.

Der Organisator entscheidet:
- Reihenfolge;
- ob B blockierend oder unabhängig ist;
- ob beide Anteile in einem gemeinsamen Branch vertretbar sind;
- ob B wegen Scope-/Freeze-Grenzen nur dokumentiert wird.

**Kein dritter spontaner Arbeitsstrang.**

Standardablauf:

`ORGANIZE → PLAN(A+B) → IMPLEMENT → VERIFY → DOC → EVIDENCE → CI → DIFF → MERGE → POST-MERGE VERIFY → NEXT-PLAN`

### Drei-Schritte-Vorausplanung

Am Ende jeder Iteration werden genau drei wahrscheinliche Folgeschritte kurz vorbereitet. Für jeden werden Ziel, Abhängigkeit, erwarteter Scope und Gate genannt. Diese Vorschau ist Orientierung, keine automatische Freigabe.

### Iterationsstatus

Jede Iteration erhält eine ID `Ixx – Kurzname`, einen Status `🟢 | 🟨 | 🔴 | 🔵 | 🔒` und einen Checkpoint-basierten Fortschrittsbalken wie `████████░░ 80 %`. Prozentwerte dürfen nur definierte Gates abbilden.

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
- genau einem empfohlenen nächsten Schritt;
- den nächsten drei vorgeplanten Schritten in Kurzform.

## 12. Klare Sprache und Regressionslernen

- Nutzertexte beginnen mit der einfachen deutschen Wirkung. Ein notwendiger technischer Name folgt erst danach in Klammern oder als genauer Befehl.
- Status wird nie nur durch Farbe vermittelt, sondern immer durch Zeichen, Wort und bei Fortschritt durch eine Zahl.
- Neue frei wählbare deutsche Dokumentnamen werden deutsch benannt. Bestehende technische Verträge, Programmschnittstellen und gebräuchliche Werkzeugdateien werden nicht allein zur Übersetzung umbenannt, weil dies Links, Prüfungen und Startwege unnötig gefährden würde.
- Terminalbefehle werden vollständig angegeben und unmittelbar in einfacher deutscher Sprache erklärt.
- `docs/REGRESSIONSMANIFEST.json` ist die maschinenlesbare Zuordnung ähnlicher Fehler zu Prüfungen. Nach einem bestätigten Fehler wird zuerst eine bestehende Familie erweitert. Eine neue Familie ist nur zulässig, wenn Ursache und Prüfung wirklich neu sind.
- Der Repository-Gate prüft Schema, eindeutige Kennungen und vorhandene Prüfdateien. Er verändert weder Code noch erwartete Ergebnisse.

### Kurzer Auftrag für Hilfsagenten

Jeder Auftrag verwendet deutsche Rollenwörter und genau diese Reihenfolge:

`Ziel | Bereich | erlaubte Dateien | Nicht-Ziele | Prüfung | Rückgabe | Stopp`

Hilfsagenten vermeiden Abkürzungen und englische Prozesswörter in ihrer Rückgabe, soweit kein genauer Datei-, Befehls- oder Schnittstellenname wiedergegeben werden muss. Der Organisator nennt zusätzlich Fortschritt als belegte Prüfpunkte und die Anzahl offener Schritte.

---

## PROVOWARE GLOBAL DEVELOPMENT CONTRACT

Dieser globale Kern gilt zusätzlich zu den projektspezifischen Regeln. Bei Sicherheits- oder Nachvollziehbarkeitskonflikten hat er Vorrang; lokale Regeln dürfen ihn verschärfen, nicht stillschweigend abschwächen.

- **Frozen Current Plan:** Laufenden freigegebenen Plan nicht durch neue Ideen erweitern; Neues in die nächste Iteration einordnen.
- **Conflict Gate:** Unterbrechen nur bei nachgewiesenem Konflikt mit Planvoraussetzung, Sicherheit, Ausgangs-SHA, Scope oder Invariant.
- **Single Writer:** Pro produktivem Scope nur ein autorisierter Executor; Analyse/Planung/Prüfung dürfen parallel lesen.
- **SHA + Scope:** Vor Mutation HEAD und erlaubten/verbotenen Scope prüfen; keine stillen Nebenrefactorings.
- **Evidence:** Kein PASS ohne echten Test; Evidence muss zum geprüften HEAD gehören.
- **Controlled Evidence Lab:** Echte Mutationen, Fehler-Injektion und Recovery-Tests nur in isolierten Testbereichen; Produktivdaten bleiben geschützt.
- **Next Queue:** Neue Anforderungen/Findings append-only erfassen und Beziehungen wie BLOCKS, REQUIRES, SUPERSEDES, DUPLICATE oder CONFLICTS dokumentieren.
- **Statusklarheit:** OBSERVED/SUSPECTED/REPRODUCED/CONFIRMED/DISPROVED nicht vermischen.
- **Recovery Key:** Nach Abbruch oder Agentenwechsel müssen Stand, Ziel, Frozen Plan, Scope, Findings, Gates und nächster erlaubter Schritt ohne alten Chat rekonstruierbar sein.
- **Traceability:** Requirement/Decision → Finding → Plan → Change → Test/Evidence → Gate/Checkpoint nachvollziehbar halten.
- **Negativtests:** Schutzmechanismen absichtlich gegen falschen SHA, zweiten Writer, Scope-Verstoß und unbelegtes PASS testen.
- **Sichtbarer Fortschritt:** Längere Prüfungen mit Schritt, Fortschritt, Ergebnis und Ampelstatus darstellen.

Leitsatz: **Kein Agent muss sich erinnern. Kein Agent darf raten. Keine Änderung verliert ihren Ursprung. Kein PASS existiert ohne Evidence.**
