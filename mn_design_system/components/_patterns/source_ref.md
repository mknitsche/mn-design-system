# Source-Ref

> Quelle erstklassig: macht den Quellen-Verweis zu einem eigenstaendigen
> Baustein statt einer beilaeufigen Meta-Notiz. Eine primaere Quelle, optional
> begleitet von weiteren. Kleine graue Meta-Optik.

## Anatomie

```
Quelle: finanznachrichten.de ↗ · weitere: handelsblatt.com ↗ · n-tv.de ↗
```

Ein `<span class="mn-source-ref">` mit dem Praefix `Quelle:`, der primaeren
Quelle als Link, und — falls vorhanden — `· weitere:` gefolgt von den weiteren
Quellen-Links (`·`-getrennt). Der externe-Link-Pfeil `↗` haengt per CSS
(`.mn-source-ref__link::after`) an jedem Link, nicht als Text (Mockup `.src::after`).

## API-Contract

`SourceRefInput` (Pydantic, siehe `contracts.py`):

| Feld | Typ | Constraint |
|---|---|---|
| `primary` | `SourceLink` | die fuehrende Quelle ("Quelle: …") |
| `weitere` | `list[SourceLink]` | Default `[]` — weitere Belege ("· weitere: …") |

`SourceLink` (Pydantic):

| Feld | Typ | Constraint |
|---|---|---|
| `href` | `str` | min_length=1 — Ziel-URL |
| `label` | `str` | min_length=1 — sichtbares Label (z.B. Domain) |

## Verwendete Tokens

- `web.text.caption` — Schriftgroesse (Feinzeile)
- `web.leading.caption` — Zeilenhoehe
- `color.light.text-muted` — Text- und Link-Farbe (grau)
- `web.stroke.focus` / `web.color.focus-ring` — `:focus-visible`-Outline der Links

## Verhalten

- HTML-Struktur: `<span class="mn-source-ref">Quelle: <a class="mn-source-ref__link">…</a></span>`.
- `weitere` leer → nur `Quelle: <primary>`. `weitere` gesetzt → zusaetzlich
  ` · weitere: <w1> · <w2> · …`.
- Jeder Link traegt per CSS-`::after` den `↗`-Pfeil (Inhalt/Dekoration getrennt).
- `href` (mit `quote=True`) und `label` werden per `html.escape()` XSS-sicher
  ausgegeben.
- Links haben einen Token-basierten `:focus-visible`-Indikator (WCAG 2.4.7).
- `render_source_ref_html(input, inline_css=True)` haengt das Komponenten-CSS an.

## Varianten

- **Nur primary**: `weitere=[]` — der haeufige Meta-Zeilen-Fall.
- **primary + weitere**: ein bis n weitere Belege — der Detail-/Aufmacher-Fall.
- Keine Tier- oder Farbvarianten (Quelle ist immer dezent grau).

## Plattform-Implementierungen

- `mn_design_system/components/web/source_ref.py` — HTML- + CSS-Renderer
- PDF/LaTeX — nicht implementiert (Pattern-First erlaubt spaeteres Nachziehen).

## Referenzen

- Mockup: `claudeAI ~/sync/build-artifacts/2026-06-14-briefing-web-mockup.html`
  (`.item__sources` / `.src::after`).
- Konsument: News-Item (`news_item.md`) nutzt source_ref fuer `source` und
  `detail.sources`.
