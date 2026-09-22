# PROVOWARE – Update-Organisator und Zwei-Spuren-Prozess

## Ziel

Jede Iteration besteht aus genau zwei logisch getrennten Anteilen und einer verpflichtenden kollisionsfreien Datei-Besitzplanung:

- **A – PLAN:** verbindlicher nächster Schritt aus dem bestehenden Entwicklungsplan.
- **B – DELTA:** genau ein neuer, aus dem letzten Lauf entstandener Folgepunkt.

Damit bleibt die Entwicklung planstabil, reagiert aber trotzdem kontrolliert auf neue Befunde.

## Rollenmatrix

| Rolle | Modus | Darf Produktcode ändern? | Hauptzweck |
| --- | --- | ---: | --- |
| Update-Organisator | ORGANIZE | Nein | Reihenfolge, A/B-Auswahl, Scope-Kontrolle |
| Planer | PLAN | Nein | technischen Block zerlegen und Gates definieren |
| Explorer | PLAN/READ | Nein | Codepfade und Abhängigkeiten aufklären |
| Implementierer | IMPLEMENT | Ja, exklusiver Scope | freigegebenen Block umsetzen |
| Testprüfer | VERIFY | Nein | unabhängige Funktions-/Regressionprüfung |
| Sicherheitsprüfer | VERIFY | Nein | Sicherheitsgrenzen prüfen |
| UX-/Accessibility-Prüfer | VERIFY | Nein | Bedienbarkeit/Accessibility prüfen |
| Dokumentar | DOC | Nur Dokumentation | geprüften Ist-Stand nachführen |

## Organisator-Algorithmus

1. aktuellen `main`-Fingerprint und letzte Evidence lesen;
2. letzten PLAN-/DELTA-Abschluss prüfen;
3. nächsten offenen Planpunkt bestimmen;
4. neue Befunde des letzten Laufs sammeln;
5. Befunde priorisieren:
   `Blocker > Security > Regression > Evidence/Testlücke > Wartbarkeit > Komfort`;
6. genau einen DELTA-Kandidaten auswählen oder `NONE`;
7. Abhängigkeit zwischen A und B bestimmen;
8. Reihenfolge festlegen;
9. erlaubte Dateien und Nicht-Ziele definieren;
10. Gates und Stop-Bedingungen ausgeben;
11. Datei-Besitzmatrix festlegen;
12. nach Abschluss genau drei wahrscheinliche Folgeschritte vorplanen.

## Entscheidungslogik

### B blockiert A
Beispiel: letzter Lauf zeigt falsche Pfadvalidierung, während der Plan den Scanner starten würde.

Reihenfolge:
**B → Verify → A**

### B ist unabhängig
Beispiel: fehlende Evidence-Beschreibung, während A einen separaten read-only Kern ergänzt.

Reihenfolge:
**A → Verify → B/DOC**

### B verletzt Freeze-/Scope-Grenze
B wird dokumentiert und in die variable Folgeliste der nächsten Iteration verschoben. Es wird **nicht** heimlich mitimplementiert.

### Kein B vorhanden
`B = NONE`. Es wird kein künstlicher Zusatzscope erfunden.

## Update-Paket

Vor jeder Implementierung:

```text
UPDATE-ID:
BASE-SHA:

A – PLAN
Quelle:
Ziel:
Erlaubte Dateien:
Nicht-Ziele:
Tests:
Exit-Gate:

B – DELTA
Quelle letzter Lauf:
Priorität:
Ziel:
Erlaubte Dateien:
Nicht-Ziele:
Tests:
Exit-Gate:

REIHENFOLGE:
BLOCKER:
DATEI-BESITZ:
- <datei>: <einziger schreibender Besitzer>

ITERATIONSSTATUS:
FORTSCHRITT:

NÄCHSTE 3 SCHRITTE:
1.
2.
3.

MERGE-KRITERIUM:
```

## Anti-Drift-Regeln

- maximal ein PLAN- und ein DELTA-Anteil;
- kein dritter opportunistischer Patch;
- Prüfer ändern den geprüften Block nicht;
- Dokumentar dokumentiert nur belegte Ergebnisse;
- Organisator schreibt keinen Produktcode;
- Implementierer erweitert den Scope nicht selbst;
- neue Erkenntnisse während der Implementierung werden als Kandidaten für den **nächsten** DELTA-Anteil gesammelt, außer sie blockieren die aktuelle Korrektheit oder Sicherheit;
- pro Datei existiert während eines Write-Batches genau ein schreibender Besitzer;
- Prüfer berichten ausschließlich read-only und reparieren ihre Befunde nicht selbst;
- Planer implementieren nicht;
- Dokumentar schreibt erst nach bestätigter Prüfung;
- kollidierende Änderungen werden serialisiert;
- jede Iteration endet mit drei vorgeplanten, noch nicht automatisch freigegebenen Folgeschritten;
- identische fehlgeschlagene Tests werden ohne Zustandsänderung höchstens einmal reproduziert;
- pro Root Cause sind höchstens zwei gezielte Reparaturzyklen erlaubt; danach wird neu geplant;
- Full Suite folgt targeted Tests und wird nicht als Fehlersuchschleife verwendet;
- Timeout/Hänger ist ein eigener Befund und darf keinen automatischen Retry-Zyklus auslösen;
- ein Lauf ohne neue Hypothese oder neue Evidence wird nicht wiederholt.

## Iterationsanzeige

Jede Iteration verwendet:

- `🟢` abgeschlossen / belegt
- `🟨` in Arbeit / OPEN
- `🔴` blockiert / fehlgeschlagen
- `🔵` geplant
- `🔒` gesperrt

Zusätzlich wird ein Checkpoint-basierter Balken ausgegeben, z. B. `██████░░░░ 60 %`.

## GUI-/Konsolen-Parität

Jede fachliche GUI-Funktion muss einen gleichwertigen Konsolenweg über ein laienfreundliches Zahlenmenü besitzen. Die Detailregeln stehen in `docs/GUI_CLI_PARITY.md`. GUI und CLI bleiben Adapter desselben Application-/Domain-Kerns.

## Beispiel für den aktuellen Stand

**A – PLAN:** B01-B Pfad-/Symlink-Sicherheitsmodell.
**B – DELTA:** aus B01-A bleibt die reale Zweitgeräte-Portabilitäts-Evidence offen.

Bewertung:
B blockiert B01-B nicht. Daher wird A zuerst umgesetzt; B bleibt als klarer Evidence-/Portabilitäts-Folgepunkt erhalten und darf nicht in Pfadlogik vermischt werden.

## Repository-Quality-Verantwortungen

`scripts/repo_quality.py` bleibt der einzige stabile Einstiegspunkt für den Repository-Contract. Die eigentlichen Prüffamilien liegen wartbar getrennt unter `scripts/repo_quality_checks/`. Änderungen an diesen Modulen gelten weiterhin als Änderung des Entwicklungs-/CI-Vertrags und müssen deshalb gemeinsam mit passender Prozessdokumentation geprüft werden.
