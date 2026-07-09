"""Web-Renderer Chat-Stream — HTML + CSS, Twin-Chat (Build-Spec cld1-S57, T-3.4).

Konsumiert ChatStreamInput aus `_patterns.chat_contracts`. Rendert den LEEREN
Nachrichten-Rahmen fuer `/kabinett/chat` — die eigentlichen Nachrichten (Rolle
owner/twin, Markdown-Body, Code-Bloecke, Tool-Badges) werden ausschliesslich
clientseitig durch chat.js als DOM-Knoten in diesen Rahmen eingehaengt (keine
Server-Roundtrips, kein innerHTML mit Modell-/Nutzer-Text — XSS-Schutz).

DOM-Vertrag fuer chat.js (dieses CSS definiert die Klassen, chat.js erzeugt die
Knoten zur Laufzeit):

    <div class="mn-chat-shell">                      <!-- Seiten-Wrapper -->
      ...
      <div class="mn-chat-stream" id="chat-stream">   <!-- render_chat_stream_html() -->
        <article class="mn-chat-message mn-chat-message--owner|--twin">
          <p class="mn-chat-message__role">(App-spezifisch, z.B. Matthias|cld1-amber)</p>
          <div class="mn-chat-message__body">
            <!-- Whitelist-Markdown als DOM-Knoten: p / ul / ol / li / pre>code / code / strong / em -->
          </div>
          <div class="mn-chat-tools">                 <!-- nur bei Tool-Aufrufen -->
            <span class="mn-chat-tool-badge">mn-brain: todo_erledigen</span>
          </div>
        </article>
      </div>
      ...
    </div>

`.mn-chat-shell` ist der volle Seiten-Wrapper (flex-column, volle Viewport-
Hoehe, Sans-Schrift) — der Konsument (chat_ui.py) legt ihn um Status-Banner +
Verlaufsauswahl + Chat-Stream + Composer, damit NUR der Stream scrollt und der
Composer am unteren Rand stehen bleibt (mobile-first, Design-Spec cld1-S57).
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.chat_contracts import ChatStreamInput


def render_chat_stream_html(input: ChatStreamInput, *, inline_css: bool = False) -> str:
    """Chat-Stream-Rahmen als HTML-Snippet (<div> mit Leer-Zustand-Absatz).

    chat.js entfernt/versteckt den Leer-Zustand-Absatz (`[data-chat-empty]`),
    sobald die erste Nachricht eingehaengt wird.
    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an.
    """
    parts: list[str] = []
    if inline_css:
        parts.append(f"<style>{render_chat_stream_css()}</style>")

    stream_id = escape(input.stream_id, quote=True)
    aria_label = escape(input.aria_label, quote=True)
    parts.append(
        f'<div class="mn-chat-stream" id="{stream_id}" '
        f'aria-live="polite" aria-label="{aria_label}">'
    )
    parts.append(
        f'<p class="mn-chat-stream__empty" data-chat-empty>{escape(input.empty_hint)}</p>'
    )
    parts.append("</div>")
    return "".join(parts)


def render_chat_stream_css() -> str:
    """Komponenten-CSS — Shell-Layout + vollstaendiger Nachrichten-Klassen-Vertrag.

    Token-Werte via CSS Custom Properties (var(--x, fallback)); Konsument
    kann zusaetzlich echte Werte im eigenen :root-Block ausgeben (chat_ui.py
    tut dies dynamisch aus den TOKENS, analog generate_pages.py).
    """
    return """
.mn-chat-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
  background: var(--color-light-bg, #fdfdfd);
}
.mn-chat-stream {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  gap: var(--space-3, 12px);
  padding: var(--space-4, 16px) var(--web-layout-page-inset, 44px);
  scroll-behavior: smooth;
}
.mn-chat-stream__empty {
  margin: auto;
  font-style: italic;
  font-size: var(--web-text-ui, 14px);
  color: var(--color-light-text-muted, #6b7280);
  text-align: center;
}
.mn-chat-message {
  max-width: 78%;
  padding: var(--space-3, 12px) var(--space-4, 16px);
  border-radius: var(--radius-card, 4px);
  font-size: var(--web-text-body, 16px);
  line-height: var(--web-leading-body, 1.6);
}
.mn-chat-message--owner {
  align-self: flex-end;
  background: var(--color-light-accent-soft, #e0e7ff);
  color: var(--color-light-text, #1e1b4b);
}
.mn-chat-message--twin {
  align-self: flex-start;
  background: var(--color-light-surface, #ffffff);
  border: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
  border-left: var(--web-stroke-line-strong, 2px) solid var(--color-light-h2, #4338ca);
  color: var(--color-light-text, #1e1b4b);
}
.mn-chat-message__role {
  margin: 0 0 var(--space-1, 4px);
  font-size: var(--web-text-caption, 12px);
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-light-text-muted, #6b7280);
}
.mn-chat-message__body {
  overflow-wrap: break-word;
}
.mn-chat-message__body p {
  margin: 0 0 var(--space-2, 8px);
}
.mn-chat-message__body p:last-child {
  margin-bottom: 0;
}
.mn-chat-message__body ul,
.mn-chat-message__body ol {
  margin: 0 0 var(--space-2, 8px);
  padding-left: var(--space-5, 20px);
}
.mn-chat-message__body li {
  margin-bottom: var(--space-1, 4px);
}
.mn-chat-message__body code {
  font-family: var(--font-family-mono, "JetBrains Mono"), ui-monospace, monospace;
  font-size: 0.9em;
  background: var(--color-light-surface-subtle, #f6f6f6);
  padding: 0.1em 0.35em;
  border-radius: var(--radius-subtle, 2px);
}
.mn-chat-message__body pre {
  margin: 0 0 var(--space-2, 8px);
  padding: var(--space-3, 12px);
  background: var(--color-light-surface-subtle, #f6f6f6);
  border: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
  border-radius: var(--radius-subtle, 2px);
  overflow-x: auto;
  max-width: 100%;
}
.mn-chat-message__body pre code {
  background: none;
  padding: 0;
  font-size: var(--web-text-caption, 12px);
  line-height: var(--web-leading-caption, 1.4);
  white-space: pre;
}
.mn-chat-tools {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1, 4px);
  margin-top: var(--space-2, 8px);
}
.mn-chat-tool-badge {
  display: inline-flex;
  align-items: center;
  font-family: var(--font-family-mono, "JetBrains Mono"), ui-monospace, monospace;
  font-size: var(--web-text-caption, 12px);
  color: var(--color-light-text-muted, #6b7280);
  background: var(--color-light-surface-subtle, #f6f6f6);
  border: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
  border-radius: var(--radius-subtle, 2px);
  padding: 0.15em 0.5em;
}
.mn-chat-tool-badge::before {
  content: "\\2699\\FE0E ";
}
@media (max-width: 640px) {
  .mn-chat-message {
    max-width: 92%;
  }
}
""".strip()
