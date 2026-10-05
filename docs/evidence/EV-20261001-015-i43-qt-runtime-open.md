# EV-20261001-015 – I43 Qt-Laufzeitvoraussetzung offen

## Ergebnis

- **SETUP:** OPEN
- **I25-AUTO:** OPEN (nicht ausgeführt)
- **I25-HUMAN:** OPEN (nicht ausgeführt)
- **I43 GESAMT:** OPEN

Die ausdrücklich erlaubte lokale Einrichtung erreichte die Qt-Validierung,
konnte sie aber wegen der fehlenden Systembibliothek `libGL.so.1` nicht
abschließen. Der Befund ist eine fehlende Voraussetzung der Prüfungsumgebung,
kein belegter Produktfehler.

## Nachweisdaten

- **Evidence-ID:** `EV-20261001-015`
- **Datum/Uhrzeit:** 2026-10-01 12:29 UTC
- **Commit/Fingerprint:** `e3f11fc341d3bcbd0640f82b872ea1232ad3e74f`
- **Betroffene Anforderungen/Entscheidung:** `REQ-001`, `REQ-004`, `REQ-006`,
  `REQ-BASELINE-1` und `ADR-0001`; kein zugeordneter CR
- **Testumgebung:** nicht-interaktive Linux-Shell; `.venv` war vor dem ersten
  Lauf nicht vorhanden
- **Status:** `OPEN`

## Ablauf und Beobachtung

### Lauf 1 – lokale Umgebung anlegen

```bash
printf 'j\n' | timeout 600s ./start.sh --setup
```

Die erste ausdrückliche Bestätigung erlaubte das Anlegen von `.venv`. Vor der
Paketinstallation verlangte der Starter eine zweite Bestätigung. Da keine
weitere Eingabe vorlag, verwendete er die sichere Ablehnung und installierte
keine Pakete.

- **Exit-Code:** `7`
- **Timeout:** nein
- **Wirkung:** `.venv` angelegt; keine Paket- oder Systeminstallation

### Lauf 2 – gepinnte Pakete lokal installieren und validieren

```bash
printf 'j\n' | timeout 600s ./start.sh --setup
```

Weil `.venv` nun bereits bestand, erreichte die eine Bestätigung dieses Mal
die Frage zur PyPI-Installation. Der Starter installierte PySide6 6.11.2 und
seine gepinnten Bestandteile ausschließlich in `.venv`. Die anschließende
Qt-Validierung scheiterte mit:

```text
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

- **Exit-Code:** `1`
- **Timeout:** nein
- **Wirkung:** gepinnte Pakete nur in `.venv`; keine Systeminstallation

Die identischen Befehle erreichten unterschiedliche Sicherheitsfragen, weil
Lauf 1 den lokalen Zustand durch das Anlegen von `.venv` verändert hatte.

## Erwartung

Setup richtet nach den erforderlichen Bestätigungen ausschließlich die lokale
virtuelle Umgebung ein und validiert die Qt-Laufzeit. Erst nach erfolgreicher
Validierung darf der technische I25-Lauf beginnen. Die menschliche
Verständlichkeitsprüfung bleibt davon getrennt.

## Einordnung und Grenzen

Die Qt-Laufzeit konnte ohne `libGL.so.1` nicht validiert werden. Deshalb wurde
`./start.sh --i25-offscreen` nicht ausgeführt; es entstanden keine
I25-Berichte, Screenshots oder Artefakt-Hashes. Dieser Nachweis belegt weder
technische Barrierefreiheit noch Laienverständlichkeit. Er belegt auch keinen
Produktfehler. Es wurden keine Systempakete installiert und keine Rechte
ausgeweitet.

## Nächster Schritt

Explizit entscheiden, ob und wie `libGL.so.1` in der vorgesehenen
Prüfungsumgebung bereitgestellt werden darf. Bis dahin bleiben Setup,
I25-AUTO und I25-HUMAN `OPEN`; eine Systeminstallation erfolgt nicht
eigenmächtig.
