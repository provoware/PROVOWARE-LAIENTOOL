# I40 – Vollständiger Projektaudit

## Ziel und Grenze

Dieser Bericht bewertet den Repository-Stand vom **22. September 2026** auf Commit
`8184824d1ea2b989e11110f72482b94df468d3e2`. Geprüft wurden Produktcode,
Startweg, Sicherheitsgrenzen, GUI/CLI, Tests, Nachweiswerkzeuge, Paketierung,
CI und führende Dokumentation. Der Audit ist eine statische und automatisierte
Bestandsaufnahme, kein Penetrationstest und keine Freigabe der noch offenen
Geräte- oder Human-Prüfungen.

## Bewertung

- **Nutzen:** erwartete Wirkung auf Sicherheit, Korrektheit und Freigabefähigkeit.
- **Aufwand:** `XS` bis 2 Stunden, `S` 0,5–1 Tag, `M` 2–5 Tage,
  `L` 1–2 Wochen, `XL` mehr als 2 Wochen oder externe Abhängigkeit.
- **BESTÄTIGT:** direkt aus Code, Vertrag oder Prüflauf belegt.
- **OPEN:** in dieser Umgebung nicht objektiv abschließbar.

## Priorisierte Schwachstellen und Verbesserungen

### 1. Die Produktfreigabe hat drei offene Realprüfungen

- **Status:** OPEN · **Nutzen:** sehr hoch · **Aufwand:** M plus externe Verfügbarkeit.
- **Beleg:** `todo.txt` nennt den Zweitgeräte-Nachweis (P0) sowie die Human-Abnahmen
  für Kopieren/Verschieben und Diagnose-Datei (P1). `docs/CURRENT_ITERATION.md`
  hält dieselben Gates ausdrücklich offen.
- **Auswirkung:** Portabilität und Laienverständlichkeit sind automatisch gut
  vorbereitet, aber noch nicht am realen zweiten Gerät beziehungsweise durch
  Menschen belegt. Eine allgemeine Freigabe wäre verfrüht.
- **Verbesserung:** Die drei vorhandenen, einmaligen Nachweiswege in ihrer
  priorisierten Reihenfolge ausführen; nicht durch weitere Simulation ersetzen.
- **Akzeptanzkriterium:** redigierte, commitgebundene PASS-Evidence aus
  `./start.sh --second-device-evidence-json`, `./start.sh --i25-evidence` und
  `./start.sh --i31-evidence`.

### 2. Große Verzeichnisse können das Fenster ohne Abbruchmöglichkeit blockieren

- **Status:** BESTÄTIGT · **Nutzen:** sehr hoch · **Aufwand:** L (1–2 Wochen).
- **Beleg:** `gui_shell.py:282-285` ruft die Inventarisierung synchron aus dem
  GUI-Ereignispfad auf. `inventory.py:84-92,136-166` sammelt und sortiert ohne
  Datei-, Tiefen-, Zeit- oder Speichergrenze das vollständige Verzeichnis.
- **Auswirkung:** Bei großen, langsamen oder eingehängten Verzeichnissen friert
  die Oberfläche ein; Fortschritt und Abbruch fehlen. Das widerspricht dem
  Architekturvertrag, nach dem Preview-Laden den UI-Thread nicht blockiert.
- **Verbesserung:** Inventarisierung in einen abbrechbaren Worker verschieben,
  begrenzte Batches/Fortschritt liefern und ein fachlich sichtbares Limit mit
  sicherem OPEN-Ergebnis einführen. CLI und GUI müssen denselben Kern behalten.
- **Akzeptanzkriterium:** reproduzierbarer Großbaum-Test belegt responsive GUI,
  Abbruch, begrenzte Ressourcen und unveränderte Read-only-Garantie.

### 3. Die Diagnoseredaktion garantiert nicht, dass beliebige Pfade verschwinden

- **Status:** BESTÄTIGT · **Nutzen:** sehr hoch · **Aufwand:** M (2–5 Tage).
- **Beleg:** `diagnostics.py:18-22,44-56` erkennt Home-Pfade nur im Muster
  `/home/<name>` sowie wenige Tokenformen. `diagnostics.py:132-139` übernimmt
  freie Fehlermeldungen nach genau dieser Redaktion. Pfade unter `/root`, `/mnt`,
  Wechseldatenträgern oder sensible Dateinamen sind nicht allgemein abgedeckt.
- **Auswirkung:** Eine weitergegebene Diagnose kann lokale Pfade oder Dateinamen
  offenlegen, obwohl der Sicherheitsvertrag beide als potenziell sensibel behandelt.
- **Verbesserung:** strukturierte, erlaubnislistenbasierte Diagnosefelder und
  plattformunabhängige Pfad-/Dateinamenredaktion statt wachsender Regex-Sammlung.
- **Akzeptanzkriterium:** Regressionstests für `/root`, `/mnt`, Unicode,
  Leerzeichen, Windows-artige Pfade und Dateinamen bestehen ohne Nutzdatenleck.

### 4. Diagnose und Preflight hängen unnötig von der GUI-Einrichtung ab

- **Status:** BESTÄTIGT · **Nutzen:** hoch · **Aufwand:** M (2–5 Tage).
- **Beleg:** `start.sh:144-199` validiert oder installiert Venv und PySide6 vor
  jeder normalen Aktion; erst `start.sh:234-250` verzweigt zu Preflight,
  Diagnose oder Zweitgeräteprüfung. Die direkten Python-Wege funktionieren im
  geprüften System ohne PySide6, sind aber kein offizieller Nutzerweg.
- **Auswirkung:** Ausgerechnet bei defekter oder offline nicht einrichtbarer GUI
  sind die read-only Diagnosewege über den offiziellen Einstieg nicht verfügbar.
- **Verbesserung:** Aktionen in Core-only und GUI-abhängig klassifizieren;
  Core-only weiterhin über `start.sh`, aber vor der PySide6-Prüfung ausführen.
- **Akzeptanzkriterium:** Preflight und Diagnose funktionieren ohne `.venv` und
  ohne Netz; GUI-/Evidence-Modi bleiben Venv-first und versionsgeprüft.

### 5. Produktänderungen lösen den portablen Paketnachweis nicht zuverlässig aus

- **Status:** BESTÄTIGT · **Nutzen:** hoch · **Aufwand:** S (0,5–1 Tag).
- **Beleg:** Das Paket nimmt alle getrackten Dateien unter `src/`, `scripts/` und
  `docs/` auf (`build_portable_package.py:29-45,76-92`). Die Pfadfilter in
  `.github/workflows/portable-package.yml:4-39` enthalten aber weder `src/**`
  noch alle Runtime-Skripte/Dokumente; zudem steht der I35-Test im PR-Filter
  doppelt und fehlt im Push-Filter.
- **Auswirkung:** Ein PR kann den ausgelieferten Inhalt verändern, ohne den echten
  Paketbau und Offline-Runtime-Check anzustoßen. Das allgemeine Unit-Gate ersetzt
  diese Artefaktprüfung nicht.
- **Verbesserung:** Workflow-Trigger aus derselben Runtime-Dateimenge ableiten
  beziehungsweise konservativ `src/**`, `scripts/**` und relevante `docs/**`
  abdecken; Duplikat entfernen und Triggervertrag testen.
- **Akzeptanzkriterium:** repräsentative Änderungen jeder Paketklasse starten das
  Paketgate auf PR und `main`; reine Nicht-Runtime-Änderungen nicht.

### 6. Der Online-Installationspfad ist nur versions-, nicht hashgebunden

- **Status:** BESTÄTIGT · **Nutzen:** hoch · **Aufwand:** M (2–5 Tage).
- **Beleg:** `requirements-gui.txt` pinnt nur `PySide6==6.11.2`.
  `start.sh:182-191` prüft Hashes ausschließlich beim lokalen Wheelhouse; der
  PyPI-Fallback nutzt kein `--require-hashes`. GUI-CI installiert ebenfalls aus
  dieser einfachen Requirement-Datei.
- **Auswirkung:** Version-Pinning verhindert Versionsdrift, bindet einen
  Online-Download aber nicht an vorab akzeptierte Artefakte. Das Offline-Paket
  ist durch die vorhandene Wheel-Baseline deutlich stärker geschützt.
- **Verbesserung:** Online-Einrichtung entweder zugunsten des geprüften
  Wheelhouse vermeiden oder eine plattformgerechte Hash-Lock-Strategie einführen.
- **Akzeptanzkriterium:** manipulierte oder unbekannte Distributionsdatei wird
  vor Installation fail-closed abgelehnt; Offline-Verhalten bleibt erhalten.

### 7. Eine vorhandene ungültige `.venv` wird nicht robust ersetzt

- **Status:** BESTÄTIGT · **Nutzen:** mittel · **Aufwand:** S (0,5–1 Tag).
- **Beleg:** Bei fehlgeschlagener Validierung erstellt `start.sh:144-163`
  `.venv.tmp` und führt anschließend `mv .venv.tmp .venv` aus. Existiert `.venv`
  bereits als ungültiges Verzeichnis, verschiebt `mv` den temporären Ordner in
  dieses Verzeichnis statt es atomar zu ersetzen.
- **Auswirkung:** `--setup` kann einen typischen Reparaturfall verschlimmern und
  hinterlässt verschachtelte Reste; eine verständliche Recovery-Anweisung fehlt.
- **Verbesserung:** Bestehenden Zustand nie still löschen, sondern klar blockieren
  und einen bestätigten, reversiblen Quarantäne-/Umbenennungsweg anbieten.
- **Akzeptanzkriterium:** Tests für ungültiges Verzeichnis, Datei, Symlink,
  Abbruch und fehlgeschlagene Erstellung belegen definierten Rückweg ohne Verlust.

### 8. Die unterstützte Python-Spanne ist intern widersprüchlich

- **Status:** BESTÄTIGT · **Nutzen:** mittel · **Aufwand:** XS (bis 2 Stunden).
- **Beleg:** `start.sh:101-109` und das Paketmanifest fordern `>=3.10,<3.15`;
  `preflight.py:164` bewertet dagegen jede Version ab 3.10 ohne Obergrenze als
  geeignet.
- **Auswirkung:** Ein interner oder künftig entkoppelter Preflight kann PASS
  melden, obwohl der offizielle Starter dieselbe Laufzeit blockiert.
- **Verbesserung:** Eine gemeinsame zentrale Versionsgrenze verwenden und beide
  Randwerte testen.
- **Akzeptanzkriterium:** 3.9 und 3.15 werden konsistent blockiert, 3.10 bis 3.14
  konsistent akzeptiert.

### 9. Lint und Typprüfung sind nicht als nutzbare Qualitätsgates eingerichtet

- **Status:** BESTÄTIGT · **Nutzen:** mittel · **Aufwand:** M (2–5 Tage).
- **Beleg:** `ruff check .` meldete 17 Befunde, darunter ungenutzte Imports und
  nicht verwendete Werte. `mypy src scripts start.py` brach mit 12 Import-/Modul-
  Setupfehlern ab. Der aktuelle Repository-Workflow führt keines der Werkzeuge aus.
- **Auswirkung:** Tote Pfade und Typgrenzen werden nur zufällig durch Tests
  entdeckt; ein ad-hoc Typcheck liefert noch kein verwertbares Signal.
- **Verbesserung:** Erst minimale Konfiguration und klare Scope-Grenze festlegen,
  dann bestehende Befunde ohne Nebenrefactor bereinigen und Gates aufnehmen.
- **Akzeptanzkriterium:** Beide Befehle laufen lokal und in CI reproduzierbar;
  Ausnahmen sind eng begründet, nicht pauschal unterdrückt.

### 10. Mehrere Kernfunktionen liegen deutlich über der Kohäsionsschwelle

- **Status:** BESTÄTIGT · **Nutzen:** mittel · **Aufwand:** L (1–2 Wochen).
- **Beleg:** AST-Auswertung fand unter anderem `create_main_window` mit 341,
  `write_diagnostic_export` mit 145 und `execute` mit 134 Funktionszeilen.
  Die Evidence-Skripte I17/I25 wiederholen Browser-, HTTP-, Bericht- und
  Human-Gate-Strukturen; `i25_auto_evidence.py` umfasst 599 Zeilen.
- **Auswirkung:** Änderungen koppeln Darstellung, Ablauf und Prüfaufbau; Reviews
  und gezielte Tests werden schwerer. Die hohe Testzahl reduziert, beseitigt aber
  nicht die Änderungsfläche.
- **Verbesserung:** Nur entlang realer Verantwortungsgrenzen teilen: zuerst
  gemeinsame Evidence-Infrastruktur mit mindestens zwei Nutzern, danach GUI-
  Dialogbau und Ablaufsteuerung. Kein Zerlegen allein wegen Zeilenzahl.
- **Akzeptanzkriterium:** kleinere unabhängig testbare Verantwortungen, keine
  zusätzliche Fachlogik in Adaptern und unveränderte GUI/CLI-Parität.

### 11. Der Informationsdateien-Registerstand ist sichtbar veraltet

- **Status:** BESTÄTIGT · **Nutzen:** niedrig · **Aufwand:** XS (bis 2 Stunden).
- **Beleg:** `docs/DATEIENREGISTER.md:23` kennzeichnet
  `docs/CURRENT_ITERATION.md` noch als „🟢 I36“, während die Datei I39 führt.
  Das grüne Repository-Gate erkennt diesen semantischen Drift nicht.
- **Auswirkung:** Das Register schwächt seine eigene Funktion als verlässlicher
  Wegweiser und zeigt eine Lücke zwischen Existenzprüfung und Inhaltsprüfung.
- **Verbesserung:** Status berichtigen und den Gate-Vertrag entweder auf einen
  dynamischen Verweis umstellen oder den flüchtigen Iterationsnamen entfernen.
- **Akzeptanzkriterium:** Register und CURRENT_ITERATION widersprechen sich nicht;
  ein gezielter Test verhindert denselben Drift.

## Belegte Stärken

- 257 Unit-/Integrationstests liefen in 0,825 Sekunden vollständig grün.
- Repository-, Plugin-, Read-only-, Syntax- und Core-Diagnose-Gates bestanden.
- Schreibende Produktpfade sind standardmäßig gesperrt; der Diagnose-Writer ist
  separat autorisiert, create-only und gegen Parallelzugriff getestet.
- Actions sind auf unveränderliche Commits gepinnt, Berechtigungen minimal und
  Jobs zeitlich begrenzt.
- Symlinks, Traversal, Überschreiben, Unicode, Abbruch, Rechtefehler, ENOSPC und
  parallele Writer sind in den relevanten Kernbereichen regressionsgeprüft.

## Prüfstand und Grenzen

| Prüfung | Ergebnis |
| --- | --- |
| `python3 scripts/repo_quality.py` | PASS, Exit 0 |
| `python3 scripts/plugin_boundary_guard.py` | PASS, Exit 0 |
| `python3 scripts/read_only_guard.py` | PASS, Exit 0 |
| `PYTHONPATH=src python3 -m unittest discover -s tests -v` | PASS, 257 Tests, Exit 0 |
| `python3 -m compileall -q src scripts start.py tests` | PASS, Exit 0 |
| `python3 scripts/core_diagnostics.py` | PASS, Exit 0 |
| `python3 scripts/diagnostic_snapshot.py --json` | PASS, Exit 0 |
| `ruff check .` | FAIL, 17 Befunde, Exit 1 |
| `mypy src scripts start.py` | OPEN, 12 Setup-/Importfehler, Exit 2 |
| echte GUI bei 100/150/200 %, Zweitgerät und Human-Gates | OPEN |

Die Umgebung war Ubuntu 24.04.4, Linux x86_64, Python 3.12.13, ohne grafische
Sitzung und ohne PySide6. Es wurden keine Abhängigkeiten installiert, keine
Nutzerdaten verändert und keine offenen Realprüfungen als bestanden gewertet.

## Abschluss

- **Ziel:** erreicht; die belegten Schwächen sind nach Nutzen und Aufwand geordnet.
- **Geändert:** nur dieser Bericht und sein Indexeintrag.
- **Nicht geändert:** Produktcode, Tests, Workflows, Freigaben und Abhängigkeiten.
- **Neue Risiken:** keine Laufzeitrisiken; der Bericht ist eine Momentaufnahme.
- **Status:** 🟨 ANALYSE ABGESCHLOSSEN, Produktfreigaben weiter offen.
- **Empfohlener nächster Schritt:** Befund 1 schließen: den realen P0-
  Zweitgeräte-Nachweis auf einem zweiten Ubuntu-/Kubuntu-Gerät ausführen.

### Drei-Schritte-Vorausplanung

1. **Zweitgerät:** reales Gerät erforderlich; Scope Evidence/Status; Gate
   `./start.sh --second-device-evidence-json`.
2. **Kopieren/Verschieben:** Desktop und P0-Reihenfolge erforderlich; Scope
   I25-Evidence; Gate `./start.sh --i25-evidence`.
3. **Diagnose-Datei:** Desktop und vorangehende Freigaben erforderlich; Scope
   I31-Evidence; Gate `./start.sh --i31-evidence`.
