"""Web-Renderer News-Item — HTML + CSS, Briefing-Web-Ausgabe (Welle 3).

Konsumiert NewsItemInput aus `_patterns.contracts`. Kaskaden-Einheit des
Briefings: Rang + Schlagzeile (optional interner "tiefer"-Link) + Basis-Text +
Meta-Zeile (Kategorie · Zeit · Quelle) + optionaler aufklappbarer Vertiefungs-
Stufe ("+ mehr"). Der Aufmacher (`is_aufmacher`) ist dezent prominent: eine
Top-Akzentlinie und ein groesserer Titel (Tufte — Prominenz aus Struktur, nicht
aus Farbe).

Die Quelle wird ueber die source_ref-Komponente gerendert (Meta-Zeile und
Detail-Quellen), damit "Quelle" ueberall ein erstklassiger Baustein ist.

CSS-Strategie: alle Masse, Schriftgroessen, Linien und Farben aus Web-
Foundation- bzw. Light-Tokens (var(--web-*) / var(--color-*) / var(--space-*)).
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import NewsItemInput
from mn_design_system.components.web.source_ref import (
    render_source_ref_css,
    render_source_ref_html,
)


def render_news_item_html(input: NewsItemInput, *, inline_css: bool = False) -> str:
    """News-Item als HTML-Snippet (<article class="mn-news-item">).

    Struktur: row → (rank? + body → (eyebrow? · title[·link] · text · meta ·
    details?)). Aufmacher tragen `mn-news-item--aufmacher`. Alle Inhalte sind
    html.escape'd; hrefs zusaetzlich quote-escaped.
    inline_css=True hangt News-Item- UND Source-Ref-CSS in einem <style>-Block an.
    """
    parts: list[str] = []
    if inline_css:
        parts.append(
            f"<style>{render_news_item_css()}{render_source_ref_css()}</style>"
        )

    classes = ["mn-news-item"]
    if input.is_aufmacher:
        classes.append("mn-news-item--aufmacher")
    parts.append(f'<article class="{" ".join(classes)}">')
    parts.append('<div class="mn-news-item__row">')

    if input.rank is not None:
        parts.append(f'<span class="mn-news-item__rank">{escape(input.rank)}</span>')

    parts.append('<div class="mn-news-item__body">')

    # Eyebrow (z.B. "Aufmacher · stand auf S1").
    if input.eyebrow is not None:
        parts.append(f'<p class="mn-news-item__eyebrow">{escape(input.eyebrow)}</p>')

    # Titel — interner "tiefer"-Link nur, wenn deeper_href gesetzt ist.
    title = escape(input.title)
    if input.deeper_href is not None:
        href = escape(input.deeper_href, quote=True)
        title_inner = f'<a class="mn-news-item__title-link" href="{href}">{title}</a>'
    else:
        title_inner = title
    parts.append(f'<h3 class="mn-news-item__title">{title_inner}</h3>')

    # Basis-Tiefe.
    parts.append(f'<p class="mn-news-item__text">{escape(input.text)}</p>')

    # Meta-Zeile: Kategorie · Zeit · Quelle (inline).
    parts.append('<div class="mn-news-item__meta">')
    parts.append(f'<span class="mn-news-item__cat">{escape(input.kategorie)}</span>')
    parts.append(f'<span class="mn-news-item__time">{escape(input.zeitangabe)}</span>')
    if input.source is not None:
        parts.append(render_source_ref_html(input.source))
    parts.append("</div>")

    # Aufklappbare Vertiefungs-Stufe.
    if input.detail is not None:
        detail = input.detail
        summary_label = escape(detail.summary_label)
        parts.append('<details class="mn-news-item__details">')
        parts.append(
            f'<summary class="mn-news-item__more">+ mehr ({summary_label})</summary>'
        )
        parts.append('<div class="mn-news-item__detail">')
        parts.append(
            f'<span class="mn-news-item__level">{escape(detail.level_label)}</span>'
        )
        parts.append(f'<p class="mn-news-item__detail-text">{escape(detail.text)}</p>')
        if detail.sources is not None:
            parts.append(render_source_ref_html(detail.sources))
        parts.append("</div>")
        parts.append("</details>")

    parts.append("</div>")  # __body
    parts.append("</div>")  # __row
    parts.append("</article>")
    return "".join(parts)


def render_news_item_css() -> str:
    """Komponenten-CSS — Layout + Aufmacher-Modifier, Token-Werte via CSS
    Custom Properties.

    Konsument muss `dist/css/tokens.css` einbinden, damit `var(--color-light-h1)`
    etc. greift, und das Source-Ref-CSS (render_source_ref_css()) fuer die
    eingebettete Quelle.
    """
    return """
.mn-news-item {
  padding: var(--space-4, 16px) 0;
  border-bottom: var(--web-stroke-line, 1px) solid var(--color-light-surface-subtle, #f6f6f6);
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  scroll-margin-top: var(--space-4, 16px);
}
.mn-news-item__row {
  display: flex;
  gap: var(--space-4, 16px);
  align-items: baseline;
}
.mn-news-item__rank {
  font-size: var(--web-text-ui, 14px);
  font-weight: 700;
  color: var(--color-grey-300, #cbd5e1);
  min-width: 1.6em;
  font-variant-numeric: tabular-nums;
}
.mn-news-item__body {
  flex: 1;
}
.mn-news-item__eyebrow {
  font-size: var(--web-text-caption, 12px);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-light-accent, #4F46E5);
  margin: 0 0 var(--space-1, 4px);
}
.mn-news-item__title {
  font-size: var(--web-text-lead, 19px);
  line-height: var(--web-leading-h3, 1.3);
  font-weight: 600;
  color: var(--color-light-h1, #312e81);
  margin: 0 0 var(--space-1, 4px);
}
.mn-news-item__title-link {
  color: inherit;
  text-decoration: none;
}
.mn-news-item__title-link:hover {
  color: var(--color-light-accent, #4F46E5);
  text-decoration: underline;
}
.mn-news-item__title-link:focus-visible {
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: 2px;
}
.mn-news-item__text {
  font-size: var(--web-text-body, 16px);
  line-height: var(--web-leading-body, 1.6);
  color: var(--color-grey-700, #374151);
  margin: 0;
}
.mn-news-item__meta {
  display: flex;
  gap: var(--space-3, 12px);
  align-items: center;
  flex-wrap: wrap;
  margin-top: var(--space-2, 8px);
  font-size: var(--web-text-caption, 12px);
  color: var(--color-light-text-muted, #6b7280);
}
.mn-news-item__cat {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-light-h2, #4338ca);
}
.mn-news-item__details {
  margin-top: var(--space-2, 8px);
}
.mn-news-item__more {
  font-size: var(--web-text-ui, 14px);
  color: var(--color-light-accent, #4F46E5);
  cursor: pointer;
  list-style: none;
  display: inline-flex;
  align-items: center;
  gap: var(--space-1, 4px);
  user-select: none;
}
.mn-news-item__more::-webkit-details-marker {
  display: none;
}
.mn-news-item__detail {
  margin-top: var(--space-2, 8px);
  padding-left: var(--space-3, 12px);
  border-left: var(--web-stroke-line-strong, 2px) solid var(--color-light-accent-soft, #e0e7ff);
  font-size: var(--web-text-body, 16px);
  line-height: var(--web-leading-body, 1.6);
  color: var(--color-grey-700, #374151);
}
.mn-news-item__level {
  display: block;
  font-size: var(--web-text-caption, 12px);
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-light-accent, #4F46E5);
  margin-bottom: var(--space-2, 8px);
}
.mn-news-item__detail-text {
  margin: 0;
}
.mn-news-item--aufmacher {
  border-top: var(--web-stroke-line-strong, 2px) solid var(--color-light-accent, #4F46E5);
  padding-top: var(--space-3, 12px);
}
.mn-news-item--aufmacher .mn-news-item__title {
  font-size: var(--web-text-h3, 23px);
  line-height: var(--web-leading-h2, 1.22);
}
""".strip()
