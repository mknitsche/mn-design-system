"""Web-Renderer Stream-Cursor — HTML + CSS, Twin-Chat (Build-Spec cld1-S57, T-3.4).

Konsumiert StreamCursorInput aus `_patterns.chat_contracts`. Ein zurueckhaltender
Tipp-Indikator (drei pulsierende Punkte + Text) — Tufte-minimal statt Spinner-
Grafik. chat.js schaltet das `hidden`-Attribut waehrend ein Turn laeuft
(erste SSE-Delta bis `done`/`error`).
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.chat_contracts import StreamCursorInput


def render_stream_cursor_html(
    input: StreamCursorInput, *, inline_css: bool = False
) -> str:
    """Stream-Cursor als HTML-Snippet (<span>, standardmaessig `hidden`).

    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an.
    """
    parts: list[str] = []
    if inline_css:
        parts.append(f"<style>{render_stream_cursor_css()}</style>")

    cursor_id = escape(input.cursor_id, quote=True)
    parts.append(
        f'<span class="mn-stream-cursor" id="{cursor_id}" hidden '
        f'role="status" aria-live="polite">'
    )
    parts.append(
        '<span class="mn-stream-cursor__dots" aria-hidden="true">'
        "<span></span><span></span><span></span></span>"
    )
    parts.append(f'<span class="mn-stream-cursor__label">{escape(input.label)}</span>')
    parts.append("</span>")
    return "".join(parts)


def render_stream_cursor_css() -> str:
    """Komponenten-CSS — drei gestaffelt pulsierende Punkte, Reduced-Motion-fest."""
    return """
.mn-stream-cursor {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2, 8px);
  padding: var(--space-1, 4px) var(--web-layout-page-inset, 44px);
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  font-size: var(--web-text-caption, 12px);
  color: var(--color-light-text-muted, #6b7280);
}
.mn-stream-cursor[hidden] {
  display: none;
}
.mn-stream-cursor__dots {
  display: inline-flex;
  gap: 0.28em;
}
.mn-stream-cursor__dots span {
  width: 0.35em;
  height: 0.35em;
  border-radius: var(--radius-round, 9999px);
  background: currentColor;
  opacity: 0.35;
  animation: mn-stream-cursor-pulse 1.1s ease-in-out infinite;
}
.mn-stream-cursor__dots span:nth-child(2) {
  animation-delay: 0.15s;
}
.mn-stream-cursor__dots span:nth-child(3) {
  animation-delay: 0.3s;
}
@keyframes mn-stream-cursor-pulse {
  0%, 80%, 100% {
    opacity: 0.25;
  }
  40% {
    opacity: 0.9;
  }
}
@media (prefers-reduced-motion: reduce) {
  .mn-stream-cursor__dots span {
    animation: none;
    opacity: 0.6;
  }
}
""".strip()
