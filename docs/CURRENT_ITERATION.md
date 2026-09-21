# PROVOWARE – Current Iteration

## I35 – Portable Artifact Provenance Binding

**Status:** 🟢 AUTO PASS · FREEZE-BEREIT
**Fortschritt:** `██████████ 100 %`

## A – PLAN

I32/I33 werden um eine fail-closed Bindung von Git-Commit, Manifest, Paketwurzel, ZIP-Dateiname und Checksum-Sidecar ergänzt.

## B – DELTA

NONE. I25/I31 Human-Gates und B01-Zweitgerät bleiben gesammelt offen.

## Implementiert

- Builder akzeptiert nur exakten 40-stelligen Git-SHA;
- Paketwurzel wird gegen Manifest-Commit/Plattform geprüft;
- ZIP-Dateiname wird gegen dieselbe Provenienz geprüft;
- `.zip.sha256` bindet tatsächliche ZIP-Bytes und exakten Dateinamen;
- Offline-Wheelhouse bleibt auf `linux-x86_64` begrenzt;
- Manipulations-/Rename-/Checksum-Tests;
- echter Portable-Package-CI-Lauf prüft Sidecar automatisch.

## Sicherheitsgrenze

Keine Signatur-/Authentizitätsbehauptung. ZIP und Sidecar gemeinsam austauschbar zu schützen ist ein separater kryptografischer Trust-Block.

## Exit-Gates

1. I35 targeted tests PASS.
2. I32/I33 Paketregression PASS.
3. echter Offline-Paketlauf PASS.
4. Sidecar-Prüfung im CI PASS.
5. Full Repository Gate PASS.
6. GUI-Cross-Regressionsgates PASS, soweit ausgelöst.

## AUTO-Ergebnis

Commit-/Manifest-/Paketwurzel-/ZIP-Name-/Sidecar-Bindung und echter Offline-Bootstrap sind vollständig grün.

## Nächste drei Schritte

1. 🟢 I35 Evidence an RC `98920d7af0d16c986c26742e859ca6f41fa18fed` binden und mergen.
2. 🔵 danach verbleibende rein automatische Status-/Release-Sicherheitsarbeit priorisieren.
3. 🔒 I25/I31 Human-Gates und B01-Zweitgerät weiterhin gesammelt offen halten.
