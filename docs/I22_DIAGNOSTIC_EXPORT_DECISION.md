# I22 – Diagnose-Export Decision Gate

## Status

**Entscheidung eingefroren. Keine Implementierung. Read-only-Lock bleibt unverändert aktiv.**

## Ausgangslage

I20 erzeugt einen redigierten Diagnosebericht ausschließlich in-memory bzw. auf stdout.

Aktuell gilt:

- keine Diagnose-Datei;
- keine Persistenz;
- kein Upload;
- kein Netzwerk;
- keine automatische Reparatur;
- `write_paths_enabled=False`.

I22 entscheidet ausschließlich, ob ein späterer expliziter Datei-Export fachlich zulässig sein darf.

## Entscheidung

Ein späterer Diagnose-Export **darf grundsätzlich implementiert werden**, aber nur unter einem eigenen Writer-/Export-Gate und nur bei vollständig erfülltem Vertrag.

I22 selbst öffnet keinen Schreibpfad.

## Nutzerinitiierung

Export ist ausschließlich erlaubt nach einer **expliziten Nutzeraktion**.

Nicht erlaubt:

- automatischer Export beim Start;
- automatischer Export bei Fehlern;
- stiller Crash-Dump;
- periodische Diagnose-Dateien;
- Hintergrundexport;
- Telemetrie;
- automatischer Upload.

## Exportinhalt

Exportiert werden darf ausschließlich ein bereits vollständig gebauter und redigierter `DiagnosticReport`.

Reihenfolge ist zwingend:

```text
read-only Fakten sammeln
→ DiagnosticReport bauen
→ Redaction vollständig anwenden
→ Report validieren
→ Exportvorschau
→ ausdrückliche Nutzerfreigabe
→ erst späterer Writer
```

Keine Rohdaten dürfen erst nach dem Schreiben redigiert werden.

## Formate

Für einen ersten späteren Export sind zulässig:

- JSON für reproduzierbare technische Analyse;
- Klartext für laienfreundliche Weitergabe.

Kein:

- ZIP;
- Binärformat;
- Datenbank;
- proprietäres Format;
- eingebetteter Screenshot;
- automatisches Anhängen weiterer Logs.

Weitere Formate benötigen einen neuen Vertrag.

## Zielwahl

Der Nutzer wählt ausdrücklich einen **vorhandenen Zielordner**.

Der spätere Writer muss mindestens prüfen:

- Zielordner existiert;
- Zielordner ist kein Symlink;
- Zielpfad ist sicher auflösbar;
- Zieldatei existiert noch nicht;
- kein Overwrite;
- kein Auto-Rename eines Konflikts ohne sichtbare Nutzerentscheidung;
- keine automatische Rechteausweitung.

Externe Datenträger benötigen vor Freigabe einen eigenen Ziel-/Mount-Vertrag oder müssen BLOCKED bleiben.

## Dateiname

Ein vorgeschlagener Dateiname darf automatisch erzeugt werden, z. B.:

```text
PROVOWARE-Diagnose-20260921-170000.json
```

Der Name darf keine:

- Nutzernamen;
- Hostnamen;
- Projektpfade;
- Dateinamen aus Nutzerdaten;
- Recovery-IDs;
- Secrets

enthalten.

## Overwrite

**Overwrite bleibt verboten.**

Existiert der Zielname bereits:

- Status BLOCKED;
- keine Datei wird verändert;
- Nutzer wählt einen anderen Namen oder Zielordner.

Kein stilles `(1)`-/`copy`-Suffix im ersten Vertrag.

## Redaction-Gate

Vor Export muss erneut belegt werden:

- Home-Pfade redigiert;
- E-Mail-Adressen redigiert;
- bekannte Token-Muster redigiert;
- Recovery-IDs nicht enthalten;
- keine unnötigen Umgebungsvariablen;
- keine persönlichen Dateilisten;
- keine ungefilterten Stacktraces.

Redaction-Failure = Export BLOCKED.

## Größen-/Umfangsgrenze

Der erste Exportvertrag bleibt klein und deterministisch.

Er enthält ausschließlich den bestehenden Diagnosebericht.

Kein rekursives Einsammeln von:

- Log-Verzeichnissen;
- Dateibäumen;
- Konfigurationsordnern;
- Browserprofilen;
- Journaldateien.

Damit bleibt der Datenschutzumfang prüfbar.

## Sicherheits-/Writer-Gate

Ein späterer Export ist der **erste ausdrücklich erlaubte kleine Schreibpfad** außerhalb produktiver Nutzerdateioperationen.

Deshalb darf er den bestehenden `read_only_guard.py` nicht beiläufig umgehen.

Vor Implementierung erforderlich:

1. expliziter I22-Folge-REOPEN für genau den Export-Writer;
2. Writer-Dateien klar getrennt vom allgemeinen read-only Produktkern;
3. statischer Guard wird nicht global abgeschaltet;
4. gezielter Allowlist-/Scope-Vertrag nur für den Export-Writer;
5. create-only / no-overwrite Verhalten;
6. Abbruch-/Fehler-/Partial-Write-Strategie;
7. Regressionstest gegen unbeabsichtigte andere Schreibpfade.

## Partial Write / Crash

Vor Writer-Implementierung muss entschieden und getestet werden, wie halbfertige Exporte verhindert oder eindeutig erkannt werden.

Mindestanforderung:

- keine vorhandene Datei überschreiben;
- bei Fehler niemals einen bestehenden Export beschädigen;
- unvollständige neue Datei klar erkennbar oder sicher entfernbar;
- kein automatischer Retry ohne Nutzerwissen.

Die konkrete atomare Schreibstrategie ist **noch nicht** freigegeben.

## Netzwerk

Datei-Export bedeutet ausschließlich lokales Speichern.

Nicht Bestandteil:

- E-Mail-Versand;
- GitHub-Issue-Upload;
- Cloud-Speicher;
- Webhook;
- Support-Server;
- Telemetrie.

Jede Netzwerkübertragung benötigt einen separaten Decision Gate.

## GUI / CLI

Ein späterer Export muss GUI-/CLI-Parität beachten, sofern er als normale Nutzerfunktion freigegeben wird.

Mögliche Ausnahme:

- diagnostischer CLI-only Export, falls ausdrücklich als Diagnosewerkzeug dokumentiert.

Diese Adapterentscheidung ist noch offen.

## Datenschutzstatus

```text
Diagnose sammeln        🟢 read-only
Redaction               🟢 vorhanden
stdout-Ausgabe          🟢 vorhanden
lokaler Datei-Export    🔒 noch nicht implementiert
Overwrite               🔒 verboten
automatischer Export    🔒 verboten
Netzwerk/Upload         🔒 verboten
Telemetrie              🔒 verboten
```

## Kein Produktcode in I22

I22 ändert nicht:

- `diagnostics.py`;
- `diagnostic_snapshot.py`;
- Read-only-Lock;
- Registry;
- GUI;
- CLI;
- Dateisystem.

## Freigegeben für spätere Planung

Nur:

- explizit initiierter lokaler Export;
- bereits redigierter bestehender Bericht;
- JSON/Klartext;
- explizites vorhandenes Ziel;
- no-overwrite;
- eigener kleiner Writer-Gate.

## Weiter gesperrt

- automatische Exporte;
- Crash-Dumps;
- Upload;
- Netzwerk;
- Telemetrie;
- ZIP/Log-Bundle;
- Rohdatenexport;
- bestehende Datei überschreiben;
- allgemeiner Writer;
- Executor für Nutzerdateien.
