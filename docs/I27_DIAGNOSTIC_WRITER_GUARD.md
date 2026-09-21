# I27 – Diagnostic Writer Guard / No-Clobber Gate

## Status

**Hardened writer-spezifischer Guard implementiert. Noch kein Writer.**

I27 öffnet keinen produktiven Export und erzeugt keine Datei. Der Block schafft ausschließlich die statische Sicherheitsgrenze, die I24 und I26 vor einem späteren `diagnostic_export.py` verlangen.

## Warum der alte I27-Branch nicht gemergt wird

Der historische Branch `security/i27-diagnostic-writer-guard` enthielt die richtige Grundidee, war aber auf altem Main und besaß statische Fail-open-Kanten:

- dynamische bzw. numerische `os.open`-Flags waren nicht sicher blockiert;
- `os.write` war nicht an einen nachweislich exklusiv erzeugten Partial-FD gebunden;
- `os.link` verlangte nicht streng `partial_path → final_path`;
- mehrere indirekte Low-Level-/Escape-APIs waren nicht explizit ausgeschlossen.

I27 wird deshalb auf frischem `main` gehärtet transplantiert.

## Exakte REOPEN-Grenze

Nur `src/provoware_laientool/diagnostic_export.py` darf künftig an den Spezialguard delegiert werden. Keine Wildcards, kein Verzeichnis-Reopen, kein zweites Writer-Modul.

Alle übrigen Produktmodule bleiben unter dem allgemeinen Read-only-Lock. Dieser blockiert zusätzlich Low-Level-Primitiven wie `os.open`, `os.write`, `os.link`, `os.pwrite`, `os.writev`, `os.creat`, `os.truncate`, `os.mknod` und verwandte APIs.

## Erlaubtes Create-Primitiv

Schreibendes `os.open` ist nur zulässig, wenn statisch beweisbar:

- expliziter `partial_path`;
- `O_CREAT`;
- `O_EXCL`;
- genau `O_WRONLY` oder `O_RDWR`;
- optional `O_CLOEXEC` / `O_NOFOLLOW`;
- kein `O_TRUNC`, `O_APPEND`, `O_TMPFILE`;
- keine dynamischen oder numerischen Rohflags;
- I28 darf relative Partial-Operationen ausschließlich über einen statisch belegten `target_dir_fd` aus `O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW` ausführen.

Nicht vollständig statisch belegbar => **BLOCKED**.

## FD-Provenienz

`os.write(fd, ...)` ist nur zulässig, wenn `fd` direkt aus einem statisch freigegebenen exklusiven `os.open(partial_path, ...)` stammt.

## No-Clobber Publish

Ein späterer Publish darf ausschließlich diesem Vertrag folgen:

```text
os.link(partial_path, final_path, follow_symlinks=False)
```

Seit I28 ist die noch engere Form zulässig: Quelle `partial_name` und Ziel `final_name` müssen relativ zum **gleichen**, statisch belegten `target_dir_fd` veröffentlicht werden. Beliebige oder unterschiedliche `*_dir_fd`, `rename`, `replace` und freie Hardlinks bleiben blockiert.

## Löschgrenze

`os.unlink()` ist ausschließlich für `partial_name`/`partial_path` und – im I28-Writer – relativ zum belegten `target_dir_fd` zulässig. Finale Pfade und freie Löschpfade bleiben blockiert.

## Escape-Härtung

Im Spezialwriter bleiben unter anderem Netzwerk, `subprocess`, `tempfile`, `ctypes`, `mmap`, `shutil`, alternative Datei-Writer, Archive/Kompression, dynamisches `eval/exec/__import__` sowie indirekte Low-Level-Writer gesperrt.

## Gerettete Preview-Invariante

Der überholte Branch `domain/i12-preview-contract` enthielt noch die sinnvolle Invariante: **MOVE und TRASH müssen reversibel geplant sein.**

Der aktuelle I21-Erzeuger markierte MOVE bereits korrekt; I27-Hygiene stellt zusätzlich die zentrale Domain-Prüfung wieder fail-closed her.

## Nicht-Ziele

- kein `diagnostic_export.py`;
- kein produktiver Dateisystem-Write;
- kein Export-Adapter;
- kein Registry-READY;
- kein Race-/ENOSPC-/PermissionError-Lauf;
- keine Freigabe für andere Produktmodule.

## Nächster autonomer Block

Erst nach grünem I27 darf ein dedizierter Writer als separater Testlab-Block entstehen. Pflicht: Race, Ziel entsteht nach Preflight, Crash nach Partial-Create/Write, ENOSPC, PermissionError, Hash-/Größenabweichung, Partial-Ownership und erfolgreicher No-clobber-Publish.
