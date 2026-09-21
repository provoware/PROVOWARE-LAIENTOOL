# I19 – Preview-Zielwahl Decision Gate

## Status

**Entscheidung dokumentiert. Keine Produktimplementierung. Kein Executor.**

## Problem

I12 kann Copy/Move bereits als Preview modellieren, verwendet aber genau eine freigegebene `root` für Quelle und Ziel.

Eine vorschnelle freie Zielordnerwahl würde mehrere neue Sicherheitsfragen gleichzeitig öffnen:

- zweite Vertrauenswurzel;
- Cross-Device-Move;
- Zielkollisionen/Overwrite;
- freier Speicher;
- Recovery über Dateisystemgrenzen;
- TOCTOU zwischen Preview und Ausführung.

I19 entscheidet deshalb bewusst den kleinsten sicheren ersten Zielwahlvertrag.

## Entscheidung

### Initialer freigegebener Zielraum

Für die **erste** Copy-/Move-Preview gilt:

> Quelle und Ziel müssen innerhalb derselben explizit gewählten und B01-validierten Wurzel liegen.

Beispiel:

```text
Downloads/
├── unsortiert/datei.pdf     ← Quelle
└── Dokumente/datei.pdf      ← mögliches Ziel
```

Nicht freigegeben:

```text
Downloads/datei.pdf
→ /media/USB/datei.pdf
```

Eine zweite Zielwurzel / externe Datenträger bleiben bis zu einem späteren Multi-Root-Vertrag BLOCKED.

## Warum diese Entscheidung

- passt zum bestehenden I12-`PreviewPlan.root`;
- benötigt keinen heimlichen Schema-/Domain-Reopen;
- verhindert Cross-Device-Sonderfälle;
- nutzt den bestehenden B01-Pfadvertrag unverändert;
- reicht für den Kernfall „Downloads in Unterordner organisieren“;
- reduziert spätere Executor-Komplexität deutlich.

## Zielauswahl

Die spätere Oberfläche darf ein Ziel **nicht automatisch erfinden**.

Der Nutzer wählt ausdrücklich einen Zielordner innerhalb der freigegebenen Wurzel.

GUI:

- Ordnerauswahl auf die freigegebene Wurzel begrenzen;
- Wirkung vor jeder späteren Schreibfreigabe anzeigen.

CLI:

- laienfreundliche nummerierte Zielauswahl;
- optional explizite Pfadeingabe nur innerhalb der Wurzel;
- gleicher Application-/Domain-Core.

## Zielpfadbildung

Für eine Quelldatei:

```text
source = <root>/<relative-source>
target_dir = explizit gewählter Unterordner in <root>
target = <target_dir>/<source.name>
```

Der Dateiname wird im ersten Vertrag nicht automatisch verändert.

## Kollisionen

### Default

**Existiert das Ziel bereits, wird geblockt.**

Kein:

- Überschreiben;
- stilles Ersetzen;
- automatisches Zusammenführen;
- `(1)`-/`copy`-Suffix ohne ausdrücklichen späteren Vertrag.

Begründung: Konfliktbehandlung ist eine eigene Nutzerentscheidung und darf nicht in der Zielwahl versteckt werden.

## Quelle = Ziel

Weiterhin BLOCKED.

Auch logisch identische aufgelöste Pfade müssen abgelehnt werden.

## Symlinks

Zielordner und Zielpfad bleiben im initialen Vertrag symlink-frei.

Keine Ausnahme gegenüber B01.

## Fehlendes Ziel

Der konkrete Zieldateipfad darf bei reiner Preview noch fehlen.

Der **Zielordner** muss dagegen vor einer späteren Ausführung existent, sicher auflösbar und innerhalb der Wurzel liegen.

I12 `must_exist=False` für den geplanten Zieldateipfad bleibt damit sinnvoll.

## Reversibilität

### Copy

Recovery-Vertrag:

`remove-created-copy`

Voraussetzung für späteren Executor:

- Ziel existierte vor Ausführung nicht;
- nach Copy muss die erzeugte Datei eindeutig der Aktion zuordenbar sein.

### Move

Recovery-Vertrag:

`move-back`

Für die erste Ausführung darf Move nur innerhalb derselben Wurzel / des unterstützten Dateisystemvertrags freigegeben werden.

Cross-Device-Move bleibt BLOCKED.

## Overwrite

**Kein Overwrite im ersten Executor-Vertrag.**

Damit wird vermieden:

- Sicherung eines verdrängten Zielinhalts;
- doppelte Recovery-Semantik;
- unklare Undo-Reihenfolge;
- Datenverlust durch falsche Konfliktentscheidung.

## TOCTOU

I19 gibt **keinen** TOCTOU-Schutz frei.

Vor einem späteren Executor muss unmittelbar vor dem Schreibzugriff erneut geprüft werden:

- Quelle existiert noch und entspricht dem erwarteten Objekt;
- Zielordner ist weiterhin innerhalb der freigegebenen Wurzel;
- Ziel existiert weiterhin nicht;
- keine relevante Symlink-/Pfadänderung ist eingetreten;
- Schreibfähigkeit/Freiraum sind ausreichend.

Preview-PASS allein ist niemals Executor-PASS.

## Freier Speicher

Vor Copy und vor Move-Implementierungen, die temporär zusätzlichen Speicher benötigen, ist eine Kapazitätsprüfung Pflicht.

Keine Freigabe in I19; nur Executor-Voraussetzung.

## Berechtigungen

Preview darf read-only bleiben.

Schreibberechtigung wird erst im späteren Executor-Gate geprüft und darf keine automatische Rechteausweitung auslösen.

## Multi-Root / externe Datenträger

Noch nicht unterstützt.

Ein späterer Vertrag müsste mindestens getrennt modellieren:

- `source_root`;
- `target_root`;
- Device-/Mount-Identität;
- Cross-Device-Move-Semantik;
- Kapazität;
- Recovery über beide Wurzeln.

Bis dahin bleiben externe Copy-/Move-Ziele BLOCKED.

## Architekturentscheidung

```text
I15 Inventory
    ↓
I18 Auswahl/Ansicht
    ↓
I19 expliziter Zielordner innerhalb derselben root
    ↓
I12 PreviewItem(copy|move)
    ↓
validate_preview()
    ↓
I13 RecoveryContract
    ↓
🔒 STOP – noch kein Executor
```

## Erforderliche spätere Application-Funktion

Noch nicht implementiert, aber fachlich vorgegeben:

```text
prepare_copy_preview(root, selected_items, target_dir)
prepare_move_preview(root, selected_items, target_dir)
```

Beide müssen denselben Core für GUI und CLI verwenden.

## Exit-Entscheidung

### Freigegeben für nächste Planung

- explizite Zielordnerwahl;
- nur innerhalb derselben Root;
- Copy-/Move-Preview;
- kein Overwrite;
- kein Symlink;
- gleiche Core-Logik GUI/CLI.

### Weiter gesperrt

- Executor;
- externe Zielwurzeln;
- Cross-Device-Move;
- Overwrite;
- Auto-Rename bei Konflikt;
- automatische Zielwahl;
- Persistenz/Journal-Writer;
- Rechteausweitung.

## Kein REOPEN notwendig

Für den initialen Same-Root-Zielvertrag ist aktuell **kein I12-Schema-Reopen erforderlich**.

Ein Multi-Root-Zielvertrag würde dagegen ausdrücklich einen neuen Domain-/Preview-Entscheidungsschritt benötigen.
