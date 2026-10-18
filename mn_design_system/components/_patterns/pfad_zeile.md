# Pfadzeile

> Die Vorfahren eines Ordners als Links, von oben nach unten: `archiv › briefing ›`. Tier-neutral.

## API-Contract

`PfadZeileInput(vorfahren=((label, href), ...))` (Pydantic, frozen, `extra="forbid"`); `href`: interner oder
relativer Pfad, kein Schema. `render_pfad_zeile_html(p, *, inline_css=False)` liefert `""` bei leeren Vorfahren,
sonst `<nav class="mn-pfad-zeile" aria-label="Pfad">`; Trenner `›` ist `aria-hidden`. `render_pfad_zeile_css()`.

## Regel (Verwendung)

Welche Vorfahren gezeigt werden, entscheidet der Konsument. Im Magazin: nur Vorfahren oberhalb des direkten
Elternordners und unterhalb der Wurzel, also erst ab Ebene 3 (die Zurueck-Zeile traegt den Elternordner).

## Verwendete Tokens

`web.text.ui`, `web.leading.ui`, `color.light.text-muted`, `color.light.accent` (Hover), `web.stroke.focus`,
`web.color.focus-ring`, `space.1`.
