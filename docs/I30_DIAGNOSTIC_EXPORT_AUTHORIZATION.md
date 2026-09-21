# I30 – Diagnose-Export Application-Autorisierung

## Status

**Nichtvisueller Autorisierungs-Core implementiert. Registry-Eintrag bleibt OPEN. Keine GUI-/CLI-Funktion.**

## Ablauf

```text
I26 ExportPreparation
→ preparation_fingerprint()
→ Confirmation Stage 1
→ Confirmation Stage 2
→ AuthorizedExportRequest
→ one-shot execute()
→ intern write_enabled=True
→ I28 Writer
```

## Fingerprint

Gebunden werden:

- finaler Zielpfad;
- Exportformat;
- Payload-Größe;
- Payload-SHA-256;
- `overwrite_allowed=False`.

Zusätzlich wird vor Fingerprint-Bildung geprüft, dass die tatsächlichen Payload-Bytes noch exakt zu Größe und SHA-256 im Plan passen und `write_enabled=False` ist.

## Sitzungsmodell

`DiagnosticExportAuthorizationSession` ist bewusst nur prozesslokal.

- kein Persistenzspeicher;
- kein KeyStore;
- kein wiederverwendbares globales Token;
- eine Sitzung gilt nur für exakt eine I26-Vorbereitung;
- Cancel sperrt die Sitzung;
- Stage 2 ohne Stage 1 ist blockiert;
- Änderung nach Stage 1 setzt den Ablauf auf Anfang zurück;
- eine ausgegebene Anfrage gehört durch `session_id` nur zu dieser Sitzung;
- der Writer-Aufruf ist one-shot.

## Replay-Schutz

Die Sitzung wird **vor** dem Writer-Aufruf als verbraucht markiert. Auch wenn ein späterer Writerfehler auftreten sollte, kann dieselbe Autorisierung dadurch nicht automatisch erneut ausgeführt werden.

Ein zweiter `execute()`-Aufruf endet `BLOCKED_REPLAY`.

## Registry

Neue Sicherheitsklasse:

`explicit-write-confirmation`

Neuer Eintrag:

`diagnostics.export_local`

Status:

`OPEN`

GUI und CLI bleiben beide `False`, bis ein späterer Adapterblock beide Seiten implementiert.

## Automatische Tests

- Registry-Vertrag;
- stabile Fingerprints;
- Payload-Manipulation;
- falsche Reihenfolge;
- Stale Plan nach Stage 1;
- Cancel vor Stage 1;
- Cancel nach Stage 1;
- Stage-2 Request;
- Writer exakt einmal;
- Replay;
- fremde Sitzung;
- manipulierter Request;
- bereits write-enabled Plan wird abgelehnt.

## Nicht-Ziele

- kein GUI-Button;
- kein CLI-Menü;
- kein Startmodus;
- kein READY;
- keine reale Nutzerdatei;
- keine Persistenz;
- kein allgemeiner Executor;
- keine Änderung am I28 No-clobber-Writer.

## Folgeblock

Ein späterer I31 darf GUI-/CLI-Adapter zunächst als gegateten Prüfmodus implementieren. Vor READY bleiben Auto-Evidence und eine einzige Human-Gesamtabnahme des sichtbaren Schreibworkflows Pflicht.
