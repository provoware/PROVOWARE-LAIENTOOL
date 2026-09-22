# PROVOWARE – Aktueller Arbeitsblock

## I41 – Diagnosepfadredaktion

**Status:** 🟢 ABGESCHLOSSEN
**Fortschritt:** `██████████ 100 %`
**Produktfreigabe:** unverändert; Zweitgeräte- und Human-Gates bleiben offen

## Ziel

Absolute POSIX-, Windows-Laufwerks- und UNC-Pfade in frei übernommenen
Diagnosetexten so redigieren, dass lokale Pfade und Dateinamen nicht
weitergegeben werden.

## Ergebnis

- absolute POSIX-, Windows-Laufwerks- und UNC-Pfade werden durch `<PATH>`
  ersetzt;
- Unicode, Leerzeichen und gültige Trennzeichen innerhalb eines Pfades sind
  regressionsgetestet;
- Satzzeichen nach einem Pfad, bereits redigierte Home-Pfade und Webadressen
  bleiben erhalten;
- ein blockierter Diagnoseexport gibt weder Inhalt noch Schreibplan zurück;
- 260 Tests und die betroffenen Repository-Guards sind auf dem Release
  Candidate erfolgreich durchgelaufen;
- es wurden keine Schreibrechte, Startwege oder Produktfreigaben verändert.

## Bewusster Trade-off

Die sicherheitsorientierte Erkennung kann in freiem Diagnosetext auch eine
unproblematische Zeichenfolge redigieren, wenn sie wie ein absoluter Pfad
aussieht. Diese mögliche Überredaktion ist akzeptiert: Ein weniger ausführlicher
Diagnosetext ist sicherer als die unbeabsichtigte Weitergabe lokaler Namen.

## Offene Freigaben und Abgrenzung

- Die Zweitgeräteprüfung wurde auf Nutzerentscheidung übersprungen. Sie gilt
  ausdrücklich **nicht** als bestanden und wird nur nach neuer Freigabe wieder
  aufgenommen.
- Die Human-Abnahmen für Kopieren/Verschieben und für die Diagnose-Datei bleiben
  offen.
- Ein Inventarlimit wurde nicht eingeführt, weil keine fachlich freigegebene
  Defaultgrenze vorliegt. Der Befund bleibt nachvollziehbar in `todo.txt`
  vertagt.
- Der historische I40-Audit bleibt als damalige Bestandsaufnahme unverändert.

## Nächster verbindlicher Schritt

**P1 – Human-Abnahme für Kopieren und Verschieben**

Nach ausdrücklicher Freigabe einmal den vorhandenen Bediennachweis über
`./start.sh --i25-evidence` ausführen. Bis dahin bleiben die Funktionen im
normalen Programmweg gesperrt.

### Drei-Schritte-Vorausplanung

1. **Kopieren/Verschieben:** ausdrückliche Human-Freigabe erforderlich; Scope
   I25-Evidence; Gate `./start.sh --i25-evidence`.
2. **Diagnose-Datei:** ausdrückliche Human-Freigabe erforderlich; Scope
   I31-Evidence; Gate `./start.sh --i31-evidence`.
3. **Inventarlimit:** fachlich freigegebene Defaultgrenze erforderlich; Scope
   Inventarisierung und direkte Tests; Gate begrenzter Großbaum-Test mit
   sicherem Abbruch.
