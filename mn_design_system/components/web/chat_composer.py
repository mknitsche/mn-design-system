"""Web-Renderer Chat-Composer — HTML + CSS, Twin-Chat (Build-Spec cld1-S57, T-3.4).

Konsumiert ChatComposerInput aus `_patterns.chat_contracts`. Die Eingabe-Leiste
am unteren Rand von `/kabinett/chat`: mehrzeiliges Textfeld, Senden- und
Unterbrechen-Button, eine Hinweis-Zeile (Zeichenzahl/zuletzt verursachte
Kosten — chat.js aktualisiert den Text laufend). Keine inline Event-Handler:
chat.js verdrahtet alle Interaktionen ueber die DOM-ids per addEventListener
(CSP script-src ohne 'unsafe-inline').

Mobile-first (Design-Spec cld1-S57 § Chat-UI): der Composer bleibt der letzte
Flex-Block im `.mn-chat-shell`-Spaltenlayout (siehe chat_stream.py) und traegt
zusaetzlich das untere Safe-Area-Inset (iPhone-Home-Indikator/Notch).
"""

from __future__ import annotations

from html import escape

from mn_design_system.components._patterns.chat_contracts import ChatComposerInput


def render_chat_composer_html(
    input: ChatComposerInput, *, inline_css: bool = False
) -> str:
    """Composer als HTML-Snippet (<div> mit <textarea> + zwei <button>).

    inline_css=True hangt das Komponenten-CSS in einem <style>-Block an.
    """
    parts: list[str] = []
    if inline_css:
        parts.append(f"<style>{render_chat_composer_css()}</style>")

    ta_id = escape(input.textarea_id, quote=True)
    send_id = escape(input.send_id, quote=True)
    interrupt_id = escape(input.interrupt_id, quote=True)
    hint_id = escape(input.hint_id, quote=True)
    placeholder = escape(input.placeholder, quote=True)

    parts.append('<div class="mn-chat-composer">')
    parts.append(
        f'<label class="mn-chat-composer__label" for="{ta_id}">Nachricht</label>'
    )
    parts.append(
        f'<textarea class="mn-chat-composer__input" id="{ta_id}" rows="1" '
        f'placeholder="{placeholder}" aria-label="{placeholder}"></textarea>'
    )
    parts.append('<div class="mn-chat-composer__row">')
    parts.append(
        f'<span class="mn-chat-composer__hint" id="{hint_id}">{escape(input.hint)}</span>'
    )
    parts.append('<div class="mn-chat-composer__actions">')
    parts.append(
        f'<button type="button" class="mn-chat-composer__btn mn-chat-composer__btn--interrupt" '
        f'id="{interrupt_id}" disabled>{escape(input.interrupt_label)}</button>'
    )
    parts.append(
        f'<button type="button" class="mn-chat-composer__btn mn-chat-composer__btn--send" '
        f'id="{send_id}">{escape(input.send_label)}</button>'
    )
    parts.append("</div>")  # __actions
    parts.append("</div>")  # __row
    parts.append("</div>")  # mn-chat-composer
    return "".join(parts)


def render_chat_composer_css() -> str:
    """Komponenten-CSS — Layout + Buttons, Token-Werte via Custom Properties."""
    return """
.mn-chat-composer {
  flex: 0 0 auto;
  border-top: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
  background: var(--color-light-surface, #ffffff);
  padding: var(--space-3, 12px) var(--web-layout-page-inset, 44px)
    calc(var(--space-3, 12px) + env(safe-area-inset-bottom, 0px)) var(--web-layout-page-inset, 44px);
  font-family: var(--web-font-sans, "Geist"), system-ui, sans-serif;
}
.mn-chat-composer__label {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}
.mn-chat-composer__input {
  width: 100%;
  box-sizing: border-box;
  resize: vertical;
  min-height: 2.75em;
  max-height: 40vh;
  padding: var(--space-2, 8px) var(--space-3, 12px);
  border: var(--web-stroke-line, 1px) solid var(--web-color-separator, #b4bcc8);
  border-radius: var(--radius-input, 4px);
  font-family: inherit;
  font-size: var(--web-text-body, 16px);
  line-height: var(--web-leading-body, 1.6);
  color: var(--color-light-text, #1e1b4b);
  background: var(--color-light-bg, #fdfdfd);
}
.mn-chat-composer__input:focus-visible {
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: 1px;
}
.mn-chat-composer__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3, 12px);
  margin-top: var(--space-2, 8px);
}
.mn-chat-composer__hint {
  font-size: var(--web-text-caption, 12px);
  color: var(--color-light-text-muted, #6b7280);
  font-variant-numeric: tabular-nums;
}
.mn-chat-composer__actions {
  display: flex;
  gap: var(--space-2, 8px);
}
.mn-chat-composer__btn {
  font-family: inherit;
  font-size: var(--web-text-ui, 14px);
  font-weight: 600;
  padding: var(--space-2, 8px) var(--space-4, 16px);
  border-radius: var(--radius-input, 4px);
  border: var(--web-stroke-line, 1px) solid transparent;
  cursor: pointer;
  transition: background 120ms, opacity 120ms;
}
.mn-chat-composer__btn:focus-visible {
  outline: var(--web-stroke-focus, 2px) solid var(--web-color-focus-ring, #4F46E5);
  outline-offset: 2px;
}
.mn-chat-composer__btn--send {
  background: var(--color-light-accent, #4F46E5);
  color: var(--color-dark-text, #f5f5f7);
}
.mn-chat-composer__btn--send:hover {
  background: var(--color-light-h2, #4338ca);
}
.mn-chat-composer__btn--interrupt {
  background: transparent;
  border-color: var(--web-color-separator, #b4bcc8);
  color: var(--color-light-text-muted, #6b7280);
}
.mn-chat-composer__btn--interrupt:hover:not(:disabled) {
  border-color: var(--color-status-error, #D32F2F);
  color: var(--color-status-error, #D32F2F);
}
.mn-chat-composer__btn:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}
@media (prefers-reduced-motion: reduce) {
  .mn-chat-composer__btn {
    transition: none;
  }
}
""".strip()
