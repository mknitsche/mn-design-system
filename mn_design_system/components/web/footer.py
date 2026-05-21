"""Web-Renderer Footer — HTML + CSS.

Konsumiert FooterInput aus `_patterns.contracts`. Schlanke einzeilige
Seiten-Fusszeile von mkn-desk.com: links eine Identitaets-Zeile aus
`|`-getrennten Segmenten (Marke, Seiten-Kontext, optional ein client-seitig
gefuellter Profil-Slot), rechts die Rechtslinks (`·`-getrennt) plus optionale
Version.

CSS-Strategie wie brand_bar / kpi_card: Farb- und Schrift-Token via CSS Custom
Properties, Layout inline. Die "Hochstrich"-Trennlinie ueber dem Footer ist
eine duenne `border-top` (Spec §cld1-S19 Variante E, Schlusszeilen-Form cld1-S21).
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.contracts import FooterInput


def render_footer_html(input: FooterInput, *, inline_css: bool = False) -> str:
    """Footer als HTML-Snippet — eine Zeile: links Identitaet, rechts Recht + Version.

    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an —
    fuer Single-Snippet-Embeds.
    """
    parts: list[str] = []
    if inline_css:
        parts.append(f"<style>{render_footer_css()}</style>")

    parts.append('<footer class="mn-footer">')
    parts.append('<div class="mn-footer__inner">')

    # Linke Identitaets-Zeile: Segmente, mit |-Strich getrennt.
    parts.append('<div class="mn-footer__identity">')
    for index, segment in enumerate(input.segments):
        if index > 0:
            parts.append('<span class="mn-footer__sep" aria-hidden="true">|</span>')
        text = escape(segment.text)
        if segment.slot_id is not None:
            slot_id = escape(segment.slot_id, quote=True)
            parts.append(f'<span class="mn-footer__slot" id="{slot_id}">{text}</span>')
        else:
            parts.append(f'<span class="mn-footer__seg">{text}</span>')
    parts.append("</div>")

    # Rechter Cluster: Rechtslinks + optionale Version, mit ·-Punkt getrennt.
    parts.append('<div class="mn-footer__meta">')
    meta: list[str] = []
    for link in input.links:
        href = escape(link.href, quote=True)
        label = escape(link.label)
        meta.append(f'<a class="mn-footer__link" href="{href}">{label}</a>')
    if input.version is not None:
        version = escape(input.version)
        meta.append(f'<span class="mn-footer__version">{version}</span>')
    separator = '<span class="mn-footer__sep" aria-hidden="true">·</span>'
    parts.append(separator.join(meta))
    parts.append("</div>")

    parts.append("</div>")
    parts.append("</footer>")
    return "".join(parts)


def render_footer_css() -> str:
    """Komponenten-CSS — Layout-only, Token-Werte via CSS Custom Properties.

    Konsument muss `dist/css/tokens.css` einbinden, damit
    `var(--color-light-border)` etc. greift.
    """
    return """
.mn-footer {
  font-family: var(--font-body, "Geist"), system-ui, sans-serif;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: var(--stroke-thin, 0.5pt) solid var(--color-light-border, #cbd5e1);
}
.mn-footer__inner {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.35rem 1.5rem;
  font-size: 0.8125rem;
  color: var(--color-light-text-muted, #6b7280);
}
.mn-footer__identity,
.mn-footer__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
}
.mn-footer__sep {
  margin: 0 0.5rem;
  opacity: 0.5;
}
.mn-footer__link {
  color: var(--color-light-text-muted, #6b7280);
  text-decoration: none;
}
.mn-footer__link:hover {
  text-decoration: underline;
}
.mn-footer__link:focus-visible {
  outline: 2px solid var(--color-light-accent, #4F46E5);
  outline-offset: 2px;
}
.mn-footer__version {
  color: var(--color-light-text-subtle, #9ca3af);
}
""".strip()
