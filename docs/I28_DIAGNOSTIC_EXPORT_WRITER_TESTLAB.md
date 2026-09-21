# I28 – Diagnostic Export Writer Testlab

## Status

**Dedizierter Writer im automatischen Testlabor: PASS. Kein GUI-/CLI-Adapter und keine Registry-Freigabe.**

I28 ist der erste Block, der die von I24/I26/I27 vorbereitete Schreibprimitive tatsächlich implementiert. Der Writer bleibt jedoch ohne Nutzerpfad und kann vom normalen Produktworkflow nicht aufgerufen werden.

## Autorisierungsgrenze

I26 erzeugt weiterhin ausschließlich:

```text
write_enabled = False
overwrite_allowed = False
```

Der I28-Writer verweigert solche Pläne.

Für automatisierte Writer-Tests wird aus einem validierten I26-Plan ausdrücklich eine immutable Test-Autorisierung mit `write_enabled=True` erzeugt. Es existiert weiterhin **kein Produktcode**, der diese Freigabe erzeugt.

## Directory-FD statt Path-Race

I28 verschärft den I27-Vertrag:

1. Zielordner mit `O_DIRECTORY | O_NOFOLLOW` öffnen.
2. Device/Inode von Pfadprüfung und geöffnetem Directory-FD vergleichen.
3. Partial-Datei mit `O_CREAT | O_EXCL | O_RDWR | O_NOFOLLOW` **relativ zu diesem Directory-FD** erzeugen.
4. Payload vollständig schreiben und `fsync`.
5. Größe und SHA-256 aus demselben Partial-FD erneut lesen/verifizieren.
6. Zielordner-Identität vor Publish erneut prüfen.
7. No-clobber-Publish über `os.link(partial_name, final_name, src_dir_fd=..., dst_dir_fd=..., follow_symlinks=False)`.
8. Directory `fsync`.
9. eigene Partial-Datei relativ zum selben Directory-FD entfernen.
10. Directory erneut `fsync`.

Damit hängt der Commit nicht von einer erneut aufgelösten freien Zielpfadkette ab.

## Kein Overwrite

Existiert der finale Name bereits oder entsteht er im Race, gewinnt genau ein Writer. Der andere endet `BLOCKED`. Es gibt:

- kein `rename`;
- kein `replace`;
- kein Auto-Rename;
- kein Retry;
- kein Fallback.

## Partial-Eigentum

Der Partial-Name enthält nur einen zufälligen nicht sensiblen Token:

```text
.PROVOWARE-Diagnose.partial-<random>
```

Er wird exklusiv erzeugt. Behandelte Fehler vor Publish versuchen ausschließlich diese eigene Partial-Datei zu entfernen.

Ein echter Prozessabbruch kann eine Partial-Datei zurücklassen. Sie bleibt bewusst erkennbar und wird nicht als erfolgreicher Export gemeldet.

## Datenschutz

- Datei wird initial mit Modus `0600` erzeugt;
- Writer erhält nur Payload-Bytes + ExportPlan;
- kein DiagnosticReport;
- keine Redaction im Writer;
- kein Netzwerk;
- keine Zusatzsammlung;
- keine Recovery-ID.

## Automatische Failure-Evidence

I28 testet mindestens:

- I26-Plan ohne Schreibfreigabe => BLOCKED;
- erfolgreicher exakter Export;
- private Dateirechte;
- vorhandenes finales Ziel unverändert;
- Payload-Größen-/Hashabweichung;
- manipulierten Finalpfad;
- Symlink-Zielordner;
- Partial-Namenskollision ohne Retry;
- ENOSPC beim Write;
- PermissionError vor Create;
- Crash vor Publish: nur erkennbare Partial-Datei bleibt;
- zwei parallele Writer auf denselben finalen Namen: exakt ein PASS, ein BLOCKED;
- keine produktive Erzeugung von `write_enabled=True`.

## Weiterhin gesperrt

- GUI-/CLI-Export;
- Registry-READY;
- automatische Nutzer-Autorisierung;
- allgemeiner Executor;
- Copy/Move/Trash-Write;
- Overwrite;
- Netzwerk.

## Exit-Gate

I28 ist erst technisch grün, wenn Writer-Tests, I27-Guard, globaler Read-only-Lock, Full Suite, Core Diagnostic und Preflight gemeinsam PASS sind.
