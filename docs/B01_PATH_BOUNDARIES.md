# B01-B – Pfad- und Symlink-Sicherheitsmodell

**Status:** read-only Sicherheitskern implementiert
**Bezug:** REQ-001; AQ-003, AQ-004

## Ziel

Jede spätere Dateioperation muss an eine explizit freigegebene Wurzel gebunden sein. Pfade, Dateinamen, Unicode, Leerzeichen, Symlinks und Traversal gelten als nicht vertrauenswürdig.

## Verbindliche Regeln

1. Die freigegebene Wurzel muss existieren und sicher auflösbar sein.
2. Kandidaten werden gegen die **aufgelöste** Wurzel geprüft.
3. `..` und absolute Pfade dürfen die Wurzel nicht verlassen.
4. Symlinks sind standardmäßig gesperrt.
5. Auch bei explizit erlaubtem Symlink-Modus darf das aufgelöste Ziel die Wurzel niemals verlassen.
6. Defekte Symlinks und nicht auflösbare Pfade werden fail-closed abgelehnt.
7. Unicode und Leerzeichen sind erlaubt, solange die Sicherheitsgrenze eingehalten wird.
8. Fehlende Ziele sind standardmäßig gesperrt. Nur reine Planungs-/Preview-Fälle dürfen mit `must_exist=False` geprüft werden.
9. Die Validierung selbst ist read-only.

## API

`validate_existing_root(root)` validiert eine explizit gewählte Wurzel.

`validate_path(root, candidate, allow_symlink=False, must_exist=True)` liefert eine immutable `PathDecision`.

## Nicht-Ziele

- kein rekursiver Dateiscan;
- kein Verschieben/Kopieren/Löschen;
- kein TOCTOU-Schutz für spätere Schreiboperationen;
- keine Mount-/Device-Policy;
- keine Rechteänderung.

## Exit-Gate

- Traversal nach außen blockiert;
- absolute Außenpfade blockiert;
- Symlink nach außen blockiert;
- Symlink standardmäßig blockiert;
- defekter Symlink blockiert;
- Unicode/Leerzeichen innerhalb der Wurzel erlaubt;
- fehlende Pfade bleiben ohne expliziten Planungsmodus gesperrt.
