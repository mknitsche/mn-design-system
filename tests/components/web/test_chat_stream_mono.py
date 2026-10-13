"""Chat-Baustein: Code und Werkzeug-Abzeichen in der Web-Mono (Review 0.16.0).

``--font-family-mono`` ist der PDF-Name „JetBrainsMono“ (Token ``font.family.mono``), kein
Web-Familienname — wer ``tokens.css`` laedt, bekam damit keine Monospace-Schrift.
"""

from __future__ import annotations

from mn_design_system.components.web.chat_stream import render_chat_stream_css


def test_mono_regeln_nutzen_den_web_familiennamen():
    css = render_chat_stream_css()
    assert css.count("var(--web-font-mono") >= 2, (
        "Untergrenze: Code + Abzeichen (LP-36)"
    )
    assert "--font-family-mono" not in css
