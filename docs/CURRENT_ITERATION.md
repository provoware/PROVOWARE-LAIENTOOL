# PROVOWARE – Current Iteration

## I17-C – Venv-first Runtime-Härtung für I17-B

**Status:** 🟨 INFRASTRUKTUR-PATCH IMPLEMENTIERT – REALER ZIELSYSTEMLAUF DANACH OFFEN
**Fortschritt:** `███████░░░ 70 %`

**Basis:** `7687147510090642369942f82c0e7b713f081f7c`

## A – FESTER PLAN

**Ziel:** Den realen I17-B-Zielsystemlauf auf eine projektlokale, validierte Python-`.venv` umstellen, damit System-Python und GUI-Abhängigkeiten nicht auseinanderlaufen.

### Befund aus echtem Zielsystemlauf

- System-Python: 3.14.4;
- Display-Session: Wayland vorhanden;
- automatisierter Accessibility-Vertrag: PASS;
- PySide6 im System-Python: nicht vorhanden;
- I17 blieb deshalb korrekt OPEN.

### Umgesetzter Infrastrukturblock

- neuer Standardstarter `start.sh`;
- `.venv` als verbindliche Projekt-Runtime;
- Python-Vertrag `>=3.10,<3.15`;
- PySide6 fest auf `6.11.2` gepinnt;
- `--check`, `--setup`, `--gui`, `--menu`, `--preflight`, `--json`, `--i17`;
- keine Systeminstallation und keine Rechteausweitung;
- explizite Zustimmung vor Venv-Erzeugung und PyPI-Installation;
- `--yes` nur als ausdrücklicher nicht-interaktiver Opt-in;
- Vor-/Nachvalidierung von Venv, PySide6 und QtWidgets;
- atomare Erst-Erzeugung über `.venv.tmp`;
- Regressionstests für Dependency-Pin, Venv-first und Privilegschutz.

## B – VARIABLE FOLGEAUFGABE

**Quelle:** realer I17-B-Lauf.

**Befund:** `.gitignore` enthielt bereits `.venv/`, aber das Repository besaß keinen Bootstrap, der diese Umgebung tatsächlich erzeugt und für GUI/I17 erzwingt.

**Maßnahme:** Venv-first wird als dauerhafter Runtime-Vertrag formalisiert; direkte GUI-/I17-Aufrufe über zufälliges System-Python sind nicht mehr der empfohlene Nutzerweg.

## Sicherheitsgrenze

Kein:

- `sudo`/`apt`;
- Schreiben in System-Python;
- automatischer Download ohne explizite Zustimmung;
- Produkt-Executor;
- Copy/Move/Trash;
- Rechteausweitung.

## Exit-Gates

1. Venv-Bootstrap-Vertragstests PASS.
2. Repository-Contract PASS.
3. Read-only-Lock PASS.
4. vollständige Suite PASS.
5. PR-Pflichtcheck `repository-contract` PASS.
6. Post-Merge-Main-CI PASS.
7. danach echter Lauf `./start.sh --i17`.
8. I17-B erst nach vollständiger visueller Evidence PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 Realer I17-B-Lauf über Venv-Starter
`./start.sh --i17`

### 2. 🔒 I25 – Adapter-Implementierung
Erst nach grünem realem I17-Befund.

### 3. 🔵 I27 – Writer-spezifischer Guard Decision/Prototype
Weiterhin ohne produktiven Writer bis zum eigenen Guard-/No-clobber-Nachweis.
