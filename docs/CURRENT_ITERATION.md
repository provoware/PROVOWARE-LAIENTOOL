# PROVOWARE – Current Iteration

## I15 – read-only Dateiinventar + I14-Fokus-DELTA

**Status:** 🟨 B-DELTA IMPLEMENTIERT / VERIFY AUSSTEHEND
**Fortschritt:** `███░░░░░░░ 30 %`

Der Prozentwert bildet ausschließlich definierte I15-Checkpoints ab.

## Reihenfolge

Der bestätigte Accessibility-Befund aus I14 blockiert den Start des neuen Inventar-Write-Batches.

Deshalb:

1. **B – DELTA zuerst:** Fokusvertrag reparieren und separat verifizieren.
2. **A – PLAN danach:** ausschließlich read-only Inventarkern implementieren.

Kein paralleler Schreibzugriff auf beide Blöcke.

## B – DELTA: I14-Fokusvertrag

**Quelle:** bestätigter I14-Befund.

**Ziel:** explizite Fokusdarstellung für alle fokussierbaren I11-Kernwidgets im eigenen Stylesheet sicherstellen.

**Umgesetzt:**

- 🟢 `QPushButton:focus` bleibt erhalten
- 🟢 `QComboBox:focus` ergänzt
- 🟢 `QTextEdit:focus` ergänzt
- 🟢 automatisierte Erwartung auf drei PASS-Fokusregeln aktualisiert
- 🟢 automatische Gesamtwertung erwartet danach `PASS`, reale manuelle Gates bleiben `OPEN`
- 🔵 unabhängiges CI-/Regression-Gate ausstehend

**Nicht behauptet:**

- kein reales Bildschirm-PASS;
- kein 200-%-Clipping-PASS;
- kein vollständiger Tastaturpfad-PASS;
- kein Laien-PASS.

## A – FESTER PLAN: read-only Dateiinventar

**Status:** 🔒 NOCH NICHT GESTARTET

**Ziel:** eine explizit gewählte und B01-validierte Wurzel ausschließlich lesend rekursiv inventarisieren.

Geplanter Minimalvertrag:

- immutable Inventarobjekte;
- reguläre Dateien mit relativem Pfad und Byte-Größe;
- deterministische Sortierung;
- Unicode und Leerzeichen;
- Symlinks nicht verfolgen;
- Zugriffs-/Race-Fehler als immutable Befund statt Absturz;
- keinerlei Hashing, Klassifizierung, Preview-Plan oder GUI/CLI-Use-Case.

## Datei-Besitz – B-DELTA

| Datei | Schreibender Besitzer | Prüfer |
| --- | --- | --- |
| `src/provoware_laientool/ui_themes.py` | IMPLEMENT | VERIFY read-only |
| `tests/test_accessibility_evidence.py` | TEST-SCOPE | VERIFY read-only |
| `docs/CURRENT_ITERATION.md` | ORGANIZE/DOC | VERIFY read-only |

## Nicht-Ziele des DELTA

- keine Layout-Änderung;
- keine neuen Farben;
- keine GUI-Funktion;
- keine Änderung am Evidence-Runner;
- keine künstliche Hochstufung der realen I14-Gates.

## Gate vor I15-A

1. Repository-Contract PASS.
2. vollständige Tests PASS.
3. Accessibility-Evidence automatisiert `PASS`.
4. Gesamtstatus des Evidence-Runners bleibt wegen manueller Gates `OPEN`.
5. finaler DELTA-Diff ohne Scope-Drift.

Erst danach beginnt der Inventar-Write-Batch.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I15-A – read-only Inventarkern
**Abhängigkeit:** Fokus-DELTA vollständig grün.
**Gate:** nur lesen; B01-Pfadgrenzen; Symlink-Sperre; Unicode/Leerzeichen; Fehlerfälle.

### 2. 🔵 I16 – Preview-Application-Use-Case
**Abhängigkeit:** I15-Inventar grün.
**Gate:** Inventarfakten → Preview; GUI-/CLI-Parität; weiterhin kein Executor.

### 3. 🔵 I17 – realer I14-Zielsystemlauf
**Abhängigkeit:** automatisierter Fokusvertrag grün.
**Gate:** echte 100/150/200-%-, Tastatur-, Fokus- und Laien-Evidence.
