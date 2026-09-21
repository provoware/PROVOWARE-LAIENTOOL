# PROVOWARE LAIENTOOL – Theme-Tokens

**Status:** Design-Tokens, noch keine produktive Implementierung.

## Semantische Token-Namen

| Token | Bedeutung |
| --- | --- |
| `bg.canvas` | äußerster Hintergrund |
| `bg.surface` | Standard-Panel |
| `bg.surfaceRaised` | hervorgehobene Card |
| `bg.input` | Eingabefläche |
| `text.primary` | Haupttext |
| `text.secondary` | Hilfs-/Metatext |
| `border.default` | Standardrahmen |
| `accent.primary` | Hauptakzent |
| `accent.secondary` | zweiter Akzent |
| `contrast.one` | Kontrastfarbe 1 |
| `contrast.two` | Kontrastfarbe 2 |
| `state.success` | Erfolg |
| `state.warning` | Warnung |
| `state.error` | Fehler |
| `state.info` | Information |
| `focus.ring` | Tastaturfokus |
| `workflow.active` | aktiver Workflow-Schritt |
| `workflow.done` | abgeschlossener Workflow-Schritt |

## Theme-Familien

**Purple Neon:** Navy/Anthrazit + Lila + elektrisches Blau + Cyan + Grün.
**Turquoise Neon:** Petrol + Türkis + Cyanblau + Violett + Amber/Orange.
**Graphite Electric:** Graphit + elektrisches Blau + Blaugrau + Neongrün + Amber.
**Crimson / Copper:** Burgunder/Schwarzbraun + Rot/Magenta + Kupfer/Orange + Cyan + Cremeweiß.

## Geometrie

- Radius klein: 6–8 px
- Radius Standard: 10–12 px
- Radius Panel: 14–18 px
- Neon-/Fokusrahmen: 1–2 px
- großzügige Klickflächen und Innenabstände

## Typografie

- Seitentitel: 24–32 px
- Bereichsüberschrift: 18–22 px
- Standard: 15–17 px
- Button: 15–18 px
- Hilfe: mindestens 14 px
- Skalierung: 100 / 125 / 150 / 175 / 200 %

## Semantikregeln

- Farbe niemals als einziges Signal.
- Aktiver Workflow = Nummer + Symbol + Text + Akzent.
- Fehler = Farbe + Fehlersymbol + Klartext + Handlungsempfehlung.
- Fokus = deutlich sichtbarer Ring.
- Neon nur für Fokus, Auswahl, aktiven Workflow und primäre Aktion.
- Theme-Wechsel verändert keine Informationsarchitektur.
