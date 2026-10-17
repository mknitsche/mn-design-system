# Zurueck-Zeile (Back-Link)

> Die EINE Zurueck-Zeile einer mkn-desk.com-Seite: ein Link auf die Elternseite. Tier-neutral.

## Anatomie

```
← Briefing                                  <- Zurueck-Zeile (erstes Kind von <main>)
Briefing, Sektion Politik                   <- h1 der Seite
```

`<nav class="mn-back-link" aria-label="Zurück">` mit genau einem `<a href>`; der Pfeil ist ein
`<span aria-hidden="true">←</span>`, der Link-Text ist der Titel der Elternseite.

## API-Contract

`BackLinkInput` (Pydantic, frozen, `extra="forbid"`, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `href` | `str` | interner Pfad: gestrippt, genau ein fuehrendes `/`, kein `//`, kein Backslash, keine Steuerzeichen (sonst ValueError) |
| `label` | `str` | min_length=1, wörtlich die H1 der Elternseite |

`render_back_link_html(input, *, inline_css=False)` und `render_back_link_css()`.

## Regel (Verwendung)

- **Genau eine** Zurueck-Zeile je Seite, als **erstes Kind von `<main>`**, vor dem Seitentitel.
- **Nur unterhalb einer Reiterseite.** Eine Seite, die selbst ein Reiter (Unterleiste) oder die Bereichswurzel
  ist, traegt keine.
- Das Ziel ist die Seite, die diese Seite verlinkt; der Text ist deren Titel.
- Keine zweite Reihe von Links auf andere Seiten daneben (Navigation = Masthead, Unterleiste, Zurueck-Zeile).

## Verwendete Tokens

`web.text.ui`, `color.light.text-muted`, `color.light.accent` (Hover), `web.touch-target`
(Mindesthoehe), `space.4` (Abstand unten), `web.stroke-focus` / `web.color-focus-ring` (Tastatur-Fokus).
Keine Literalfarbe ausser als `var()`-Rueckfall.
