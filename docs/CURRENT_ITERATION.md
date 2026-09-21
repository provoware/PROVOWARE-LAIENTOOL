# PROVOWARE – Current Iteration

## I17-D – Automated Qt Evidence Pipeline

**Status:** 🟨 IMPLEMENTIERT – PR-/REAL-EVIDENCE-GATES OFFEN
**Fortschritt:** `████████░░ 80 %`

## A – FESTER PLAN

**Ziel:** Die manuelle I17-B-Evidence weitgehend automatisieren und alle sichtbaren Prüf-/Abnahmeinformationen über Chromium führen.

### I17-AUTO

- echte Produktions-`MainWindow` statt Testduplikat;
- 100/150/200-%-Layoutprüfung;
- Widget-Geometrie und Sichtbarkeit;
- explizite Tab-Reihenfolge;
- Tab/Shift+Tab über QtTest;
- Fokus-Screenshot;
- synthetische leere/Unicode-/Leerzeichen-Fixtures;
- read-only Dateivorschau über denselben Application-Core;
- fünf automatische Screenshots;
- HTML/JSON/TXT-Evidence;
- optionaler Offscreen-Modus.

### I17-HUMAN

Nur nach technischem PASS genau eine Frage zur gesamten Laienverständlichkeit.

Die sichtbare Abnahme läuft ausschließlich in Chromium über einen lokalen Loopback-Server auf `127.0.0.1`.

## B – VARIABLE FOLGEAUFGABE

**Quelle:** realer I17-B-Lauf.

**Befund:** Manuelle Screenshot-, Skalierungs- und Tab-Prüfungen waren objektivierbar und erzeugten unnötige Bedienlast.

**Maßnahme:** AUTO und HUMAN werden formal getrennt. Nur die nicht objektivierbare Gesamtwahrnehmung bleibt menschlich.

## Dauerhafter Startvertrag

`start.sh` ist der einzige offizielle Nutzer-Einstiegspunkt.

- neue Nutzerfunktionen müssen über `start.sh` erreichbar sein;
- Runtime-/Venv-/Startänderungen aktualisieren `start.sh` im selben Change-Batch;
- direkte Python-Aufrufe bleiben interne Entwicklungswege;
- der Repository-Gate prüft die Pflichtoptionen des Starters.

## Sicherheitsgrenze

Kein Produkt-Writer, kein Nutzerdatei-Write, keine Rechteausweitung, kein externer Webserver und kein automatisches Human-PASS.

## Exit-Gates

1. neue Contract-Tests PASS;
2. bestehende GUI-/Application-Tests PASS;
3. Repository-Contract PASS;
4. Read-only-Lock PASS;
5. vollständige Suite PASS;
6. PR-Pflichtcheck `repository-contract` PASS;
7. Post-Merge-CI PASS;
8. realer `./start.sh --i17`-Lauf;
9. AUTO PASS + HUMAN PASS;
10. anschließende Repository-Aktualitäts-/Hygieneanalyse.

## Nächste drei Schritte

1. 🔵 I17-D PR/CI abschließen und realen Chromium-Lauf ausführen.
2. 🔵 Repository-Hygiene/Aktualität/Datenmüll analysieren und nur sichere Bereinigungen ableiten.
3. 🔒 I25 erst nach vollständigem I17-PASS öffnen.
