# PROVOWARE – Aktueller Arbeitsblock

## I47 – Python-Laufzeitgrenzen konsistent und sicher prüfen

**Stand:** 24.10.2026. **Basis:** `main` bei `996fc55b797b3d3be3a488cdb25744d1506a8da5`.
**Entwicklungszweig:** `fix/i47-python-runtime-contract-20261024`.
**PR:** [#69](https://github.com/provoware/PROVOWARE-LAIENTOOL/pull/69) (Entwurf).
**Code-Commit:** `a717cebdfc438d1acadffd47a74977e16303a1eb`.
**CI-Nachweis:** die Prüfungen des jeweils aktuellen PR-Heads unter PR #69; keine Freigabe allein durch einen älteren grünen Lauf.

### Ziel, Scope und Sicherheitsgrenze

Der lesende Preflight hatte Python 3.15 und neuer als geeignet eingestuft,
obwohl der offizielle Starter und das Paketmanifest nur 3.10 bis 3.14
akzeptieren. I47 korrigiert diese widersprüchliche Eignung. Betroffen:
`src/provoware_laientool/preflight.py`, `tests/test_preflight.py`,
`tests/test_venv_bootstrap_contract.py`, diese Statusseite, die
Regressionsmatrix und `todo.txt`. **Nicht-Ziele:** Installation,
Abhängigkeitswechsel, Datei-Migration, Freigabe von Schreibaktionen,
zweites Gerät, Human-Abnahme oder Veröffentlichung.

Der Preflight prüft jetzt die **gemeldete** Python-Version statt der
zufälligen Testlaufzeit. 3.9 und 3.15+ werden abgewiesen, 3.10 bis 3.14
akzeptiert. Nicht auswertbare Versionsangaben werden sicher abgewiesen.
Ein Vertragstest bindet die Preflight-Grenzen an die vorhandenen Angaben
in `start.sh` und im Paketmanifest; der Starter selbst bleibt unverändert.

### Tatsächliche Prüfung und Fehlerkorrektur

- **PASS:** Der erste PR-Lauf [repo-quality #40064306534](https://github.com/provoware/PROVOWARE-LAIENTOOL/actions/runs/40064306534)
  bestand Repository-, Sicherheits-, vollständige Unit-/Integrationstests,
  Kern-Diagnostik und Preflight.
- **FAIL (erkannt):** Derselbe Lauf stoppte ausschließlich am
  `info_text_guard`, weil die verpflichtende Änderung an `todo.txt`
  beziehungsweise README/Evidence noch fehlte. Dies wird mit diesem
  Dokumentationsbatch behoben, nicht durch Abschwächung des Gates.
- **Noch offen:** Der vollständige unabhängige GitHub-Prüflauf auf dem
  abschließenden PR-Head ist maßgeblich; den aktuellen Status unter PR #69
  prüfen. Der Paketlauf ist ein eigenständiger Nachweis.

### Release-Pflichtmatrix – aktueller Nachweisstand

| Pflichtbereich | Status | Beleg / Rest |
| --- | --- | --- |
| Fachfunktionen und Grenzfälle | OPEN | Lesewege und Vorschau vorhanden; schreibende Use-Cases gesperrt |
| Datensicherheit und Wiederherstellung | OPEN | Read-only-Lock geprüft; Recovery ungültiger `.venv` offen |
| Fehlerbehandlung und Sicherheit | OPEN | I47 weist falsche Python-Version ab; Abhängigkeitshashes und Venv-Recovery offen |
| Design, UX und Lesbarkeit | OPEN | Technische Evidence; reale Gesamtsichtprüfung fehlt |
| 800×600 und hohe Skalierung | OPEN | 100/150/200 % technisch erfasst; 800×600 vollständig offen |
| Tastatur und Barrierefreiheit | OPEN | I25/I31 automatisch geprüft; echte Bedienprüfung erst zum Abschluss |
| Performance und Abbruch | OPEN | Inventarisierung ohne begrenzten Abbruchpfad |
| Wartbarkeit und Wiederverwendung | OPEN | Gemeinsamer Kern; Kohäsions-/Qualitätsbefunde offen |
| Installation und Paketierung | OPEN | Starter-/Manifest-Vertrag mit I47-Test; Zweitgerät und Online-Hashbindung offen |
| Automatisierte Funktionstests | PASS (I47-Code) | Grenzwerte und injizierte Plattformdaten im vollständigen PR-Testlauf bestanden |
| Integration | OPEN | GUI-/CLI-Parität vorhanden, vollständige Freigabe ausstehend |
| GUI/Browser | OPEN | I25/I31 automatisiert; reale Wahrnehmungsprüfung ausstehend |
| Regression | PASS (I47-Code) | Neue Grenzwert- und Konsistenzprüfungen auf Code-Commit erfolgreich |
| CI und Qualitätsgates | OPEN | Erstlauf Info-Text-Impact FAIL; finaler PR-Head muss vollständig grün sein |
| Dokumentation | OPEN | Matrix/TODO im Nachtragsbatch aktualisiert; Release-Dokumentation offen |
| Release-Freeze | BLOCKED | Drei reale Freigaben, vollständige Fachfunktion und Kubuntu-Endabnahme fehlen |

### Rückweg und nächste Pflichtarbeit

Änderung ausschließlich auf Entwicklungszweig; bei Regression PR nicht
integrieren und den Branch gezielt zurücknehmen. Nach grünen Pflichtgates
nächster unabhängiger Block: `.venv`-Recovery verlustfrei und ohne
stille Rechteausweitung absichern. Die einzige gebündelte persönliche
Endabnahme erfolgt erst am vollständig geprüften Release-Kandidaten.

---

## I46 – Paket-CI deckt verpackte Quelldateien ab

**Stand:** 23.10.2026. **Basis:** `main` bei `6845d6c09ab68e8ad830caaf89afb0392bcb0153`.
**Entwicklungszweig:** `fix/portable-package-trigger-coverage-20261023`.
**PR:** [#67](https://github.com/provoware/PROVOWARE-LAIENTOOL/pull/67), nach grünen Gates per Squash integriert.
**Geprüfter PR-Head:** `0baee39ac1a3f9bafbdd8a1331730fc83a4e2c4f`.
**Merge-Commit auf `main`:** `64f83a3a2f3f270f3d4a713ab319366212e954b9`.
**CI:** `PASS` für `repo-quality` und `portable-package` auf PR-Head und erneut nach Merge auf `main`.
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
| Installation / Paketierung | OPEN | Trigger-Abdeckung und Paketbau nach Merge PASS; reale Zweitgeräteprüfung weiterhin offen |
| Automatisierte Funktionstests | PASS (Basis) | `repo-quality` auf `6845d6c09ab68e8ad830caaf89afb0392bcb0153` erfolgreich; neuer Branch noch zu prüfen |
| Integration | OPEN | GUI/CLI und Export-Adapter automatisch geprüft; vollständige Freigabe fehlt |
| GUI / Browser | OPEN | I25/I31 technisch geprüft; menschliche Endprüfung fehlt |
| Regression | PASS (I46) | Drei neue Paket-Filter-Vertragstests bestanden; übrige Release-Regressionen separat OPEN |
| CI / Qualitätsgates | PASS (I46) | Beide PR-Gates und beide Post-Merge-Gates erfolgreich; andere Release-Gates unverändert OPEN |
| Dokumentation | OPEN | Aktuelle Matrix und TODO nachgeführt; vollständige Release-Dokumentation offen |
| Release / Freeze | BLOCKED | Zweitgerät, gesperrte Aktionen und gebündelte Kubuntu-Endabnahme offen |

Die historische I45-Evidence bleibt unter
`docs/evidence/EV-20261001-017-i45-i25-auto-pass.md` erhalten;
sie ersetzt keinen menschlichen Test. `main`-Prüfungen des Basis-Commits
sind kein Nachweis für den neuen Entwicklungszweig.


### Abgeschlossene I46-Nachweise

- PR [#67](https://github.com/provoware/PROVOWARE-LAIENTOOL/pull/67),
  geprüfter Head `0baee39ac1a3f9bafbdd8a1331730fc83a4e2c4f`.
- PR: [Repository-Contract](https://github.com/provoware/PROVOWARE-LAIENTOOL/actions/runs/39999103246)
  **PASS**, 268 Python-Tests; [Offline-Paket](https://github.com/provoware/PROVOWARE-LAIENTOOL/actions/runs/39999103230)
  **PASS**.
- Post-Merge auf `main`: [Repository-Contract](https://github.com/provoware/PROVOWARE-LAIENTOOL/actions/runs/39999330683)
  **PASS**; [Offline-Paket](https://github.com/provoware/PROVOWARE-LAIENTOOL/actions/runs/39999330920)
  **PASS**.
- Keine Produktfreigabe, keine Veröffentlichung. Die persönlichen und
  physischen Release-Nachweise bleiben ausdrücklich `OPEN`.

### Gates und Rückweg

1. **PASS – TARGETED:** `PYTHONPATH=src python3 -m unittest tests.test_i32_portable_package -v`
   (bei fehlendem Paketimport alternativ `unittest discover -s tests -p test_i32_portable_package.py`).
2. **PASS – FULL:** `python3 scripts/repo_quality.py`,
   `python3 scripts/read_only_guard.py` und gesamte `unittest discover`-Suite.
3. **PASS – REMOTE:** `repo-quality` und `portable-package` auf dem exakten PR-Head
   vollständig grün; Fehler nicht durch Abschwächung des Gates beheben.
4. **PASS – DIFF:** ausschließlich Trigger, Vertragstest und Statusdateien.
5. **RÜCKWEG:** I46 ist nach grünen Gates auf `main` integriert; bei einer nachgewiesenen Regression nur durch neuen geprüften PR zurücknehmen.

### Nächste drei Arbeitsschritte

1. P1-Inventarisierung: optionales Begrenzungs-/Abbruchmodell ohne willkürliche Defaultgrenze spezifizieren und mit Großbaumtests absichern.
2. P2-Recovery ungültiger `.venv` verlustfrei absichern und gezielt testen.
3. P2-Python-Versionsgrenzen im Starter und Preflight vereinheitlichen und Randwerte testen.

Die persönliche Endabnahme wird erst vor einer explizit freigegebenen
Veröffentlichung des vollständig geprüften Release-Kandidaten verlangt.
