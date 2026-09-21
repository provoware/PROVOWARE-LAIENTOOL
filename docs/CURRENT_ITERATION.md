# PROVOWARE – Current Iteration
## I32 – Portable ZIP / Fremdpfad / Offline-Paketvertrag
**Status:** 🟨 RC · AUTOMATISCHE GATES LAUFEN
**Fortschritt:** `████████░░ 80 %`

**A – PLAN:** B07 erhält eine reproduzierbare Portable-Source-ZIP-Form.  
**B – DELTA:** NONE; I31-HUMAN bleibt bewusst geparkt.

Implementiert: deterministischer ZIP-Builder, Manifest/Hashes, `start.sh` als kanonischer Einstieg, Desktop-Klickoberfläche als reine Delegation, Fremdpfad/Unicode, Offline-Hilfe, fail-closed `--check`, eigener CI-Paketgate.

Nicht behauptet wird eine frische vollständig offline einrichtbare GUI; PySide6 wird nicht gebündelt.

## Exit-Gates
1. zwei Builds byte-identisch;
2. Manifest/Hashes PASS;
3. keine Venv/Git/Buildreste;
4. Fremdpfad PASS;
5. Offline-Hilfe PASS;
6. Offline-Check ohne Mutation;
7. Full Gate PASS;
8. ZIP-CI-Artefakt vorhanden.

## Nächste drei Schritte
1. I32 automatisch prüfen und Evidence binden.
2. Bei Grün mergen.
3. I33 Offline-Dependency-Bundle-Decision rein automatisch durchführen.
