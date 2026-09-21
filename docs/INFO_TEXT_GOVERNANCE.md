# PROVOWARE – Info-Text-Governance

## Ziel

README, TODO, Evidence, Architektur- und Hilfetexte dürfen dem Code nicht hinterherlaufen. Änderungen mit Informationswirkung lösen deshalb einen **Dokumentations-Impact-Check** aus.

CI aktualisiert Texte nicht selbst. Sie erkennt, **welche Informationsklasse betroffen ist**, und blockiert einen PR, wenn kein passender Info-Text mitgeführt wurde. Inhaltliche Änderungen bleiben bewusst beim DOC-Agenten bzw. Menschen.

## 1. Informationsklassen

| Klasse | Beispiele | Zweck |
| --- | --- | --- |
| Status | `README.md`, `todo.txt` | Was ist real vorhanden, offen, gesperrt? |
| Bedienung | UI-/Workflow-Dokumente | Was sieht und versteht ein Nutzer? |
| Sicherheit | B01/B05/B06-Dokumente, Evidence | Welche Grenzen und Rückwege gelten? |
| Architektur | ADRs | Warum wurde eine technische Grenze gewählt? |
| Prozess | `AGENTS.md`, `UPDATE_ORCHESTRATION.md` | Wie wird entwickelt und geprüft? |
| Nachweis | `docs/evidence/**` | Was wurde konkret geprüft? |

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

## 5. Erweiterung neuer Info-Texte

Neue dauerhafte Textdateien werden nur angelegt, wenn sie eine eigene stabile Verantwortung besitzen.

Vor neuer Datei prüfen:

- Kann der Inhalt in einem bestehenden Dokument eindeutig gepflegt werden?
- Gibt es einen klaren Besitzer?
- Gibt es einen Trigger, wann der Text aktualisiert werden muss?
- Gibt es Überschneidungen mit README, ADR, TODO oder Evidence?

Wenn nein: bestehende Datei erweitern statt Dokumentationsfläche vergrößern.

## 6. Abnahmeregel

Ein PR mit Informationswirkung ist erst mergefähig, wenn:

- der Impact-Guard grün ist;
- Statusangaben nicht dem realen Repository widersprechen;
- neue Behauptungen durch Test/Evidence gedeckt sind;
- keine ungeprüfte Funktion als fertig dargestellt wird.
