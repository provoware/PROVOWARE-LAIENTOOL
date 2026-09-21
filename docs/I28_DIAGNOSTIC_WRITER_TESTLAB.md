# I28 – Diagnose-Export Writer Testlab

## Status

**Dedizierter Writer implementiert – ausschließlich als noch nicht angebundener Testlab-Baustein.**

Kein GUI-/CLI-Adapter, kein Registry-Use-Case und kein allgemeiner Executor.

## Vertrag

Der Writer akzeptiert nur bereits serialisierte Bytes und einen validierten `ExportPlan`. I26 erzeugt weiterhin `write_enabled=False`; ohne explizit autorisierten immutable Plan schreibt I28 nichts.

## Write-Protokoll

```text
Runtime-Vertrag erneut prüfen
→ Payload-Größe + SHA-256 prüfen
→ Partial O_CREAT|O_EXCL|O_WRONLY
→ Write + fsync
→ Partial Größe/Hash erneut prüfen
→ os.link(partial_path, final_path, follow_symlinks=False)
→ Directory-fsync
→ eigene Partial-Datei unlink
→ Directory-fsync
→ PASS
```

Kein `rename`, kein `replace`, kein Overwrite-Fallback, kein automatischer Retry.

## Automatische Failure-Matrix

- Autorisierung fehlt;
- JSON/Text;
- Unicode/Leerzeichen;
- vorhandenes Ziel;
- Hash-/Größenabweichung;
- Symlink-Ziel;
- ENOSPC;
- PermissionError;
- Ziel entsteht direkt vor Commit;
- paralleler gleicher Zielname;
- Crash nach Partial-Create;
- Crash vor Commit;
- Partial-Namenskollision;
- Cleanup-Fehler nach Publish;
- I27-Guard + globaler Read-only-Lock.

## Sicherheitsgrenze

I28 macht den Writer technisch testbar, aber **nicht produktiv erreichbar**. Ein späterer Nutzerexport braucht einen separaten Autorisierungs-/Adapterblock.
