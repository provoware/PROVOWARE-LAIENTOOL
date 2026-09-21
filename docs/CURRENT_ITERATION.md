# PROVOWARE – Current Iteration

## I33 – Offline-Wheelhouse Supply-Chain-Lock

**Status:** 🟨 RC · AUTOMATISCHE GATES LAUFEN
**Fortschritt:** `████████░░ 80 %`

## A – PLAN

I33 härtet den I32-Paketpfad gegen unerwartete Wheel-Dateien:

- committed Lock für Linux x86_64;
- exakte vier Wheel-Dateien;
- exakte Größen + SHA-256;
- Requirements-Fingerprint;
- Prüfung vor Paketbuild;
- Prüfung im extrahierten Paket;
- Prüfung in `start.sh` vor lokaler Installation.

## B – DELTA

I32 zeigte, dass Paketmanifest und Source-Head sauber reproduzierbar sind. Die verbleibende Supply-Chain-Lücke lag **vor** dem Manifest: der Download selbst war noch nicht gegen eine vorab bekannte Hashbaseline gebunden.

## Sicherheitsgrenze

- kein Lock-Autoupdate;
- kein Netzwerk-Fallback bei Lockfehler;
- kein Installieren unbekannter Extra-Wheels;
- keine Produkt-READY-Änderung;
- B01/I25/I31 bleiben geparkt.

## Exit-Gates

1. Lock-Schema/Requirements-Fingerprint.
2. exakte Wheel-Dateiliste.
3. Größenprüfung.
4. SHA-256-Prüfung.
5. Missing/Extra/Tamper fail-closed.
6. CI prüft Lock vor ZIP-Build.
7. Paketvalidator prüft Lock nach Extraktion.
8. start.sh prüft Lock vor pip.
9. Portable-Package Offline-Bootstrap PASS.
10. Full Suite / GUI-Cross-Regressions PASS.

## Nächste drei Schritte

1. 🟨 I33 vollständig automatisch prüfen.
2. 🔵 bei Grün Evidence binden und mergen.
3. 🔒 danach nächsten automatisierbaren Datenschutz-/Release-Vertrag bearbeiten; Human-Gates weiter bündeln.
