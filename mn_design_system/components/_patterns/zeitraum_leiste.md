# Zeitraum-Leiste

> Segment-Leiste aus Links zur Wahl eines Zeitfensters (`?tage=30|90|365`). Die Auswahl steckt in der Adresse: kein Skript, Zurueck-Knopf und Lesezeichen funktionieren.

## Anatomie

```
┌──────────┬──────────┬─────────┐
│ 30 Tage  │ 90 Tage  │ 1 Jahr  │   <- jede Option mind. 44 x 44 px
└──────────┴──────────┴─────────┘
              ^ aktiv (aria-current="page", Akzent auf Indigo-Tint)
```

`<nav>` mit `<a>`-Optionen. Ruhend gedaempft auf Weiss, Hover hellgrau, die gewaehlte Option
in Akzentfarbe auf zartem Indigo. Tier-neutral.

## API-Contract

`ZeitraumLeisteInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `optionen` | `list[ZeitraumOption]` | 2..6 Eintraege (eine einzelne waere keine Auswahl); hoechstens eine `active` |
| `aria_label` | `str` | Default `"Zeitraum"`, min_length=1 — Landmark-Label des `<nav>` (WCAG 2.4.1) |

`ZeitraumOption` (Pydantic):

| Feld | Typ | Constraint |
|---|---|---|
| `label` | `str` | min_length=1, sichtbarer Text ("30 Tage") |
| `href` | `str` | min_length=1, Adresse ("?tage=30") |
| `active` | `bool` | Default False — die gewaehlte Option. Keine aktive Option ist erlaubt (Wert der Adresse nicht in der Liste) |

## Verwendete Tokens

- `web.touch-target` (44px) — Mindesthoehe UND Mindestbreite jeder Option (WCAG 2.5.5)
- `color.light.surface` — Hintergrund der Leiste
- `web.color.separator` — Rahmen und Trenner zwischen den Optionen
- `color.light.text-muted` — Text ruhend (>= 4,5:1 auf Weiss)
- `color.light.text` + `color.light.surface-subtle` — Hover (>= 4,5:1)
- `color.light.accent` + `color.indigo.50` — gewaehlte Option (>= 4,5:1)
- `web.color.focus-ring`, `web.stroke.focus` — Tastatur-Fokus (Ring nach INNEN, weil die Leiste `overflow: hidden` hat)
- `web.text.ui`, `web.leading.ui`, `web.stroke.line`, `radius.subtle`, `space.4`

## Verhalten

- HTML-Struktur: `<nav class="mn-zeitraum-leiste" aria-label="...">` mit
  `<a class="mn-zeitraum-leiste__option" href="..."[ aria-current="page"]>` je Option.
- Der aktive Zustand haengt NUR am Attribut `aria-current="page"` — es gibt keine zweite
  Klasse, die „aktiv" nur aussehen laesst. Hover steht im CSS vor dem aktiven Zustand
  (gleiche Spezifitaet): die gewaehlte Option bleibt unter dem Zeiger die gewaehlte.
- `label`, `href` und `aria_label` werden per `html.escape()` (Attribute mit `quote=True`)
  ausgegeben.
- Nichts inline: kein `style=`, kein `<script>`, kein `on…=` — laeuft unter
  `script-src 'self'` / `style-src 'self'`.
- Die Leiste setzt keinen Aussenabstand; den bestimmt der Konsument.

## Plattform-Implementierungen

- `mn_design_system/components/web/zeitraum_leiste.py` — `render_zeitraum_leiste_html()`,
  `render_zeitraum_leiste_css()`
- PDF / LaTeX: nicht vorgesehen (Bedienelement)
