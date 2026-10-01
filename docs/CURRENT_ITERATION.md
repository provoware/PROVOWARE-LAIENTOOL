# PROVOWARE – Aktueller Arbeitsblock

## I45 – I25 technische Transfer-Prüfung

**Status:** 🟨 TEILWEISE BESTANDEN

**Fortschritt:** `████████░░ 75 %` (3 von 4 definierten Gates bestanden)

**Produktfreigabe:** unverändert; Copy/Move bleibt nicht READY

## Ziel

Die fehlende Qt-Laufzeitkomponente begrenzt bereitstellen, die Qt-Validierung
genau einmal wiederholen und danach die technische I25-Prüfung ausführen.

## Definierte Gates

1. **PASS – Qt-Paket:** `libegl1` und seine zwingenden Abhängigkeiten wurden
   distributionsgerecht installiert.
2. **PASS – Qt-Validierung:** `./start.sh --setup` meldete PySide6 6.11.2,
   Qt 6.11.2 und einen erfolgreichen QtWidgets-Import.
3. **PASS – I25-AUTO:** `./start.sh --i25-offscreen` bestand; Bericht,
   Auswertung, JSON und sieben Screenshots wurden unabhängig per SHA-256
   verifiziert.
4. **OPEN – I25-HUMAN:** `./start.sh --i25-evidence` benötigt weiterhin eine
   echte menschliche Wahrnehmungsentscheidung.

## Ergebnis und Abgrenzung

Die Qt-Laufzeit ist in dieser Prüfumgebung vollständig nutzbar. Der technische
I25-Lauf bestätigt die automatisierten Prüfungen für 100, 150 und 200 Prozent,
Tastaturfokus, Auswahl- und Zieldialoge sowie die read-only Transfer-Vorschau.
Die Artefakte sind an den geprüften Commit gebunden und ihre Hashes sind in
`docs/evidence/EV-20261001-017-i45-i25-auto-pass.md` festgehalten.

I25-AUTO ist damit **PASS**. I25-HUMAN bleibt **OPEN**; deshalb bleiben auch
I25 insgesamt und die Copy-/Move-Freigabe **OPEN**. Es wurde kein menschliches
PASS angenommen und kein Registry-Eintrag auf READY gesetzt.

## Nächster verbindlicher Schritt

Genau einen echten Lauf von `./start.sh --i25-evidence` durchführen und die
Wahrnehmbarkeit sowie Verständlichkeit durch einen Menschen beurteilen lassen.

### Drei-Schritte-Vorausplanung

1. **I25 menschlich prüfen:** I25-AUTO-PASS ist erfüllt; Gate ist genau ein
   echter Lauf von `./start.sh --i25-evidence` mit dokumentierter
   Wahrnehmungsentscheidung.
2. **I25-Freigabe entscheiden:** HUMAN-PASS ist erforderlich; Scope sind nur
   die betroffenen Registry- und Freeze-Texte, Gate ist ein gezielter
   Registry-/Repository-Test.
3. **Verbleibende Release-Gates prüfen:** I25-Abschluss ist erforderlich;
   Scope sind die bereits offenen Human- und Zweitgeräte-Nachweise, Gate ist
   eine konsistente Release-Checkliste ohne unbelegtes PASS.
