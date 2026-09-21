# PROVOWARE – Current Iteration

## I14 – reale Shell-/Accessibility-Evidence

**Status:** 🔴 AUTOMATISCHER BEFUND / 🟨 REALER DESKTOP-LAUF OPEN
**Fortschritt:** `██████░░░░ 60 %`

Der Prozentwert bildet ausschließlich definierte I14-Evidence-Checkpoints ab.

## A – FESTER PLAN

**Quelle:** I13-Drei-Schritte-Vorausplanung + B04 + LAIEN_QUALITY_STANDARD.

**Ziel:** die I11-Shell reproduzierbar gegen Skalierung, Tastatur, Fokus, Kontrast, Reduced Motion und Laienverständlichkeit prüfen, ohne ungeprüfte Eigenschaften als PASS zu behaupten.

**Checkpoints:**

- 🟢 dependency-freier read-only Evidence-Runner
- 🟢 vier Theme-Familien automatisch auf Kontrast geprüft
- 🟢 100/150/200-%-Stylesheetvertrag automatisch geprüft
- 🔴 expliziter Fokusvertrag unvollständig: ComboBox/TextEdit ohne eigene `:focus`-Regel
- 🟢 Laufzeitumgebung PySide6/Display wird nur als Fakt erfasst
- 🟨 reale 100-%-Bildschirmprüfung OPEN
- 🟨 reale 150-%-Bildschirmprüfung OPEN
- 🟨 reale 200-%-Bildschirmprüfung OPEN
- 🟨 echter Tastaturpfad OPEN
- 🟨 sichtbarer Fokus im realen Rendering OPEN
- 🟨 Reduced-Motion-/Bewegungsprüfung OPEN
- 🟨 Laienverständlichkeit OPEN
- 🟢 Repository-/PR-CI-Gates PASS
- 🟢 finaler Diff ohne Scope-Drift
- 🔵 Merge / Post-Merge

## B – VARIABLE FOLGEAUFGABE

**Quelle letzter Lauf:** I13 war bereits gemergt und Post-Merge-CI grün, während `CURRENT_ITERATION.md` noch „Merge / Post-Merge“ als offen auswies.

**Priorität:** Dokumentationsdrift.

**Maßnahme:** I14 startet vom bestätigten grünen I13-`main`; der alte offene Merge-/Post-Merge-Status wird ersetzt.

**Status:** 🟢 erledigt.

## Neuer Befund für die nächste Iteration

Der I14-Prüfer hat einen neuen Accessibility-Befund erzeugt:

- `QPushButton:focus` vorhanden;
- `QComboBox:focus` fehlt;
- `QTextEdit:focus` fehlt.

Dieser Befund wird **nicht** im selben VERIFY-Auftrag repariert. Er wird als nächster DELTA-Anteil vorgemerkt.

## Datei-Besitz dieser Iteration

| Datei | Schreibender Besitzer | Prüfer |
| --- | --- | --- |
| `scripts/accessibility_evidence.py` | EVIDENCE-IMPLEMENT | VERIFY read-only |
| `tests/test_accessibility_evidence.py` | TEST-SCOPE | VERIFY read-only |
| `docs/I14_ACCESSIBILITY_EVIDENCE.md` | DOC | VERIFY read-only |
| `docs/evidence/EV-20260921-004-i14-accessibility.md` | DOC/EVIDENCE | VERIFY read-only |
| `docs/CURRENT_ITERATION.md` | ORGANIZE/DOC | VERIFY read-only |
| `README.md` | DOC | VERIFY read-only |
| `todo.txt` | DOC | VERIFY read-only |
| `scripts/repo_quality.py` | PROCESS-IMPLEMENT | VERIFY read-only |

## Nicht-Ziele

- keine Reparatur des geprüften GUI-Stylesheets;
- keine GUI-Funktionserweiterung;
- kein Dateiinventar;
- keine Dateioperation;
- keine Installation von PySide6;
- kein virtueller Display-Lauf als Ersatz für reale Nutzer-Evidence;
- kein behauptetes Laien-PASS ohne reale Prüfung.

## Exit-Gates

1. Evidence-Runner-Unit-Tests PASS.
2. vollständige Test-Suite PASS.
3. Repository-Contract PASS.
4. Info-Text-Impact PASS.
5. automatisierte Befunde reproduzierbar.
6. reale manuelle Gates korrekt als OPEN dokumentiert.
7. finaler Diff ohne Scope-Drift.
8. Post-Merge-CI PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I15 – read-only Dateiinventar + I14-Fokus-DELTA
**Ziel A:** Downloads ausschließlich lesend inventarisieren und valide Preview-Eingaben erzeugen.
**DELTA B:** explizite Fokusregeln für ComboBox/TextEdit separat implementieren und erneut read-only prüfen.
**Gate:** keine Schreiboperation; Fokusvertrag danach automatisiert grün; reale Desktop-Evidence bleibt separat erforderlich.

### 2. 🔵 I16 – Preview-Application-Use-Case
**Ziel:** Inventar → Preview fachlich verbinden und identisch in GUI/CLI verfügbar machen.
**Abhängigkeit:** I15 Inventar.
**Gate:** keine Persistenz, kein Executor, GUI-/CLI-Parität.

### 3. 🔵 I17 – I14 realer Zielsystem-Lauf abschließen
**Ziel:** nach Fokuskorrektur die echte PySide6-Shell auf Zielhardware mit 100/150/200 %, Tastatur und Laienprofil prüfen.
**Abhängigkeit:** Fokus-DELTA grün und reale Zielmaschine verfügbar.
**Gate:** dokumentiertes PASS/FAIL/OPEN ohne künstliche Hochstufung.
