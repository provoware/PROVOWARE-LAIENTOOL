# PROVOWARE – Current Iteration

## I28 – Diagnostic Export Writer Testlab

**Status:** 🟢 AUTOMATISCH PASS · KEIN NUTZERPFAD
**Fortschritt:** `██████████ 100 %`

## A – FESTER PLAN

I24/I26/I27 sind erfüllt:

- Writer-Architektur und No-overwrite-Vertrag festgelegt;
- redigierter Payload + immutable ExportPlan vollständig read-only vorbereitet;
- exakter Spezialguard nur für `diagnostic_export.py`;
- alle anderen Produktmodule bleiben write-locked.

I28 implementiert erstmals den dedizierten Writer, aber ausschließlich als Testlab-Baustein. Es gibt weiterhin keinen GUI-/CLI-Adapter, keine Registry-Freigabe und keine automatische Schreibautorisierung.

## Directory-FD-Härtung

Der Writer hält den validierten Zielordner über einen `target_dir_fd` offen:

```text
target_dir
→ O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW
→ Device/Inode gegen Pfadprüfung bestätigen
→ partial_name exklusiv relativ zu target_dir_fd erzeugen
→ schreiben + fsync
→ über denselben FD Größe/Hash verifizieren
→ Zielordneridentität erneut prüfen
→ hardlink partial_name → final_name über denselben target_dir_fd
→ directory fsync
→ eigene Partial-Datei entfernen
→ directory fsync
```

Dadurch werden Partial-Create, Publish und Cleanup nicht über eine zwischenzeitlich neu aufgelöste freie Pfadkette verbunden.

## Autorisierungsgrenze

I26 erzeugt weiterhin `write_enabled=False`.

Der Writer verweigert solche Pläne. Nur die automatisierten I28-Tests erzeugen über `dataclasses.replace(..., write_enabled=True)` eine explizite Testautorisierung.

Im Produkt existiert kein Pfad, der `write_enabled=True` erzeugt.

## Automatische Failure-Matrix

- I26-Plan ohne Autorisierung → BLOCKED;
- erfolgreicher Export;
- private Dateirechte;
- vorhandenes finales Ziel unverändert;
- falsche Payload-Größe / falscher Hash;
- manipulierte Finalpfadbindung;
- Symlink-Zielordner;
- Partial-Kollision ohne Retry;
- ENOSPC;
- PermissionError;
- Crash vor Publish hinterlässt nur erkennbare Partial-Datei;
- zwei parallele Writer: exakt ein PASS, ein BLOCKED;
- keine produktive Erzeugung von `write_enabled=True`.

## Weiterhin gesperrt

- GUI-/CLI-Diagnoseexport;
- Registry-READY;
- Nutzer-Autorisierung;
- allgemeiner Executor;
- Copy/Move/Trash-Write;
- Overwrite;
- Auto-Rename;
- Netzwerk;
- I25 READY ohne finale Human-Abnahme.

## Exit-Gates

1. I28 Writer-Tests PASS.
2. I27 Writer-Guard PASS.
3. globaler Read-only-Lock PASS.
4. vollständige Unit-/Integrationssuite PASS.
5. Repository-Contract PASS.
6. Core Diagnostic PASS.
7. Diagnose/Preflight PASS.
8. kein GUI-/CLI-/Registry-Pfad zum Writer.
9. finaler Diff ohne breiten Write-Reopen.
10. Post-Merge-Main-Gate PASS.

## Nächste drei Schritte

1. 🟢 I28 automatisiert grün einfrieren; Writer bleibt ohne Nutzerpfad.
2. 🔵 nach grünem I28 eine getrennte Autorisierungs-/Adapter-Decision treffen; kein automatisches Aktivieren des Writers.
3. 🔒 I25-Human-Gate bleibt unabhängig offen und erzeugt keine Zwischenarbeit.
