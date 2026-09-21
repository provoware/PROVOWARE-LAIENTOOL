# PROVOWARE LAIENTOOL – UI-/Erscheinungsbild Profi-Spezifikation

**Status:** B00 Designsystem definiert  
**Bezug:** REQ-001, REQ-002, REQ-004, REQ-005, REQ-006, REQ-008; AQ-006, AQ-007, AQ-015, AQ-016, AQ-017, AQ-018  
**Architektur:** ADR-0001

## 1. Designziel

Das Erscheinungsbild verbindet moderne Desktop-Anwendung, klare Dateiverwaltung und visuelle Workflow-Führung.

Der Nutzer soll innerhalb weniger Sekunden erkennen:

**Wo bin ich? → Was kann ich tun? → Was ist der nächste Schritt? → Was passiert dabei? → Ist alles sicher?**

Leitwirkung:

**modern · kontrastreich · ruhig · hochwertig · eindeutig · modular · visuell geführt · technisch sauber · einsteigerfreundlich**

Neon ist funktionaler Akzent und keine permanente Dekoration.

## 2. Grundlayout

Stabiles Desktop-Raster mit fünf Ebenen:

| Bereich | Funktion |
| --- | --- |
| Kopfbereich | Branding, globale Suche, Einstellungen, Hilfe |
| linke Navigation | Hauptbereiche, Werkzeuge, Favoriten, Systemzugänge |
| Workflow-Leiste | aktuelle Arbeitsphase und nächster Schritt |
| Hauptarbeitsfläche | Dateien, Ergebnisse, Kategorien oder Bearbeitung |
| Detail-/Vorschaubereich | Thumbnail, Metadaten, Aktionen, Status |

Theme-Wechsel dürfen keine Funktion verschieben.

## 3. Visuelle Hierarchie

**A – aktueller Arbeitsschritt:** stärkste Hervorhebung, Neon-Rahmen, Nummer, Symbol, Text.  
**B – primäre Aktionen:** große Buttons oder Kacheln.  
**C – Arbeitsdaten:** Dateiliste, Kategorien, Vorschauen, Metadaten.  
**D – Zusatzinformationen:** Status, Speicherplatz, Hilfe, sekundäre Optionen.

Nicht alle Bereiche dürfen gleichzeitig dieselbe visuelle Priorität erhalten.

## 4. Workflow-System

Beispiel:

**① Dateien → ② Suchen → ③ Vorschau → ④ Sortieren → ⑤ Duplikate → ⑥ Organisieren**

Jeder Schritt besitzt Nummer, Symbol, Klartext, Status und eine sichtbare Verbindung zum vorherigen und nächsten Schritt.

| Zustand | Darstellung |
| --- | --- |
| nicht begonnen | neutral |
| bereit | dezenter Theme-Akzent |
| aktiv | Neon-Rahmen + erhöhter Kontrast |
| erledigt | Symbol + bestätigter Status |
| Warnung | Gelb/Orange + Klartext |
| Fehler | Rot + Symbol + Handlungsempfehlung |

Keine blinkenden Elemente. Reduced Motion deaktiviert Animation vollständig.

## 5. Neon-System

Neon wird nur für Bedeutungszustände eingesetzt:

- aktive Navigation
- aktueller Workflow-Schritt
- Tastaturfokus
- ausgewähltes Element
- primäre Aktion
- wichtiger Status

Empfehlung: 1–2 px Rahmen plus weicher äußerer Glow. Keine großflächigen Neon-Hintergründe hinter Fließtext.

## 6. Karten- und Flächensystem

Cards erhalten klaren Innenabstand, ruhige Grundfläche, eindeutige Überschrift, optionalen Statusbereich und leichte Trennung vom Hintergrund.

Radiusfamilie:

- klein: 6–8 px
- Standard: 10–12 px
- große Panels: 14–18 px

## 7. Hauptnavigation

Primär: Start, Dateien, Suchen, Favoriten, Zuletzt verwendet, Externe Laufwerke, Papierkorb.

Werkzeuge: Duplikate, Organisieren, Assistent.

Unterer Bereich: Einstellungen, Hilfe, Entwicklerbereich nur bei expliziter Freigabe.

Nur der aktive Navigationseintrag erhält starken Theme-Akzent.

## 8. Datei-Arbeitsbereich

Drei Ansichten:

1. Liste
2. Kacheln
3. kompakte Ansicht

Listenansicht enthält mindestens Checkbox, Dateityp-Icon oder Miniatur, Name, Typ, Größe, Änderungsdatum, Status und optionales Aktionsmenü.

Hover, Auswahl und Tastaturfokus müssen klar unterscheidbar sein.

## 9. Vorschau

- Bilder → Thumbnail
- PDF → erste Seite
- Video → Vorschaubild
- Audio → Icon + Metadaten; später optional Waveform
- Dokumente → Icon oder erzeugte Vorschau
- unbekannte Formate → eindeutiges Dateityp-Symbol

Unterhalb: Dateiname, Dateityp, Größe, Abmessungen/Laufzeit, Änderungsdatum, Pfad, Tags/Kategorie.

Destruktive Aktionen bleiben visuell und funktional von normalen Aktionen getrennt.

## 10. Vier Themes

Alle Themes verwenden identische Struktur und semantische Zustände.

### Theme 01 – Purple Neon
Grund: tiefes Navy/Anthrazit · Hauptfarbe: kräftiges Lila · Sekundärfarbe: elektrisches Blau · Kontrast 1: Cyan/Türkis · Kontrast 2: frisches Grün.

### Theme 02 – Turquoise Neon
Grund: sehr dunkles Petrol/Blaugrün · Hauptfarbe: Türkis · Sekundärfarbe: Cyanblau · Kontrast 1: Violett · Kontrast 2: Amber/Orange.

### Theme 03 – Graphite Electric
Grund: Graphit/tiefes Anthrazit · Hauptfarbe: elektrisches Blau · Sekundärfarbe: kaltes Weiß/Blaugrau · Kontrast 1: Neongrün · Kontrast 2: Amber.

### Theme 04 – Crimson / Copper
Grund: dunkles Burgunder/Schwarzbraun · Hauptfarbe: Rot/Magenta · Sekundärfarbe: Kupfer/Orange · Kontrast 1: helles Cyan · Kontrast 2: warmes Cremeweiß.

## 11. Typografie

- Seitentitel: 24–32 px
- Bereichsüberschrift: 18–22 px
- Standardtext: 15–17 px
- Buttons: 15–18 px
- Hilfetext: mindestens 14 px
- globale Skalierung: 100 / 125 / 150 / 175 / 200 %

Layout darf bei 200 % nicht auseinanderbrechen.

## 12. Buttons

Primärbutton: starker Theme-Akzent, hoher Kontrast, große Klickfläche, Icon + Text.

Sekundärbutton: ruhiger Hintergrund, klarer Rahmen.

Gefährliche Aktion: eigene semantische Farbe, Wirkungserklärung und fachlich erforderliche Bestätigung.

## 13. Statussystem

Status besitzt immer Symbol + Text; bei relevanten Vorgängen zusätzlich Zahl oder Fortschrittswert.

Beispiele: 🟢 Bereit · 🟡 Prüfung erforderlich · 🔴 Fehler · 🔵 Vorgang läuft · 🔒 Schreibgeschützt.

Farbe darf niemals allein Bedeutung vermitteln.

## 14. Anfängerhilfe

Kontextbezogene Hilfe erscheint direkt am Arbeitsschritt und ist ein-/ausblendbar.

Beispiel: **💡 Tipp für Einsteiger:** „Wähle zuerst einen Ordner. Es werden noch keine Dateien verändert.“

## 15. Sicherheitswirkung

Global permanent sichtbar:

**🔒 Sicherer Lese-Modus – Es werden keine Dateien verändert.**

Vor Schreibvorgängen muss sich dieser Bereich eindeutig verändern.

## 16. Mikrointeraktionen

Erlaubt: leichte Hover-Übergänge, sanftes Aufleuchten, Fortschrittsanimation, dezente Auswahltransition.

Nicht verwenden: Blinken, springende Layouts, starke Zoomanimationen, permanentes Pulsieren, bewegte Hintergrundeffekte.

## 17. Accessibility

Verbindlich: Tastaturbedienung, sichtbarer Fokus, Screenreader-Beschriftung, 200-%-Zoom, hoher Kontrast, Reduced Motion, große Klickflächen, keine reine Farbcodierung, verständliche Sprache.

Neon-Fokus darf gezielt als besonders sichtbarer Tastaturfokus dienen.

## 18. Responsive Desktop-Logik

Priorität bei Platzmangel:

1. Arbeitsbereich
2. aktuelle Aktion
3. Datei-/Ergebnisliste
4. Vorschau
5. Navigation
6. Zusatzinformationen

Die Vorschau darf einklappbar werden. Wichtige Aktionen dürfen nicht verschwinden.

## 19. Gesamtcharakter

**„Professionelles Werkzeug mit der Verständlichkeit einer guten Einsteiger-App.“**

Erster Eindruck: visuell attraktiv und modern.  
Längerer Einsatz: ruhig, logisch und vorhersehbar.

## 20. Verbindliche Designformel

**Dunkle ruhige Basis + modulare Cards + große Typografie + klare Datei-Vorschauen + stabile Navigation + vier echte Farbthemes + Neon nur für Bedeutung + sichtbarer Workflow + permanente Sicherheitsanzeige + progressive Komplexität = PROVOWARE UI-System**

## 21. B00-Abnahme

B00 gilt als fachlich definiert, wenn Designrichtung, vier Themes, Workflow-/Fokus-/Status-/Neonregeln und Accessibility-Grundregeln dokumentiert sind und noch keine produktive GUI-Implementierung behauptet wird.
