# EV-20260921-006 – Branch-Hygiene und I27-Transplant

## Evidence-ID

EV-20260921-006

## Datum/Uhrzeit

2026-09-21 · Europe/Berlin

## Commit/Fingerprint

Basis vor dem I27-RC: `e01f23b6937becfd26d09cb7ea74020896e29281`.

## Ziel

Altbranches klassifizieren, einzigartige Sicherheitsinvarianten retten und I27 nicht blind aus einem alten Branch mergen.

## Branch-Klassifikation

| Branch | Befund | Entscheidung |
| --- | --- | --- |
| `design/i24-diagnostic-export-writer` | 0 einzigartige Commits, nur hinter `main` | vollständig superseded; Löschkandidat |
| `application/i21-transfer-preview` | 2 alte einzigartige Commits mit früher Transfer-Implementierung/Tests | durch I21 + `transfer_application.py` superseded; relevante Sicherheitsfälle auf Main; Löschkandidat |
| `domain/i12-preview-contract` | 7 alte einzigartige Commits mit früherem Preview-Modell | Architektur superseded; MOVE-Reversibilitätsinvariante gerettet; danach Löschkandidat |
| `security/i27-diagnostic-writer-guard` | 1 einzigartiger Sicherheitsblock, aber alter Main und Guard-Lücken | nicht mergen; gehärtet auf frischem Main transplantieren; alter Branch danach Löschkandidat |

## I21-Abgleich

Alte Tests zu Copy/Move read-only, Unicode, leerer/doppelter/fehlender Auswahl, vorhandenem Ziel, externer Wurzel, Symlink-Ziel und Quelle=Ziel sind im aktuellen I21/I25-Regressionspfad abgedeckt.

## I12-Abgleich

Der alte Vertrag verlangte MOVE- und TRASH-Reversibilität. Aktuell war nur TRASH zentral erzwungen. I21 erzeugte MOVE bereits reversibel; die zentrale Preview-Prüfung wird jetzt ebenfalls fail-closed.

## I27-Abgleich

Gefundene Altguard-Lücken:

- dynamische `os.open`-Flags;
- numerische Rohflags;
- fehlende FD-Provenienz für `os.write`;
- zu schwache `os.link`-Rollenprüfung;
- fehlende Blockade mehrerer Escape-/Low-Level-Writer.

Diese Punkte werden im neuen I27-Vertrag geschlossen.

## Status

**RC-IMPLEMENTATION PREPARED** – finaler PASS erst nach vollständigem Repository-/Guard-/Test-Gate.

## Bekannte Grenze

Die verfügbare GitHub-Integration bietet hier keine Branch-Delete-Aktion. Die Altbranches werden daher nicht destruktiv umgeschrieben; die Löschentscheidung ist reproduzierbar dokumentiert.
