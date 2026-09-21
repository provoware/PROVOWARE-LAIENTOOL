# PROVOWARE – GUI-/Konsolen-Paritätsvertrag

## Zweck

Jede fachliche Funktion, die in der GUI verfügbar ist, muss auch über einen laienfreundlichen Konsolenweg erreichbar sein. GUI und Konsole sind ausschließlich unterschiedliche Adapter desselben Application-/Domain-Kerns.

## 1. Verbindliche Parität

Für jede nicht rein visuelle Funktion gilt:

- derselbe Use Case;
- dieselben Eingabevalidierungen;
- dieselben Sicherheitsgrenzen;
- dieselben Preview-/Recovery-Regeln;
- dieselben Statusmodelle;
- dieselben Fehlerklassen;
- dieselben fachlichen Ergebnisse.

Nicht zulässig:

- GUI-exklusive Fachlogik;
- CLI-exklusive Sicherheitslogik;
- direkte Dateioperationen aus Widgets oder Menühandlern;
- doppelte Implementierung derselben Fachregel.

Rein visuelle Funktionen wie Theme-Auswahl, Fenstergeometrie oder Vorschaugröße benötigen nur dann einen Konsolenweg, wenn sie fachliche Wirkung besitzen.

## 2. Laien-Zahlenmenü

Die Konsole nutzt nummerierte Menüs mit kurzen Klartextbezeichnungen.

Beispiel:

```text
PROVOWARE

1  Downloads prüfen
2  Dateien suchen
3  Vorschau anzeigen
4  Organisieren
5  Papierkorb / Rückgängig
6  Einstellungen
7  Hilfe
0  Beenden
```

Regeln:

- Hauptauswahl ausschließlich über Zahlen;
- `0` bedeutet konsistent Zurück oder Beenden;
- keine vorausgesetzten Shell-Kenntnisse;
- sichere Standardwerte;
- aktuelle Auswahl und Auswirkung vor Ausführung sichtbar;
- gefährliche Aktionen benötigen Preview und Bestätigung;
- Fehlermeldungen folgen: Was ist passiert? Was bedeutet das? Was kann ich tun?;
- bei Untermenüs bleibt die Navigation stabil und vorhersehbar;
- Funktionen werden nach Nutzeraufgabe, nicht nach internen Modulnamen benannt.

## 3. Capability Registry

Sobald echte Fachfunktionen entstehen, wird eine zentrale Capability-/Use-Case-Registry verwendet. Jeder Eintrag enthält mindestens:

- stabile Funktions-ID;
- Anzeigename;
- GUI-Verfügbarkeit;
- CLI-Verfügbarkeit;
- Sicherheitsklasse;
- Preview-Pflicht;
- Recovery-Pflicht;
- benötigte Capability;
- Status: `READY | OPEN | BLOCKED`.

GUI und Konsole lesen dieselbe Registry. Dadurch kann Paritätsdrift automatisch geprüft werden.

## 4. Paritätsgate

Eine neue GUI-Fachfunktion ist nicht vollständig abgenommen, solange nicht mindestens eines gilt:

1. gleichwertiger CLI-Zahlenmenüpfad ist implementiert und getestet; oder
2. die Funktion ist nachweislich rein visuell und als solche dokumentiert.

Eine fehlende CLI-Entsprechung wird als `OPEN` behandelt, nicht als PASS.

## 5. Tests

Für jeden gemeinsamen Use Case werden später Adapter-Paritätstests ausgeführt:

- gleiche Eingabe → gleiche fachliche Entscheidung;
- gleiche ungültige Eingabe → gleiche Fehlerklasse;
- gleiche Sicherheitsgrenze → gleiche Blockierung;
- gleiche Preview → gleiche Wirkungsaussage;
- gleiche Recovery-Voraussetzung → gleicher Status.

Die Tests vergleichen Fachresultate, nicht die Darstellung.

## 6. Architekturgrenze

```text
GUI Adapter ─┐
             ├─ Application / Domain Core ─ Safety / Preview / Recovery
CLI Adapter ─┘
```

Die Adapter dürfen darstellen, navigieren und Eingaben übersetzen. Sie dürfen keine eigene Fachentscheidung treffen.
