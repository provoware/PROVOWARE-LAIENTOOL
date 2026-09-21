# PROVOWARE – Current Iteration

## I32 – Portable Offline-Paketierung

**Status:** 🟨 RC · AUTOMATISCHE GATES LAUFEN
**Fortschritt:** `████████░░ 80 %`

## A – PLAN

B07 wird als reproduzierbares Linux-x86_64-Portable-Paket umgesetzt:

- deterministisches ZIP;
- lokales Wheelhouse für PySide6;
- Offline-first Installation via `start.sh`;
- Desktop-Klickstarter delegiert ausschließlich an `start.sh --gui`;
- Manifest + SHA-256;
- Fremdpfad mit Unicode/Leerzeichen;
- Offline-Bootstrap-Test.

## B – DELTA

Aus I31 entstand kein blockierender Produktfehler. B = **NONE**. Die I31-Human-Abnahme bleibt bewusst geparkt.

## Sicherheitsgrenze

- keine Produkt-READY-Änderung;
- kein neuer Fach-Write;
- keine Systeminstallation im Nutzerstarter;
- keine stille Paketinstallation;
- Wheelhouse vorhanden → strikt `--no-index`;
- physische Zweitgeräte-Evidence bleibt OPEN.

## Exit-Gates

1. Paketbuilder deterministisch.
2. Manifest/Hashes exakt.
3. ZIP ohne Dev-/lokale Laufzeitreste.
4. Desktop-Launcher → `start.sh --gui`.
5. reales gepinntes PySide6-Wheelhouse im CI.
6. Extraktion in Unicode-/Leerzeichen-Fremdpfad.
7. Offline-`--setup` ohne Index.
8. `start.sh --check` im extrahierten Paket.
9. Full Suite / Read-only-Lock / Core Diagnostic / Preflight.
10. Paketartefakt + Validierungsbericht.

## Weiter offen

- reales zweites Gerät;
- ARM;
- Desktop-Dateimanager-Vertrauensdialog;
- I25/I31 Human-Gates.

## Nächste drei Schritte

1. 🟨 I32 RC vollständig automatisch prüfen.
2. 🔵 bei Grün Evidence binden und mergen.
3. 🔒 danach nächsten rein automatisierbaren Block wählen; Human-Gates weiter bündeln.
