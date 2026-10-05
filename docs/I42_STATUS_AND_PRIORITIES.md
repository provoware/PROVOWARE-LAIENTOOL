# I42 – Stand, Schwachstellen und wirksamste nächste Schritte

## Auftrag und Prüfbasis

Diese Bestandsaufnahme beantwortet den Auftrag vom **5. Oktober 2026** für
Commit `e98b94e4fc67c874ec941b2c8221bce9b2f0d75a`. Berücksichtigt wurden der in
diesem Auftrag sichtbare Chat, der aktuelle Git-Stand, die führenden
Informationsdateien, der historische I40-Audit sowie gezielt die dort genannten
Code-, Start-, Test- und CI-Pfade. Frühere, hier nicht sichtbare Chats wurden
nicht unterstellt; Git-Historie und Evidence bleiben dafür die belastbare Spur.

**Kurzurteil:** Der Sicherheitskern ist umfangreich automatisch geprüft und
schreibende Produktwege bleiben gesperrt. Für eine allgemeine Freigabe fehlen
weiterhin drei Realprüfungen. Der größte technische Produkthebel ist danach die
begrenzte, abbrechbare Inventarisierung außerhalb des GUI-Threads. I40-Befund 3
(Pfadredaktion) wurde in I41 behoben; die übrigen nachstehenden Punkte sind
`OPEN`, sofern kein anderer Status genannt ist.

## 10 nächste logische Schritte

1. **Kopieren/Verschieben durch einen Menschen abnehmen (P1).** Nach
   ausdrücklicher Freigabe `./start.sh --i25-evidence` einmal ausführen; nur so
   wird aus automatischer Absicherung ein belegter, laienverständlicher Ablauf.
2. **Diagnose-Datei durch einen Menschen abnehmen (P1).** Danach
   `./start.sh --i31-evidence` einmal ausführen; die sensible Schreibfunktion
   bleibt bis zur verständlichen Gesamtprüfung zu Recht gesperrt.
3. **Zweitgeräteprüfung neu freigeben oder bewusst offen lassen (P0).** Der
   übersprungene Test darf nicht simuliert werden; reale Portabilität braucht
   ein zweites Ubuntu-/Kubuntu-Gerät und commitgebundene Evidence.
4. **Eine verständliche Inventargrenze entscheiden.** Datei-/Zeit-/Speicherlimit
   und sichtbares OPEN-Ergebnis fachlich festlegen, bevor technische Grenzwerte
   implementiert werden; das verhindert willkürliche Abbrüche.
5. **Inventarisierung abbrechbar und asynchron machen.** Gemeinsamer Core,
   Batch-Fortschritt und sicherer Abbruch müssen die GUI reaktionsfähig halten,
   ohne einen zweiten Fachpfad zu schaffen.
6. **Core-Diagnose vor GUI-Einrichtung erreichbar machen.** `--preflight` und
   die read-only Diagnosemodi in `start.sh` vor PySide6/Venv-Prüfungen
   verzweigen; gerade bei defekter GUI muss Diagnose funktionieren.
7. **Paket-CI an den tatsächlichen Paketinhalt koppeln.** Änderungen unter
   `src/**`, relevanten `scripts/**` und Paketdokumenten müssen den echten
   Paketbau auf Pull Request und `main` auslösen.
8. **Defekte `.venv` reversibel behandeln.** Statt eines mehrdeutigen `mv` eine
   klare Blockade plus bestätigten Quarantäne-/Rückweg entwerfen und gegen
   Verzeichnis, Datei und Symlink prüfen.
9. **Python-Grenzen zentral konsistent machen.** 3.10–3.14 überall akzeptieren,
   3.9 und 3.15 überall ablehnen; Starter, Preflight und Paketmanifest dürfen
   nicht verschieden urteilen.
10. **Erst danach Qualitäts- und Wartbarkeitsschulden bündeln.** Ruff/Mypy
    nutzbar konfigurieren und nur reale Verantwortungsgrenzen in großen
    GUI-/Evidence-Funktionen trennen; das senkt Folgerisiko ohne Nebenrefactor.

## 10 wichtigste Schwachstellen

1. **Drei Freigabegates sind OPEN – sehr hohe Wirkung.** Zweitgerät sowie zwei
   Human-Abnahmen fehlen; automatische Tests ersetzen weder reales Zielgerät
   noch Laienverständlichkeit.
2. **Unbegrenzte synchrone Inventarisierung – sehr hohe Wirkung.** Große oder
   langsame Bäume können GUI, Laufzeit und Speicher belasten; Fortschritt und
   Abbruch fehlen.
3. **Read-only Diagnose hängt am GUI-Bootstrap – hohe Wirkung.** Der offizielle
   Startpfad prüft Venv/PySide6 vor Core-Aktionen und kann Hilfe ausgerechnet im
   Fehlerfall verhindern.
4. **Paketworkflow hat Triggerlücken – hohe Wirkung.** Paketinhalt kann sich
   ändern, ohne dass der artefaktspezifische Offline-Test sicher startet.
5. **Online-Installation ist nicht hashgebunden – hohe Wirkung.** Exakte Version
   ist schwächer als die vorhandene Wheelhouse-Prüfung und schützt nicht gegen
   ein unbekanntes Distributionsartefakt.
6. **Recovery einer ungültigen `.venv` ist mehrdeutig – mittlere Wirkung.** Das
   aktuelle Verschieben kann einen temporären Ordner in einen defekten Zielordner
   verschachteln; ein verlustfreier Nutzerweg fehlt.
7. **Python-Kompatibilitätsaussagen widersprechen sich – mittlere Wirkung.** Der
   Starter hat eine Obergrenze, der interne Preflight bislang nicht.
8. **Lint und Typprüfung liefern kein stabiles Gate – mittlere Wirkung.** I40
   dokumentiert Ruff-Befunde und ein nicht lauffähig eingerichtetes Mypy; dadurch
   bleiben tote Pfade und Typgrenzen außerhalb der CI-Sicht.
9. **Große Funktionen und doppelte Evidence-Abläufe – mittlere Wirkung.** GUI,
   Ablaufsteuerung, Browser/HTTP und Berichtserstellung sind schwerer isoliert zu
   ändern; Teilung ist aber nur an echten Verantwortungsgrenzen sinnvoll.
10. **Statuspflege war driftanfällig – niedrige direkte, hohe
    Vertrauenswirkung.** Das Informationsregister nannte noch I36 und eine
    falsche TODO-Anzahl; flüchtige Namen/Zählwerte sind daher ungeeignet.

## 10 maximal wirksame Verbesserungen

1. **Freigabematrix statt Fertig-Annahme.** Die drei Realgates einzeln mit
   `OPEN/PASS`, Commit, Umgebung und Evidence führen; dadurch bleibt der
   tatsächliche Produktstatus unmissverständlich.
2. **Budgetierte Inventarisierungs-API.** Gemeinsame Limits, Abbruchsignal,
   Teilfortschritt und definiertes unvollständiges Ergebnis im Core schaffen;
   das adressiert Reaktionszeit, Speicher und GUI/CLI-Parität zugleich.
3. **Worker nur als Adapter.** GUI lädt Inventar/Preview außerhalb des
   Ereignis-Threads, während Sicherheitsentscheidungen im Core bleiben; damit
   steigt Responsivität ohne Architekturduplikat.
4. **Startmodi nach Fähigkeiten staffeln.** Core-only Befehle ohne Qt-Vorbedingung,
   GUI-/Evidence-Modi weiter Venv-first und fail-fast; das verbessert Recovery
   und Offline-Diagnose ohne neuen Einstiegspunkt.
5. **Paket-Trigger konservativ vervollständigen und testen.** Runtime-Klassen
   symmetrisch für Pull Request und `main` abdecken und Duplikate entfernen;
   damit prüft CI tatsächlich das auszuliefernde Artefakt.
6. **Supply-Chain-Pfade angleichen.** Bevorzugt geprüftes Wheelhouse nutzen oder
   Online-Artefakte mit plattformgerechten Hashes binden; unbekannte Dateien
   müssen vor Installation fail-closed enden.
7. **Reversible Venv-Quarantäne.** Defekten Zustand erklären, nach Bestätigung
   eindeutig umbenennen und bei Fehler zurückrollen; das erfüllt Daten- und
   Recovery-Priorität besser als stilles Ersetzen.
8. **Eine Quelle für Laufzeitgrenzen.** Gemeinsame Konstante/Vertragsprüfung für
   Starter, Preflight und Manifest plus Randwerttests; das beseitigt Statusdrift
   mit kleinem Änderungsradius.
9. **Targeted-first Qualitätsbaseline.** Ruff zunächst auf echte Fehlerklassen,
   Mypy auf importierbaren Kernscope begrenzen und erst nach bereinigter
   Baseline in CI aufnehmen; Gates dürfen nicht durch pauschale Ausnahmen grün
   werden.
10. **Driftarme Informationsführung.** Dauerhafte Fakten nur einmal führen,
    flüchtige Iterationsnamen und Eintragszahlen vermeiden und Index/Links durch
    `repo_quality.py` prüfen; das reduziert Pflegeaufwand bei höherer Verlässlichkeit.

## Abgrenzung und Status

- **BESTÄTIGT erledigt:** I41 redigiert absolute POSIX-, Windows- und UNC-Pfade;
  dieser frühere I40-Befund ist kein offener Arbeitsstrang mehr.
- **Nicht geändert:** Produktcode, Tests, Workflows, Abhängigkeiten,
  Sicherheitsfreigaben und historische Evidence.
- **Neue Risiken:** keine Laufzeitänderung; die Rangfolge ist eine Analyse auf
  dem genannten Commit und muss nach fachlichen Änderungen neu bewertet werden.
- **Status:** 🟨 **ANALYSE ABGESCHLOSSEN, PRODUKTFREIGABEN OFFEN**.

### Genau ein empfohlener nächster Schritt

Nach ausdrücklicher Nutzerfreigabe die Human-Abnahme für Kopieren/Verschieben
mit `./start.sh --i25-evidence` durchführen; ohne diese Freigabe den Stand
einfrieren.

### Drei-Schritte-Vorausplanung

1. **Kopieren/Verschieben:** braucht Freigabe und grafische Sitzung; Scope
   I25-Evidence/Status; Gate `./start.sh --i25-evidence`.
2. **Diagnose-Datei:** braucht Freigabe und grafische Sitzung; Scope
   I31-Evidence/Status; Gate `./start.sh --i31-evidence`.
3. **Inventarisierung:** braucht eine fachliche Defaultgrenze; Scope Core,
   Adapter und direkte Tests; Gate Großbaum-, Abbruch- und Responsiveness-Test.
