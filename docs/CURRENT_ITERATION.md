# PROVOWARE – Current Iteration

## I17-B – Geführter realer GUI-/Accessibility-Zielsystemlauf

**Status:** 🟨 EVIDENCE-ASSISTENT IMPLEMENTIERT – REALER ZIELSYSTEMLAUF OFFEN
**Fortschritt:** `██████░░░░ 60 %`

**Basis:** `b1a7bbd47c74316fc391177bea112fc836e73caf`

## A – FESTER PLAN

**Ziel:** Den bereits definierten realen I17-Zielsystemlauf so führen, dass ein Laie ihn mit einem Befehl reproduzierbar durchführen kann, ohne dass CI oder das Skript einen visuellen PASS vortäuscht.

### Umgesetzter Block

- geführter `--guided`-Modus;
- echte Runtime-/Display-Vorprüfung;
- synthetische Preview-Fixtures für leer sowie Unicode/Leerzeichen;
- GUI-Start ohne Produkt-Schreibpfad;
- manuelle PASS/FAIL/OPEN/ABORT-Gates;
- maximal drei ungültige Eingabeversuche je Gate;
- fünf feste Screenshot-Namen;
- lokale TXT-/JSON-Evidence ohne Überschreiben alter Läufe;
- Abschlussstatus nur bei vollständiger Evidence PASS;
- automatische Desktop-Öffnung von Evidence-Ordner/Auswertung soweit verfügbar.

## B – VARIABLE FOLGEAUFGABE

**Quelle:** unmittelbar vorheriger Wartungsblock zu Anti-Endlosschleifen.

**Befund:** Interaktive Evidence darf selbst keine unendliche Eingabeschleife erzeugen.

**Maßnahme:** Jede Gate-Eingabe ist auf drei ungültige Versuche begrenzt. Danach bleibt das Gate `OPEN`. Es gibt keinen automatischen Retry des GUI-Laufs.

## Sicherheitsgrenze

Kein:

- Produkt-Executor;
- Copy/Move/Trash;
- Installation;
- Netzwerkpfad;
- Rechteausweitung;
- automatisches visuelles PASS;
- Überschreiben eines früheren Evidence-Laufs.

Der Helper erzeugt nur einen neuen lokalen Evidence-Ordner und synthetische Testdateien.

## Exit-Gates

1. targeted Tests für I17-Evidence PASS.
2. Repository-Contract PASS.
3. Read-only-Lock PASS.
4. vollständige Suite PASS.
5. PR-Pflichtcheck `repository-contract` PASS.
6. realer Zielsystemlauf auf echter PySide6-/Desktop-Session.
7. fünf Screenshots vorhanden und manuell auf Datenschutz geprüft.
8. erst danach I17-B vollständig PASS.

## Nächste drei vorgeplante Schritte

### 1. 🔵 Realer I17-B-Zielsystemlauf
Ein Befehl: `python3 scripts/i17_target_evidence.py --guided`.

### 2. 🔒 I25 – Adapter-Implementierung
Erst nach grünem realem I17-Befund.

### 3. 🔵 I27 – Writer-spezifischer Guard Decision/Prototype
Unabhängig planbar, aber kein produktiver Writer ohne eigenen Guard-/No-clobber-Nachweis.
