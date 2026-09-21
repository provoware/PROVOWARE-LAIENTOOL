# PROVOWARE – Current Iteration

## I09 – Zweitgeräte-Portabilitäts-Evidence

**Status:** 🟢 REPOSITORY-ANTEIL ABGESCHLOSSEN / PHYSISCH OPEN
**Fortschritt:** `█████████░ 90 %`

Der Prozentwert bildet ausschließlich die definierten Checkpoints dieser Iteration ab.

## A – FESTER PLAN

**Quelle:** I08-Drei-Schritte-Vorausplanung + offenes B01-Exit-Gate.

**Ziel:** die physische Zweitgeräte-Prüfung reproduzierbar, datensparsam und laiengerecht vorbereiten, ohne Schein-PASS für ein Gerät zu erzeugen, auf das diese Iteration keinen physischen Zugriff besitzt.

**Checkpoints:**

- 🟢 Evidence-Runner dependency-frei angelegt
- 🟢 realen Preflight-JSON-Vertrag gegengeprüft
- 🟢 Datenschutz-Redaktion auf reale verschachtelte Struktur angepasst
- 🟢 Unit-Tests für Redaktionsvertrag ergänzt
- 🟢 Laien-Anleitung für Zweitgerät erstellt
- 🟢 Repository-/PR-CI-Gates PASS
- 🟢 finaler Diff ohne Scope-Drift
- 🔵 Merge/Post-Merge-Prüfung
- 🟨 reale physische Ausführung auf Zweitgerät bleibt anschließend separat OPEN

## B – VARIABLE FOLGEAUFGABE

**Quelle letzter Lauf:** I08-Abschlussdatei enthielt trotz grünem Post-Merge-CI noch den alten Hinweis „Post-Merge-Prüfung folgt“.

**Priorität:** Dokumentationsdrift.

**Maßnahme:** I09 übernimmt den bestätigten I08-Post-Merge-Stand als abgeschlossen; kein Produktpatch erforderlich.

**Status:** 🟢 erledigt.

## Datei-Besitz dieser Iteration

| Datei | Schreibender Besitzer | Prüfer |
| --- | --- | --- |
| `scripts/second_device_evidence.py` | IMPLEMENT | VERIFY read-only |
| `tests/test_second_device_evidence.py` | IMPLEMENT | VERIFY read-only |
| `docs/B01_SECOND_DEVICE_EVIDENCE.md` | DOC | VERIFY read-only |
| `docs/B01_PLATFORM_PREFLIGHT.md` | DOC | VERIFY read-only |
| `docs/evidence/EV-20260921-002-b01a-preflight.md` | DOC | VERIFY read-only |
| `docs/CURRENT_ITERATION.md` | ORGANIZE/DOC | VERIFY read-only |
| `README.md` | DOC | VERIFY read-only |
| `todo.txt` | DOC | VERIFY read-only |
| `scripts/repo_quality.py` | PROCESS-IMPLEMENT | VERIFY read-only |

## Nicht-Ziele

- keine Behauptung, dass die zweite physische Maschine bereits geprüft wurde;
- keine Installation;
- kein Netzwerkzugriff;
- keine GUI-Implementierung;
- keine Nutzdaten-Schreiboperation;
- keine Änderung der eingefrorenen Baseline.

## Exit-Gates

1. neuer Evidence-Runner Unit-Test PASS.
2. bestehende B01-Tests PASS.
3. Repository-Contract PASS.
4. Info-Text-Impact PASS.
5. Preflight Text/JSON PASS.
6. finaler Diff ohne Scope-Drift.
7. Post-Merge-CI PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 I10 – gemeinsame Capability-/Use-Case-Registry
**Ziel:** zentralen Fachfunktionskatalog schaffen, aus dem GUI und Konsolenmenü dieselben Funktionen beziehen.
**Abhängigkeit:** I09 Repository-Teil muss grün eingefroren sein.
**Gate:** keine doppelte Fachlogik; Registry-Tests; weiterhin read-only.

### 2. 🔵 I11 – minimaler read-only UX-/CLI-Shell-Prototyp
**Ziel:** erste navigierbare PySide6-Shell und äquivalentes Konsolen-Zahlenmenü auf demselben Core-Vertrag.
**Abhängigkeit:** I10 Registry.
**Gate:** Laienstandard, Tastatur, 100/150/200 %, Paritätstest und keine Nutzdaten-Schreiboperation.

### 3. 🔵 I12 – Preview-Modell vorbereiten
**Ziel:** B05 als rein fachliches immutable Preview-Modell für spätere Dateiaktionen entwerfen, noch ohne Executor.
**Abhängigkeit:** gemeinsame Use-Case-Grenzen aus I10.
**Gate:** Wirkung, Quelle, Zielgrenzen und Rückweg modelliert; keinerlei produktiver Schreibpfad.
