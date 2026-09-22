# PROVOWARE – Info-Text-Governance

## Ziel

README, TODO, Evidence, Architektur- und Hilfetexte dürfen dem Code nicht hinterherlaufen. Änderungen mit Informationswirkung lösen deshalb einen **Dokumentations-Impact-Check** aus.

CI aktualisiert Texte nicht selbst. Sie erkennt, **welche Informationsklasse betroffen ist**, und blockiert einen PR, wenn kein passender Info-Text mitgeführt wurde. Inhaltliche Änderungen bleiben bewusst beim DOC-Agenten bzw. Menschen.

## 1. Informationsklassen

| Klasse | Beispiele | Zweck |
| --- | --- | --- |
| Status | `README.md`, `todo.txt` | Was ist real vorhanden, offen, gesperrt? |
| Navigation | `docs/README.md` | Wo liegt die führende Detailquelle? |
| Bedienung | UI-/Workflow-Dokumente | Was sieht und versteht ein Nutzer? |
| Sicherheit | B01/B05/B06-Dokumente, Evidence | Welche Grenzen und Rückwege gelten? |
| Architektur | ADRs | Warum wurde eine technische Grenze gewählt? |
| Prozess | `AGENTS.md`, `UPDATE_ORCHESTRATION.md` | Wie wird entwickelt und geprüft? |
| Nachweis | `docs/evidence/**` | Was wurde konkret geprüft? |
| Register | `docs/DATEIENREGISTER.md` | Welche Datei führt welchen Stand und wann wird sie gepflegt? |

## 2. Trigger

Der Guard `scripts/info_text_guard.py` prüft den Diff gegen den Basis-Commit.

### Produktkern geändert

Trigger:
- `src/**`
- `start.py`

Erwartung: mindestens eine passende Status-, Fach- oder Evidence-Datei wird im selben Änderungspaket aktualisiert.

### Entwicklungs-/CI-Vertrag geändert

Trigger:
- `AGENTS.md`
- `.github/**`
- `scripts/repo_quality.py`
- `scripts/info_text_guard.py`

Erwartung: Prozess-/Statusdokumentation wird mitgeführt.

### UI-/Laienwirkung geändert

Triggernamen enthalten z. B. `ui`, `gui`, `theme`, `wizard`, `dialog`.

Erwartung: `docs/UI_DESIGN_SYSTEM.md`, `docs/LAIEN_QUALITY_STANDARD.md`, passende Evidence oder README/TODO wird aktualisiert.

## 3. Anti-Scheinaktualisierung

Ein Text-Commit darf nicht nur Datum, Leerzeichen oder Statussymbol ändern, um den Guard zu erfüllen. Review und Evidence prüfen weiterhin den Inhalt.

Der Guard ist ein **Staleness-Sensor**, kein Wahrheitsautomat.

## 4. Schreibdisziplin

1. Implementierer ändert Produktcode.
2. VERIFY prüft unabhängig.
3. DOC übernimmt ausschließlich bestätigte Fakten.
4. Info-Texte werden erst auf `PASS` gesetzt, wenn passende Evidence existiert.
5. Ungeprüfte Funktionen werden als `OPEN` bezeichnet.
6. README ist Übersicht, nicht zweite Spezifikation.
7. Baseline bleibt unverändert, solange kein expliziter Change Request sie öffnet.
8. Flüchtiger PR-/Merge-/CI-Livestatus bleibt in GitHub; dauerhafte Texte speichern Capability-, OPEN-/LOCKED- und historische Evidence-Zustände.

## 5. Erweiterung neuer Info-Texte

Neue dauerhafte Textdateien werden nur angelegt, wenn sie eine eigene stabile Verantwortung besitzen.

Vor neuer Datei prüfen:

- Kann der Inhalt in einem bestehenden Dokument eindeutig gepflegt werden?
- Gibt es einen klaren Besitzer?
- Gibt es einen Trigger, wann der Text aktualisiert werden muss?
- Gibt es Überschneidungen mit README, ADR, TODO oder Evidence?

Wenn nein: bestehende Datei erweitern statt Dokumentationsfläche vergrößern.

## 6. Dauerhafter Status und Navigation

Der aktuelle GitHub-Workflow-/Merge-Zustand wird nicht in README/TODO gespiegelt. Das vermeidet zwangsläufige Drift direkt nach einem Merge.

- README/TODO verwenden dauerhafte Aussagen wie `PASS`, `OPEN`, `LOCKED` oder konkrete Capability-Fakten.
- Historische Run-/Commit-IDs gehören in Evidence oder Abschlussnotizen.
- [Dokumentationsindex](README.md) ist die Navigationsquelle; neue `docs/I??_*.md` werden dort verlinkt.
- [Wartbarkeitsvertrag](MAINTENANCE.md) definiert die Pflege- und Quellen-der-Wahrheit-Regeln.
- [Register der Informationsdateien](DATEIENREGISTER.md) hält Zustand, Pflegeanlass und Besitzer der führenden Quellen fest.
- `scripts/repo_quality.py` prüft interne Markdown-Links, Iterationsindex, Python-Syntax und typische Tabellenbruch-Artefakte.

## 7. Abnahmeregel

Ein PR mit Informationswirkung ist erst mergefähig, wenn:

- der Impact-Guard grün ist;
- Statusangaben nicht dem realen Repository widersprechen;
- neue Behauptungen durch Test/Evidence gedeckt sind;
- keine ungeprüfte Funktion als fertig dargestellt wird.
