# Optimierungsprotokoll 2026-10-21

## Lesende Diagnose ohne GUI

Problem: Der bestehende P1-Eintrag in todo.txt und die Projektanalyse
docs/I42_STATUS_AND_PRIORITIES.md dokumentieren die Abhängigkeit der
read-only Befehle von der GUI-Installation.

Änderung: Sechs read-only Modi in start.sh starten nun vor der
Venv-/PySide6-Prüfung über das System-Python. GUI- und Evidence-Modi
bleiben unverändert gesichert. README und TODO wurden angepasst.

Mehrwert: Preflight und Diagnose sind bei fehlender GUI erreichbar,
ohne Dateien zu verändern oder Pakete zu installieren.

Tests: Zwei neue isolierte Vertragstests für die sechs Core-Modi
und die unveränderte GUI-Abhängigkeit.
Statische Prüfung: PASS.
Vollständige lokale Suite: BLOCKED (kein Checkout erreichbar).
GitHub-CI: OPEN bis zum echten Nachweis auf dem finalen Commit.

Risiko: Preflight beobachtet System-Python statt einer möglichen
Projekt-Venv. Human-Freigaben und Zweitgeräteprüfung bleiben OPEN.

Basis: https://github.com/provoware/PROVOWARE-LAIENTOOL/commit/61a16be20696a7a44a7370429a7cb13cbd63b1b9
Commit: https://github.com/provoware/PROVOWARE-LAIENTOOL/commit/0ef628c8ee4d55855ca9e1556aaef2dc92516738
PR-Vergleich: https://github.com/provoware/PROVOWARE-LAIENTOOL/compare/main...fix/core-diagnostics-without-venv-20261021
PR: Noch nicht bestätigt.

Nächster Schritt: GitHub-CI abwarten und nur nach bestandener
Prüfkette eine Freigabeentscheidung treffen. main bleibt unverändert.
