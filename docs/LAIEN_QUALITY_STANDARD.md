# PROVOWARE – Messbarer Laien-Qualitätsstandard

## Zweck

„Laienfreundlich“ ist kein Stilwort, sondern ein Abnahmevertrag. Eine Funktion gilt erst dann als laientauglich, wenn ein Nutzer ohne Projektwissen Ziel, Wirkung, Risiko und nächsten Schritt erkennen kann.

## 1. Kernprinzipien

1. **Erkennen statt erinnern:** sichtbare Auswahl, klare Standardwerte, keine vorausgesetzten Befehle.
2. **Eine sichere Hauptaktion:** pro Schritt genau eine klar dominierende Fortsetzung.
3. **Progressive Komplexität:** Expertenoptionen sind verfügbar, aber nicht Voraussetzung für den Standardweg.
4. **Wirkung vor Ausführung:** vor jeder schreibenden Aktion werden Quelle, Ziel, Anzahl, Umfang und Rückweg verständlich gezeigt.
5. **Fehler als Handlungsanweisung:** Meldungen nennen Problem, Auswirkung und konkrete nächste Aktion.
6. **Keine versteckten Zustände:** Lese-/Schreibmodus, Auswahl, Fortschritt und Abschluss sind sichtbar.
7. **Reversibilität:** soweit fachlich möglich Undo/Recovery statt irreversibler Direktaktion.

## 2. Messbare UX-Gates

Für jeden sichtbaren Kernworkflow gelten mindestens:

| Gate | PASS-Kriterium |
| --- | --- |
| Startklarheit | Innerhalb der ersten Ansicht ist erkennbar, was das Werkzeug macht und ob Dateien verändert werden. |
| Hauptaufgabe | Standardaufgabe ohne Terminal, Quellcodekenntnis oder Dateinamenswissen ausführbar. |
| Klickpfad | Standardfall benötigt keine unnötigen Schleifen oder Rücksprünge; jeder Schritt hat einen eindeutigen Zweck. |
| Fehlerverständnis | Fehlermeldung enthält Ursache/Fakt, Auswirkung und nächste sichere Aktion in Alltagssprache. |
| Sicherheitsverständnis | Vor Schreibzugriff ist sichtbar, **was** geändert wird und **wie** zurückgekehrt werden kann. |
| Abbruch | Nutzer kann vor irreversibler Wirkung abbrechen, ohne einen unklaren Zwischenzustand zu hinterlassen. |
| Abschluss | Ergebnis nennt erledigt / nicht erledigt / offen sowie den nächsten sinnvollen Schritt. |
| Tastatur | Kernworkflow vollständig per Tastatur erreichbar. |
| Fokus | Aktiver Tastaturfokus ist jederzeit sichtbar. |
| Skalierung | 100 %, 150 % und 200 % ohne abgeschnittene Kernaktionen oder unbedienbare Dialoge. |
| Kontrast | Text, Fokus, Auswahl und Status erfüllen den festgelegten Kontrastvertrag; Farbe ist nie alleiniger Informationsträger. |
| Reduced Motion | Keine notwendige Information hängt von Animation ab; Bewegungen sind reduzierbar. |

## 3. Laien-Textvertrag

Benutzertexte vermeiden unnötige interne Begriffe. Falls ein Fachbegriff unvermeidbar ist:

**Alltagsbegriff zuerst, Fachbegriff in Klammern danach.**

Beispiel:

> „Verknüpfung zu einem anderen Pfad (Symlink) wurde aus Sicherheitsgründen blockiert.“

Jede relevante Fehlermeldung folgt:

`WAS IST PASSIERT → WAS BEDEUTET DAS → WAS KANN ICH JETZT TUN`

Nicht zulässig als alleinige Nutzermeldung:

- rohe Exception;
- Stacktrace;
- Exit-Code ohne Erklärung;
- interne Klassen-/Funktionsnamen;
- „Invalid input“ ohne Korrekturhinweis;
- „Operation failed“ ohne Ursache oder sichere Folgeaktion.

## 4. Standardweg und Expertenweg

Der Standardweg darf keine Expertenentscheidung verlangen, wenn das System eine sichere Voreinstellung bestimmen kann.

Expertenoptionen:

- sind optisch sekundär;
- verändern nie heimlich Sicherheitsgrenzen;
- zeigen bei höherem Risiko eine Wirkungserklärung;
- besitzen nachvollziehbare Rücksetzwerte.

## 5. Validierung pro sichtbarer Änderung

Bei GUI-/Text-/Workflow-Änderungen dokumentiert die Evidence mindestens:

- getesteter Standardfall;
- ein typischer Fehlfall;
- Tastaturpfad;
- 100/150/200-%-Prüfung;
- Fokus und Kontrast;
- Abbruch-/Zurück-Pfad;
- Wortlaut der wichtigsten Status-/Fehlermeldungen;
- offene Punkte als `OPEN`.

## 6. Laien-Testprofil

Mindestens vor Release Candidate:

1. frisches Benutzerprofil ohne Projektwissen;
2. keine vorausgesetzte Terminalbedienung;
3. keine vorbereiteten Spezialpfade;
4. mindestens ein Unicode-/Leerzeichenfall;
5. mindestens ein fehlendes Capability-/Berechtigungs-Szenario;
6. Standardaufgabe vom Start bis Abschluss;
7. Testperson soll nach jedem kritischen Schritt beantworten können:
   - Was passiert als Nächstes?
   - Werden gerade Dateien verändert?
   - Kann ich zurück?
   - Was muss ich tun, wenn etwas nicht klappt?

Eine unklare Antwort ist ein UX-Befund, auch wenn der Code technisch korrekt arbeitet.

## 7. Qualitätsstatus

- 🟢 **PASS:** messbare Gates belegt.
- 🟨 **OPEN:** Funktion technisch vorhanden, Laiennachweis fehlt oder ist unvollständig.
- 🔴 **FAIL:** Nutzer kann Wirkung/Risiko nicht zuverlässig erkennen oder Standardweg ist nicht sicher bedienbar.

Technisches PASS ersetzt kein Laien-PASS.
