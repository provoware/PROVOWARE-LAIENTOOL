# PROVOWARE – Current Iteration

## I32 – Portable Offline-Paketierung

**Status:** 🟢 AUTO PASS · CI-LINUX-X86_64
**Fortschritt:** `██████████ 100 %`

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

## AUTO-Ergebnis

Der Portable-Package-Gate ist auf dem exakten Source-Head `bfee18f528e6a06feb9b3b43d1da9575578f2e89` vollständig grün.

## Nächste drei Schritte

1. 🟢 I32 Evidence an `bfee18f528e6a06feb9b3b43d1da9575578f2e89` binden und mergen.
2. 🔵 danach den nächsten rein automatisierbaren Release-/Sicherheitsblock wählen.
3. 🔒 B01-Zweitgerät sowie I25/I31 Human-Gates weiter gesammelt offen halten; keine Einzeltestserie starten.
