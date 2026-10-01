# EV-20261001-014 – I42 Transfer-Barrierefreiheitsprüfung offen

## Ergebnis

- **I25-AUTO:** OPEN
- **I25-HUMAN:** OPEN
- **I42 GESAMT:** OPEN

Die Prüfung hat nicht begonnen. Der offizielle Starter hat vor dem
technischen Lauf sicher angehalten, weil die lokale virtuelle Umgebung
`.venv` fehlt und ihre Einrichtung nicht bestätigt wurde.

## Nachweisdaten

- **Evidence-ID:** `EV-20261001-014`
- **Datum/Uhrzeit:** 2026-10-01 11:50 UTC
- **Commit/Fingerprint:** `e98b94e4fc67c874ec941b2c8221bce9b2f0d75a`
- **Betroffene Anforderungen/Entscheidung:** `REQ-001`, `REQ-004`, `REQ-006`,
  `REQ-BASELINE-1` und `ADR-0001`; kein zugeordneter CR
- **Testumgebung:** nicht-interaktive Linux-Shell; `.venv` war nicht vorhanden
- **Status:** `OPEN`

## Ablauf

```bash
timeout 240s ./start.sh --i25-offscreen
```

Der Befehl begrenzt den technischen I25-Lauf auf 240 Sekunden. Der Starter
fragte, ob `.venv` ausschließlich im Projektordner angelegt werden soll. In der
nicht-interaktiven Umgebung wurde die sichere Standardantwort verwendet: keine
Einrichtung.

## Erwartung

Der technische I25-Lauf prüft die sichtbare Transfer-Vorschau bei 100, 150 und
200 Prozent, Tastatur und Fokus sowie die vorhandenen Sicherheitsgrenzen. Ein
technisches PASS wäre nur nach tatsächlichem Abschluss dieses Laufs zulässig.
Die menschliche Verständlichkeitsprüfung bleibt davon getrennt.

## Beobachtung

Der Starter meldete die fehlende `.venv`, bot ihre lokale Einrichtung an und
brach nach der nicht bestätigten Frage ohne Installation ab. Der technische
Evidence-Lauf wurde daher nicht ausgeführt. Das war kein Timeout.

- **Exit-Code:** `4`
- **Technisches Gate:** `OPEN`
- **Human-Gate:** `OPEN` (nicht ausgeführt)
- **Produktfreigabe:** unverändert; Copy/Move bleibt nicht READY

## Artefakte und Grenzen

Es entstanden keine I25-Berichte, Screenshots oder Hashes, weil der Starter vor
dem Evidence-Lauf anhielt. Dieser Nachweis belegt nur den sicheren Abbruch bei
fehlender, nicht ausdrücklich genehmigter Umgebung. Er belegt weder technische
Barrierefreiheit noch Laienverständlichkeit.

## Nächster Schritt

Nach ausdrücklicher Erlaubnis `.venv` über `./start.sh --setup` anlegen und
danach I25 technisch und menschlich prüfen.
