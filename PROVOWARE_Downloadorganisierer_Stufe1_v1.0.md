PROVOWARE - STUFE 1: ANFORDERUNGSBASELINE UND ENTWICKLUNGSPLAN
Paket: Download-Organisierer/Aufraeumtool fuer private Ubuntu/Kubuntu-Systeme
Version: STUFE1-v1.0
Datum: 2026-09-21
Baseline: REQ-BASELINE-1
SHA-256 der kanonischen Anforderungsbasis: 00d23ba02f87dd59ec07151d8614c97e2ef6c434c7e86430198120aedb052621
Status: 🟨 GELB - PLANUNGSSTAND; STUFE 2 NOCH NICHT BEGONNEN
Pruefunabhaengigkeit: Stufe 1 durch denselben Agenten erstellt. Fuer Stufe 3 ist mindestens prozessuale Trennung mit eingefrorenem RC, frischem Pruefpfad und neuer Evidence verbindlich.

1. SCOPE UND ZIELBILD

BELEGT: Gewuenscht ist ein fuer Laien optimiertes Download-Organisier- und Aufraeumwerkzeug, das einfache und komplexere Aufgaben abdeckt, dabei sehr einfach bedienbar und zugleich weitgehend konfigurierbar bleibt. Bedienung soll primaer ueber Buttons, Auswahl- und Dateidialoge erfolgen.

BELEGT: Die Oberflaeche soll modern, gross und gut lesbar sein. Einstieg ueber Startroutine/Wizard, danach Dashboard mit Kacheln, Favoriten/haeufigen Funktionen, seitlicher Hilfe und gefuehrten Workflows.

BELEGT: Zielplattform ist mindestens Ubuntu beim Nutzer und bei dessen Mutter. Gewuenscht ist ein transportierbares ZIP mit Ordnerstruktur und moeglichst einer Klick-/Startdatei.

BELEGT: Vier kontrastgepruefte Farbthemen, variable Schriftgroesse, deutlich kontrastierende Eingabebereiche, Drag & Drop, dreistufige Nutzereinstellungen (Laie/Profi/Experte) plus separater Entwicklerbereich sind gefordert.

BELEGT: Logging/Debugging soll den normalen Nutzer nicht belasten. Optional soll bei Beendigung oder Absturz ein leicht verstaendlicher TXT-Diagnoseexport in den Download-Ordner entstehen.

BELEGT: Zu Beginn der Entwicklung sollen sechs grafische UI-Entwuerfe gemeinsam auf einem Bild zur Orientierung erstellt werden.

2. ANFORDERUNGSREGISTER - REQ-BASELINE-1

REQ-001 | Original unveraendert
Ich brauch für meine mutter, ein download-organisier und aufräumtool. für einfache, aber auch komplexere aufgaben. maximal simpel, aber auch maximal konfigurierbar und zwar immer über auswahldialoge oder buttons, also laien optimiert und nutzerfreundlich. Ich habe keine ahnung von irgendwas. und mutti auch nicht. also musst du mit denken. und auch fehleinschätzungen von mir als eventuell berücksichtigen und hinweisen.

REQ-002 | Original unveraendert
Es soll auf jeden Fall extrem simpel gestaltet sein, also dass man eigentlich reinkommt über eine Art Startroutine, auch Wizard-mäßig, die dann praktisch in einem übersichtlichen Art Kachelbereich mit beschriebenen einfachen Funktionen oder Favoriten oder häufig verwendeten Sachen, eine Art Dashboard, eine Art Hilfe an der Seite und nützliche für Laien funktionierende und hilfreiche Funktionen.

REQ-003 | Original unveraendert
Alles ein bisschen modern, natürlich so, dass es auch wirklich auf meinem Ubuntu ausprobiert werden kann, auf Mutti ihrem ausprobiert werden kann. Also am besten wäre es, wenn es eigentlich wirklich nur eine mobile Klick- und Startdatei wäre mit einer entsprechenden Ordnerstruktur dahinter, die man als ZIP transportieren kann und ja, irgendwie sowas in der Art.

REQ-004 | Original unveraendert
Am besten auch eine Art Workflow einbauen, wo man immer, wenn man zum Beispiel bestimmte Standardsachen nimmt, eine Art: Jetzt kommt das, jetzt musst du das tun, sieht und diese auch farblich hervorgehoben wird oder eventuell animiert wird, aber nicht störend, sondern einfach nur, dass der Nutzer merkt, da wäre das Nächste zu tun. Debugging und Logging-System natürlich, das den Nutzer aber nicht betrifft, also nur für die Entwicklung, soll in einem versteckten Bereich, der faktisch hervorgeholt werden kann, alles sein. Auch die ganzen Entwicklereinstellungen, die eventuell sind, die können da dort mit rein. Nutzer sollen nur einfache Einstellungen haben, dreistufig, so Laien-, Profi- und Experteneinstellungen und dann gibt's halt noch die Entwicklereinstellungen, so wie zum Beispiel das Debugging ausstellen und sowas alles, das gehört nachher alles in die Entwicklereinstellungen. Und möglichst schön nach Best Practices, gängigen Standards, extrem wartbar, mit Start beginnt, also ein Skript erstellen, das die Startroutine mit vollständiger Auflösung der Abhängigkeiten, ohne dass der Nutzer da irgendwie eingreifen muss oder so, aber extrem gut informiert wird über Status und vielleicht auch farblich.

REQ-005 | Original unveraendert
Es soll auch erweiterbar sein, vielleicht auch plug-in-fähig und so barrierefreie Sachen wie Drag-and-Drop und sowas alles beinhalten. Und in der Anfangszeit praktisch über Dashboard soll eine Art Abhak, oder nicht Abhak, sondern ein Kästchen zum Abhaken sein. Wenn das aktiviert ist, wird am Absturz oder bei Beendigung immer eine TXT-Datei praktisch exportiert, automatisch in den Download-Order mit der absolut ultimativen Debugging-Auswertung in einfacher Sprache, mit genau eindeutigen Vorkommnissen und eventuell sogar irgendwelchen weiterführenden Lösungen oder Details, sodass praktisch immer reproduzierbar bleibt, wo die Sachen gewesen sind, und im Endeffekt noch weitere hilfreiche Sachen.

REQ-006 | Original unveraendert
Schrift soll von Anfang an sehr gut sichtbar sein, also groß sein, soll variabel sein, einstellbar, genauso wie die Farbthemen. Es sollen vier Farbthemen vorhanden sein, unterschiedlichster Art und Farben. Achte auf die Kontraste und auch bei Schriftarten. Eingabebereiche sollen in einem zum Hauptfarbenbereich kontrastform farblichen Sache dargestellt werden und auch dabei extrem auf den Kontrast von Schrift und Hintergrund achten.

REQ-007 | Original unveraendert
Was habe ich noch Wichtiges vergessen oder was kann noch ergänzt werden oder weiterführend nützlich für Layout?

REQ-008 | Original unveraendert
schon Anfang der Entwicklung auch erst mal mit grafischen Bildentwürfen, vielleicht so mal sechs Stück auf einem Bild erst mal anfangen zu arbeiten, damit wir uns so orientieren, wie es am Ende werden soll. Hast du das alles verstanden?

REQ-009 | Original unveraendert
Dann ich bin fertig.

3. NORMALISIERTE ANFORDERUNGSMATRIX

REQ-001 | Ziel/Scope, GUI/UX | Normalisiert: Download-Organisation und Aufraeumen mit einfachem Standardweg und erweiterten Optionen; keine Technikkenntnisse voraussetzen. | Ziel: sichere Selbstbedienung. | Akzeptanz: Kernaufgaben ohne Terminal und ohne Fachbegriffe abschliessbar; fortgeschrittene Optionen erreichbar, aber nicht im Standardweg stoerend. | Abhaengigkeit: GUI, Sicherheitskern, Preview/Undo. | Risiko: Fehlbedienung bei destruktiven Aktionen. | Testidee: Laien-Kernworkflow plus Fehlklick-Szenarien. | Block: B01-B06 | Status: BELEGT.

REQ-002 | GUI/UX | Normalisiert: Wizard-Einstieg, danach uebersichtliches Kachel-Dashboard, Favoriten/haeufige Funktionen und kontextuelle Hilfe. | Akzeptanz: Erstnutzer erkennt naechsten Schritt und Kernfunktionen ohne Anleitung. | Block: B02-B03 | Status: BELEGT.

REQ-003 | Portabilitaet/Start | Normalisiert: Ubuntu-tauglicher, transportierbarer ZIP-Aufbau mit moeglichst einer Klick-/Startdatei. | Akzeptanz: Start aus entpacktem Paket ausserhalb Entwicklungsordner reproduzierbar. | Konflikt: "vollstaendige Aufloesung der Abhaengigkeiten ohne Eingriff" darf keine stillen Downloads/Installationen erzeugen. | Sicherer Standard: vorhandene Systemkomponenten pruefen, fehlende Komponenten klar anzeigen; Installation nur bewusst freigeben. | Block: B01/B07 | Status: BELEGT; konkrete Ubuntu-Versionen OFFEN.

REQ-004 | Workflow/Logging/Einstellungen/Wartbarkeit | Normalisiert: gefuehrte Schritte mit dezenter visueller Hervorhebung; Laie/Profi/Experte; Entwicklerbereich separat; wartbarer Startpfad und Statusanzeige. | Akzeptanz: naechster Schritt klar, Animation abschaltbar/reduziert; Entwicklerfunktionen nicht versehentlich im normalen Ablauf. | Block: B02/B03/B08 | Status: BELEGT.

REQ-005 | Erweiterbarkeit/Accessibility/Diagnose | Normalisiert: Erweiterungsarchitektur, Drag & Drop, optionaler Diagnose-TXT-Export bei Beendigung/Absturz. | Akzeptanz: Export nur nach Opt-in, datenschutzgeprueft, mit Ablaufkennung, Zeitpunkt, beobachteten Ereignissen, Fehlern und reproduzierbaren Schritten; keine erfundenen Ursachen/Loesungen. | Konflikt: "absolut ultimativ/eindeutig" ist nicht immer technisch belegbar. | Sicherer Standard: Fakten, Vermutungen und offene Ursachen getrennt kennzeichnen. | Block: B05/B08/B09 | Status: teils BELEGT, technische Machbarkeit OFFEN.

REQ-006 | Accessibility/Themes | Normalisiert: grosse variable Schrift, vier visuell unterschiedliche Themes, hohe Kontraste, kontrastreiche Eingabefelder. | Akzeptanz: UI bleibt bei 100/150/200 Prozent nutzbar; Kontrastwerte werden gegen festgelegten Accessibility-Standard gemessen; keine Bedeutung nur ueber Farbe. | Block: B02/B04 | Status: BELEGT; konkrete Farbschemata OFFEN.

REQ-007 | Offene Entscheidung/Layout | Original ist eine Aufforderung an den Qualitaetspruefer, fehlende Layout-/UX-Aspekte mitzudenken. | Daraus folgen abgeleitete Qualitaetsanforderungen in Abschnitt 4. | Block: B02-B04 | Status: BELEGT.

REQ-008 | Designprozess | Normalisiert: Entwicklungsbeginn mit sechs grafischen UI-Konzepten auf einem gemeinsamen Vergleichsbild. | Akzeptanz: sechs klar unterscheidbare, beschriftete Entwuerfe mit Dashboard, Wizard, Hilfe, Workflow-Hinweis und mindestens einem Einstellungszustand; Auswahl erfolgt vor produktiver UI-Implementierung. | Block: B00 | Status: BELEGT.

REQ-009 | Zustandswechsel | Die Nachricht enthaelt die Triggerwoerter, ist aber nicht exakt "Ich bin fertig" und beendet den Sammelmodus daher nicht. | Status: BELEGT.

4. ABGELEITETE QUALITAETSANFORDERUNGEN

AQ-001: Jede schreibende Aufraeumaktion braucht standardmaessig Preview vor Echtlauf. Loeschen wird bevorzugt in einen reversiblen Zustand verschoben statt sofort irreversibel entfernt.
AQ-002: Undo/Recovery muss fuer relevante Dateioperationen geplant und getestet werden.
AQ-003: Pfade, Dateinamen, Unicode, Leerzeichen, Symlinks und Traversal werden als untrusted input behandelt.
AQ-004: Keine Aktion ausserhalb explizit ausgewaehlter/verifizierter Ordnergrenzen.
AQ-005: Fortschritt, Pause/Abbruch und klarer Endzustand bei langen Jobs; kein unkontrollierter Mehrfachstart.
AQ-006: Tastatur-only-Kernworkflow, sichtbarer Fokus, sinnvolle Tab-Reihenfolge, Screenreader-Beschriftung soweit Framework unterstuetzt.
AQ-007: Reduced-Motion/Animation-aus fuer visuelle Hinweise.
AQ-008: Gefaehrliche Aktionen erhalten klare Wirkungserklaerung und keine irrefuehrenden Standardbuttons.
AQ-009: Diagnoseexport darf keine Secrets oder unnoetigen personenbezogenen Dateiinhalte sammeln; Dateinamen/Pfade sind als potenziell sensibel zu behandeln.
AQ-010: Offline-Verhalten muss definiert sein; keine stille Netzwerkabhaengigkeit.
AQ-011: Konfiguration erhaelt Version/Schema und sichere Migration; keine stille Migration.
AQ-012: Plugin-Faehigkeit wird als spaetere Erweiterungsgrenze geplant; Plugins duerfen nicht automatisch geladen/installiert werden und benoetigen klare Vertrauens-/Berechtigungsgrenzen.
AQ-013: Startdatei darf keine Rechteausweitung verstecken; Least Privilege.
AQ-014: Favoriten/haeufige Funktionen duerfen den Nutzer nicht zu riskanten Aktionen verleiten; riskante Aktionen bleiben sichtbar getrennt.
AQ-015: Leerer Zustand, erster Start, Fehlerzustand, kein Zugriff, kein Speicherplatz und abgebrochener Vorgang brauchen laiengerechte Screens.
AQ-016: Hilfe muss kontextuell sein und in einfacher Sprache sagen: was passiert, warum, Auswirkung, Rueckweg, Ergebnisort, naechster Schritt.
AQ-017: Vier Themes muessen nicht nur "anders" aussehen, sondern dieselbe Informationshierarchie und Accessibility erhalten.
AQ-018: Drag & Drop ist Zusatzweg, nicht einziger Weg; Dateidialog bleibt gleichwertig.
AQ-019: Diagnoseexport bei normaler Beendigung und Crash sind technisch getrennte Pfade; Crash-Export darf nicht als garantiert angenommen werden.
AQ-020: Paketintegritaet, Lizenz-/Abhaengigkeitsliste und reproduzierbarer Start werden Release-Gates.

5. WICHTIGE FEHLEINSCHAETZUNGEN / KONFLIKTE

🟧 WARNUNG: "Eine Klickdatei loest alle Abhaengigkeiten automatisch" kollidiert mit sicherem, local-first Betrieb, wenn dafuer still installiert oder aus dem Netz geladen werden muesste. Geplanter Standard: erst pruefen, dann erklaeren, dann nur nach bewusster Freigabe installieren. Fuer maximale Portabilitaet wird bevorzugt eine Paketierungsform untersucht, die Abhaengigkeiten soweit praktikabel mitliefert.

🟧 WARNUNG: "Absturzbericht immer" ist nicht absolut garantierbar. Bei Prozesskill, Stromausfall, vollem Datentraeger oder defektem Dateisystem kann kein Abschlussbericht geschrieben werden. Deshalb wird laufende, sparsame Ereignisprotokollierung plus Recovery-Auswertung beim naechsten Start geplant.

🟧 WARNUNG: Drag & Drop allein ist nicht barrierefrei. Es bleibt eine zusaetzliche Bedienform neben Buttons/Dateidialog und Tastaturbedienung.

🟧 WARNUNG: "maximal simpel" und "maximal konfigurierbar" stehen in Spannung. Sicherer Standard: progressive Offenlegung - Laienmodus zeigt nur sichere Kernentscheidungen, Profi/Experte erweitert kontrolliert, Entwicklerbereich bleibt getrennt.

6. LAIEN-, UX- UND FEHLERSZENARIEN

Befund A: Erststart mit zu vielen Optionen -> Ueberforderung -> P1 -> BELEGT aus Zielsetzung. Loesung: Wizard mit wenigen Entscheidungen und spaeterem Dashboard.
Befund B: Aufraeumen ohne Preview -> moeglicher Datenverlust -> P0 -> PLAUSIBEL bis Implementierung. Loesung: Preview, Zielgrenzen, reversible Aktion, Undo.
Befund C: Animation lenkt ab -> Accessibility-/UX-Risiko -> P2 -> PLAUSIBEL. Loesung: dezent, kurz, Reduced Motion.
Befund D: Debugdaten enthalten private Pfade/Dateinamen -> Datenschutzrisiko -> P1 -> PLAUSIBEL. Loesung: Opt-in, Minimierung, Redaction/Preview des Exports.
Befund E: Plugin-System vergroessert Angriffs-/Wartungsflaeche -> P2/P1 je Umsetzung -> PLAUSIBEL. Loesung: Kern zuerst stabil; Plugins spaeter mit Manifest, Version, Berechtigungen und deaktiviertem Auto-Install.

Simulationsfall: Nutzer waehlt "Downloads aufraeumen" -> Tool scannt nur ausgewaehlten Ordner -> zeigt Kategorien und geplante Aktionen -> Nutzer bestaetigt -> transaktionaler Lauf -> Ergebnis + Undo. Fehlerfall: Ziel verschwindet oder Rechte fehlen -> keine Teilaktion ohne definierten Zustand; klare Meldung und Rueckweg.

Simulationsfall: Nutzer zieht Ordner hinein -> Pfadpruefung -> bei Symlink/Aussenpfad Warnung/Block -> alternative Auswahl per Dialog.

Simulationsfall: Crash waehrend Verschieben -> Journal/Checkpoint erlaubt beim Neustart "Fortsetzen" oder "Zuruecksetzen"; keine Behauptung ueber Erfolg ohne Abgleich.

7. PRIORITAET UND RISIKO

P0-Planungsfelder: unkontrolliertes Loeschen/Schreiben; Pfadgrenzen/Symlinks; fehlender Rueckweg; inkonsistente Teiloperationen; unklarer Projekt-/Paketstand.
P1: Startweg, Kernworkflow, Preview, Recovery, Laienverstaendlichkeit, Diagnose-Datenschutz.
P2: Themes, Drag & Drop, Profi-/Expertenkomfort, Plugin-Vorbereitung.
P3: rein kosmetische Feinheiten.

Risikobewertung vor Implementierung ist vorlaeufig:
R-01 Datenverlust durch Aufraeumaktion: 3 x 4 x 3 = 36, HOCH.
R-02 Pfad-/Symlink-Grenzverletzung: 2 x 4 x 4 = 32, HOCH.
R-03 stille Abhaengigkeitsinstallation/Rechteausweitung: 2 x 4 x 3 = 24, MITTEL.
R-04 Diagnose-Datenleck: 2 x 3 x 4 = 24, MITTEL.
R-05 Crash mit inkonsistentem Zustand: 3 x 4 x 3 = 36, HOCH.
R-06 Accessibility/Skalierungsfehler: 3 x 2 x 2 = 12, MITTEL.
R-07 Plugin-Missbrauch/Kompatibilitaet: 2 x 4 x 4 = 32, HOCH, falls Plugins aktiv werden.

8. ENTWICKLUNGSPLAN IN ABHAENGIGKEITSREIHENFOLGE

B00 - Visuelle Orientierung
Ziel: sechs UI-Bildentwuerfe auf einem Vergleichsbild.
REQ: 002, 004, 006, 007, 008.
Nicht-Ziel: produktiver Code.
Voraussetzung: Baseline.
Risiken: schoene Optik ohne sichere Workflows.
Preview/Probe: sechs Varianten mit identischen Kernaufgaben vergleichen.
Checkpoint: ein dokumentierter Designkorridor, keine stillschweigende Auswahl.
Tests: Laien-Gegenpruefung, Kontrast-/Lesbarkeitsvorpruefung, Informationshierarchie.
Rollback: Entwurf verwerfen, keine Produktdaten betroffen.
Evidence: Bild + Auswahl-/Befundnotiz.
Akzeptanz: sechs unterscheidbare Konzepte vorhanden und gegen Kernanforderungen bewertet.
Aufwand: S. Blocker: keiner fuer Entwurf; produktive UI wartet auf Designentscheidung.

B01 - Projektkern, Paket, Start und Sicherheitsgrenzen
REQ: 001, 003, 004 + AQ-003/004/010/013/020.
Ziel: reproduzierbare Projektstruktur, Startpfad, Pfadmodell, Abhaengigkeitsinventar.
Nicht-Ziel: Aufraeumautomatik.
Preview: Start-/Preflight nur lesend.
Tests: frischer Start, vorhandener Zustand, offline, fehlende Abhaengigkeit, Rechte, Unicode/Leerzeichen.
Failure/Recovery: fehlende Runtime darf nichts veraendern.
Rollback: Paketordner entfernen.
Evidence: Versionen, Hashes, Startlogs.
Akzeptanz: Startweg ist reproduzierbar ohne stille Installation/Rechteausweitung.
Aufwand: M. Harter Blocker: konkrete Testumgebung/Projektgrundlage fuer Stufe 2.

B02 - UX-Shell, Wizard, Dashboard, Hilfe
REQ: 001, 002, 004, 006, 007.
Ziel: laiengerechter Grundrahmen.
Tests: Erststart, Wiederkehr, Tastatur, Fokus, Zoom.
Failure: defekte Konfiguration -> sichere Defaults ohne Datenoperation.
Recovery: Einstellungen ruecksetzbar.
Evidence: Screens/GUI-Testprotokoll.
Akzeptanz: Kernnavigation ohne Fachwissen.
Aufwand: M.

B03 - Gefuehrte Workflows und progressive Einstellungen
REQ: 001, 004.
Ziel: Laie/Profi/Experte plus getrennte Entwickleransicht; naechster Schritt klar hervorgehoben.
Tests: Moduswechsel ohne versteckte Verhaltensaenderung; Reduced Motion.
Rollback: Einstellungsreset.
Aufwand: M.

B04 - Themes und Accessibility
REQ: 005, 006 + AQ-006/007/017/018.
Ziel: vier Themes, Schriftgroesse, Kontrast, gleichwertige Maus/Tastatur/Dateidialog/Drag&Drop-Wege.
Tests: 100/150/200 Prozent, Tastatur-only, Fokus, Kontrastmessung, lange Texte.
Aufwand: M.

B05 - Dateiinventar und sichere Preview
REQ: 001, 005 + AQ-001/003/004.
Ziel: Downloads lesen, klassifizieren und geplante Aktionen anzeigen, noch ohne destruktive Echtaktion.
Tests: grosse Dateien, Sondernamen, Symlinks, defekte Links, Rechte, grosse Mengen.
Failure: Scanfehler bleibt lesend.
Aufwand: L.

B06 - Sichere Dateioperationen, Undo, Recovery
REQ: 001 + AQ-001/002/005.
Ziel: kleine transaktionale Operationen, Journal/Checkpoint, Locking, Abbruch, Undo.
Tests: Crash/Abbruch, Parallelstart, knapper Speicher, Zielkonflikte, Recovery/Wiederholung.
Security: Traversal/Symlink/TOCTOU soweit relevant.
Akzeptanz: kein freigaberelevanter Schreibpfad ohne Preview und belegten Rueckweg.
Aufwand: XL. Harter P0-Gate.

B07 - Portable Paketierung
REQ: 003.
Ziel: transportierbares ZIP und moeglichst Klickstart unter den konkret unterstuetzten Ubuntu/Kubuntu-Versionen.
Tests: entpackt an anderem Pfad, ausserhalb Dev-Ordner, offline, frisches Nutzerprofil soweit praktikabel.
Aufwand: L.

B08 - Logging, Entwicklerbereich, Diagnose
REQ: 004, 005 + AQ-009/019.
Ziel: strukturierte interne Logs und optionaler einfacher TXT-Diagnoseexport.
Tests: Opt-in/out, normaler Exit, simulierter Crash, sensible Pfade, Schreibfehler, voller Datentraeger.
Akzeptanz: Fakten/Annahmen/offene Ursache getrennt; keine Secrets; Exportfehler gefaehrdet keine Nutzdaten.
Aufwand: L.

B09 - Erweiterungsgrenze/Plugin-Vorbereitung
REQ: 005 + AQ-012.
Ziel: stabile interne Schnittstellen; Plugin-System nur aktivieren, wenn Sicherheits- und Wartungsmodell belegt.
Tests: inkompatibles/defektes Plugin, deaktivierte Plugins, Berechtigungsgrenzen.
Aufwand: M-L. Weicher Blocker: kann fuer erste Version als dokumentierte Erweiterungsgrenze statt aktivem Plugin-System enden.

B10 - Gesamttests, RC-Freeze
Ziel: komplette Regression, Failure-/Recovery-Matrix, Paketintegritaet, Evidence-Index.
Akzeptanz: keine P0, relevante Regressionen gruen, Recovery belegt, RC-Fingerprint.
Aufwand: L.

B11 - STUFE 3: prozessual getrennter Audit
Ziel: eingefrorenen RC aus frischem Pruefpfad ohne Reparaturen auditieren.
Akzeptanz: Traceability geschlossen; Releaseentscheidung nur auf neuer Evidence.
Aufwand: L.

9. ZIELPRODUKT UND UMGEBUNG

Zielprodukt: lokales, laiengerechtes Desktop-Werkzeug zur sicheren Organisation und kontrollierten Bereinigung des Download-Ordners mit Wizard, Dashboard, Preview, gefuehrten Workflows, Undo/Recovery, Accessibility und optionaler Diagnose.

Unterstuetzt: Ubuntu/Kubuntu-Versionen sind noch OFFEN und muessen vor Implementierung/Test konkret inventarisiert werden. Der Wunsch "mein Ubuntu und Mutti ihres" ist BELEGT, die Versionen sind nicht bekannt.

Bewusst noch nicht zugesagt: andere Linux-Distributionen, Windows, macOS, mobile Betriebssysteme, Netzwerk-/Cloud-Aufraeumen, Root-/Systemordner-Bereinigung, aktive Drittanbieter-Plugins.

10. DEFINITIONEN

Definition of Done: Baseline/CRs tracebar; alle Entwicklungsbloecke mit Evidence; sichere Schreibpfade; Regression/Failure/Recovery; Accessibility; Paket/Start reproduzierbar; eingefrorener RC; separater Audit; Exporte validiert.

Definition Release Candidate: versionierter, unveraenderlicher Paketstand mit Fingerprint, Changelog, Teststatus, bekannten Grenzen, Evidence-Index und reproduzierbarem Startpfad.

Definition Release: RC besteht frischen Stufe-3-Audit; kein P0/sicherheitskritisches ROT; Recovery/Rollback soweit erforderlich belegt; Paketintegritaet und Versionskonsistenz belegt; bekannte Grenzen dokumentiert.

11. STUFE-1-GATE UND NAECHSTER SICHERER SCHRITT

🟨 GELB: Die Anforderungen sind als REQ-BASELINE-1 eingefroren und planbar. Stufe 2 ist NICHT begonnen. Es liegt hier keine reale Projektgrundlage/kein Quellcode vor, daher darf keine Umsetzung behauptet werden.

Naechster sicherer Schritt in Stufe 2, sobald eine Projektgrundlage angelegt bzw. zugaenglich ist: B00 ausfuehren - sechs grafische Bildentwuerfe auf einem Vergleichsbild - danach B01 mit Inventar/Preflight. Vor produktivem Schreiben muessen die tatsaechlichen Ubuntu/Kubuntu-Versionen und die verfuegbaren Laufzeitkomponenten inventarisiert werden.

12. EXPORTSTATUS

Dieser Bericht ist der Stufe-1-Planungsstand. PDF, Markdown und TXT werden aus derselben Inhaltsbasis erzeugt. ZIP und Manifest werden anschliessend technisch validiert. Ein erfolgreicher Export ist keine Produktfreigabe.
