# PROVOWARE – Aktueller Arbeitsblock

## I46 – Paket-CI deckt verpackte Quelldateien ab

**Stand:** 23.10.2026. **Basis:** `main` bei `6845d6c09ab68e8ad830caaf89afb0392bcb0153`.
**Entwicklungszweig:** `fix/portable-package-trigger-coverage-20261023`.
**PR/CI:** nach dem ersten GitHub-Push zu prüfen; bis dahin `OPEN`.
**Produktfreigabe:** unverändert `OPEN`; keine Schreibfunktion freigeschaltet.

### Ziel und Umfang

P1-Paketlücke aus `todo.txt` beheben: Änderungen an tatsächlich verpackten
Laufzeitdateien müssen den vollständigen Offline-Paketbau auf Pull Requests
und `main` auslösen. Die Regeln des Paketbauers
(`scripts/build_portable_package.py`: `RUNTIME_TOP_LEVEL`,
`RUNTIME_PREFIXES`) sind die maßgebliche Grundlage.

**Dateibesitz:** Workflow = CI-Konfiguration; Pakettests = Regression;
`todo.txt` und diese Datei = Status. **Nicht-Ziele:** keine neuen
Dateischreibfunktionen, keine Freigabe gesperrter Use-Cases, keine Migration,
kein Paket-Upload und keine Änderung der Abhängigkeiten.

**Umsetzung:** identische Filter für `pull_request` und `push/main`;
`src/**`, `scripts/**`, `docs/**` sowie `README.md` ergänzt.
`docs/evidence/**` löst konservativ ebenfalls einen Paketlauf aus,
obwohl es nicht im ZIP liegt. Die doppelte Nennung des Provenance-Tests
entfällt. Ein Vertragstest prüft beide Filter auf Gleichheit, Duplikate,
alle derzeit verpackten Dateien sowie neu hinzukommende Dateien.
Der Paketbauer und sein Sicherheitsvertrag bleiben unverändert.

### Release-Pflichtmatrix (nur belegter Stand)

| Bereich | Stand | Nachweis / verbleibende Pflicht |
| --- | --- | --- |
| Fachfunktionen und Grenzfälle | OPEN | Lesender Kern und Vorschauen getestet; schreibende Aktionen bewusst gesperrt |
| Datensicherheit / Wiederherstellung | OPEN | Read-only-Schutz vorhanden; echte Wiederherstellung nach Schreibaktionen nicht freigegeben |
| Fehlerbehandlung / Sicherheit | OPEN | Core-Sicherheitsprüfungen vorhanden; Recovery ungültiger `.venv` offen |
| Design / UX / Lesbarkeit | OPEN | Technische GUI-Evidence vorhanden; persönliche Gesamtsichtprüfung fehlt |
| 800×600 und hohe Skalierung | OPEN | 100/150/200-%-Prüfungen dokumentiert; 800×600 vollständig nachzuweisen |
| Tastatur / Barrierefreiheit | OPEN | Automatische I25/I31-Evidence vorhanden; reale Bedienprüfung fehlt |
| Performance / Abbruch | OPEN | Unbegrenzte synchrone Inventarisierung ist P1 |
| Wartbarkeit / Wiederverwendung | OPEN | Gemeinsamer Core vorhanden; Qualitäts- und Kohäsionsbefunde offen |
| Installation / Paketierung | OPEN | Paketbau auf Basis-Commit grün; neue Trigger-Abdeckung und Zweitgerät offen |
| Automatisierte Funktionstests | PASS (Basis) | `repo-quality` auf `6845d6c09ab68e8ad830caaf89afb0392bcb0153` erfolgreich; neuer Branch noch zu prüfen |
| Integration | OPEN | GUI/CLI und Export-Adapter automatisch geprüft; vollständige Freigabe fehlt |
| GUI / Browser | OPEN | I25/I31 technisch geprüft; menschliche Endprüfung fehlt |
| Regression | OPEN | Neuer Filter-Vertragstest hinzugefügt; Ausführung und CI-Nachweis noch offen |
| CI / Qualitätsgates | OPEN | Basis-CI grün; PR-Gates `repo-quality` und `portable-package` ausstehend |
| Dokumentation | OPEN | Aktuelle Matrix und TODO nachgeführt; vollständige Release-Dokumentation offen |
| Release / Freeze | BLOCKED | Zweitgerät, gesperrte Aktionen und gebündelte Kubuntu-Endabnahme offen |

Die historische I45-Evidence bleibt unter
`docs/evidence/EV-20261001-017-i45-i25-auto-pass.md` erhalten;
sie ersetzt keinen menschlichen Test. `main`-Prüfungen des Basis-Commits
sind kein Nachweis für den neuen Entwicklungszweig.

### Gates und Rückweg

1. **TARGETED:** `PYTHONPATH=src python3 -m unittest tests.test_i32_portable_package -v`
   (bei fehlendem Paketimport alternativ `unittest discover -s tests -p test_i32_portable_package.py`).
2. **FULL:** `python3 scripts/repo_quality.py`,
   `python3 scripts/read_only_guard.py` und gesamte `unittest discover`-Suite.
3. **REMOTE:** `repo-quality` und `portable-package` auf dem exakten PR-Head
   vollständig grün; Fehler nicht durch Abschwächung des Gates beheben.
4. **DIFF:** ausschließlich Trigger, Vertragstest und Statusdateien.
5. **RÜCKWEG:** PR offen lassen oder schließen; `main` unverändert.

### Nächste drei Arbeitsschritte

1. Paket- und Qualitäts-PR-Gates auswerten, Fehler reparieren und erneut prüfen.
2. P1-Inventarisierung mit expliziter, optionaler Begrenzung und Abbruchmodell
   vorbereiten, ohne willkürlichen Standardwert zu behaupten.
3. P2-Recovery ungültiger `.venv` verlustfrei absichern und gezielt testen.

Die persönliche Endabnahme wird erst vor einer explizit freigegebenen
Veröffentlichung des vollständig geprüften Release-Kandidaten verlangt.
