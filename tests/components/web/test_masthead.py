"""Tests fuer den Web-Masthead (Design §10) — Contracts + Renderer."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mn_design_system.components._patterns.contracts import (
    MastheadChip,
    MastheadEmblem,
    MastheadInput,
    MastheadTierItem,
    WebTier,
)


def _make_masthead_input(**overrides) -> MastheadInput:
    base = {
        "emblem": MastheadEmblem(
            src="/assets/logo-mkn2ndbrain-kopf.png",
            alt="from the desk of mn",
            href="/start/",
        ),
        "wordmark": "from the desk of mn",
        "edition_date": "Donnerstag · 21. Mai 2026",
        "tier_items": [
            MastheadTierItem(
                label="Start", href="/start/", tier=WebTier.START, active=True
            ),
            MastheadTierItem(
                label="Bibliothek", href="/bibliothek/", tier=WebTier.BIBLIOTHEK
            ),
            MastheadTierItem(label="Atelier", href="/atelier/", tier=WebTier.ATELIER),
            MastheadTierItem(
                label="Kabinett", href="/kabinett/", tier=WebTier.KABINETT
            ),
        ],
        "context_chip": MastheadChip(tier=WebTier.ATELIER, label="Atelier · AMBER"),
    }
    base.update(overrides)
    return MastheadInput(**base)


class TestMastheadContracts:
    def test_minimal_input_constructs(self):
        masthead = _make_masthead_input()
        assert masthead.wordmark == "from the desk of mn"
        assert len(masthead.tier_items) == 4

    def test_edition_date_optional(self):
        masthead = _make_masthead_input(edition_date=None)
        assert masthead.edition_date is None

    def test_context_chip_optional(self):
        masthead = _make_masthead_input(context_chip=None)
        assert masthead.context_chip is None

    def test_tier_items_required_nonempty(self):
        with pytest.raises(ValidationError):
            _make_masthead_input(tier_items=[])

    def test_extra_field_forbidden(self):
        with pytest.raises(ValidationError):
            MastheadInput(
                emblem=MastheadEmblem(src="/x", alt="x", href="/"),
                wordmark="x",
                tier_items=[MastheadTierItem(label="X", href="/x", tier=WebTier.START)],
                unexpected="boom",
            )

    def test_frozen(self):
        masthead = _make_masthead_input()
        with pytest.raises(ValidationError):
            masthead.wordmark = "changed"


from mn_design_system.components.web.masthead import (  # noqa: E402
    render_masthead_css,
    render_masthead_html,
)
from mn_design_system.tokens import get  # noqa: E402


class TestRenderMastheadHtml:
    def test_minimal_renders_both_rows(self):
        html = render_masthead_html(_make_masthead_input())
        assert 'class="mn-masthead"' in html
        assert "mn-masthead__identity" in html
        assert "mn-masthead__tiers" in html

    def test_emblem_rendered_and_linked(self):
        html = render_masthead_html(_make_masthead_input())
        assert 'class="mn-masthead__emblem" href="/start/"' in html
        assert "/assets/logo-mkn2ndbrain-kopf.png" in html

    def test_wordmark_rendered(self):
        html = render_masthead_html(_make_masthead_input())
        assert "from the desk of mn" in html

    def test_edition_date_rendered_when_present(self):
        html = render_masthead_html(_make_masthead_input())
        assert "21. Mai 2026" in html
        assert "mn-masthead__edition" in html

    def test_edition_date_absent_when_none(self):
        html = render_masthead_html(_make_masthead_input(edition_date=None))
        assert "mn-masthead__edition" not in html

    def test_tier_pills_rendered(self):
        html = render_masthead_html(_make_masthead_input())
        assert html.count("mn-masthead__pill--") == 4

    def test_active_pill_marked_once(self):
        html = render_masthead_html(_make_masthead_input())
        assert html.count("is-active") == 1
        assert html.count('aria-current="page"') == 1

    def test_context_chip_rendered(self):
        html = render_masthead_html(_make_masthead_input())
        assert "mn-masthead__chip--atelier" in html
        assert "Atelier · AMBER" in html

    def test_hydration_chip_rendered_when_id_set(self):
        html = render_masthead_html(
            _make_masthead_input(user_chip_id="masthead-user-chip")
        )
        assert 'id="masthead-user-chip"' in html
        assert "mn-masthead__chip--loading" in html

    def test_nav_has_aria_label(self):
        html = render_masthead_html(_make_masthead_input())
        assert 'aria-label="Hauptnavigation"' in html

    def test_xss_label_escaped(self):
        html = render_masthead_html(
            _make_masthead_input(
                tier_items=[
                    MastheadTierItem(
                        label="<script>alert(1)</script>",
                        href="/x",
                        tier=WebTier.START,
                    )
                ]
            )
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_wordmark_escaped(self):
        html = render_masthead_html(
            _make_masthead_input(wordmark="<img src=x onerror=alert(1)>")
        )
        assert "<img src=x" not in html

    def test_inline_css_embedded(self):
        html = render_masthead_html(_make_masthead_input(), inline_css=True)
        assert "<style>" in html
        assert ".mn-masthead" in html


class TestRenderMastheadCss:
    def test_uses_foundation_tokens(self):
        css = render_masthead_css()
        assert "var(--web-text-ui" in css
        assert "var(--web-layout-content-width" in css
        assert "var(--web-layout-page-inset" in css
        assert "var(--web-stroke-line-strong" in css

    def test_divider_uses_separator_on_dark(self):
        css = render_masthead_css()
        assert "var(--web-color-separator-on-dark" in css

    def test_focus_ring_from_tokens(self):
        css = render_masthead_css()
        assert "var(--web-stroke-focus" in css
        assert "var(--web-color-focus-ring" in css

    def test_no_print_pt_units(self):
        """Keine pt-Einheiten — der Masthead ist rein web."""
        css = render_masthead_css()
        assert "pt;" not in css and "pt " not in css

    def test_tier_fallback_matches_real_tokens(self):
        """Der var()-Fallback je Tier-Pill/Chip muss der ECHTE Tier-Wert sein."""
        css = render_masthead_css()
        for tier in ("bibliothek", "atelier", "kabinett", "start"):
            soll_bg = get(f"color.tier.{tier}.bg")
            soll_text = get(f"color.tier.{tier}.text")
            assert soll_bg is not None and soll_text is not None
            assert f"var(--color-tier-{tier}-bg, {soll_bg})" in css
            assert f"var(--color-tier-{tier}-text, {soll_text})" in css

    def test_pill_hover_is_tier_preview(self):
        """Hover-Revision cld1-S21: der Pill-Hover leuchtet im Tier-Farbton
        (hover-on-dark-Token), nicht im alten neutralen 8%-Schimmer — eine
        Vorschau auf den Aktiv-Zustand, nur fuer inaktive Pills."""
        css = render_masthead_css()
        assert "rgba(255, 255, 255, 0.08)" not in css
        for tier in ("bibliothek", "atelier", "kabinett", "start"):
            assert f".mn-masthead__pill--{tier}:not(.is-active):hover" in css
            assert f"var(--color-tier-{tier}-hover-on-dark" in css
            assert get(f"color.tier.{tier}.hover-on-dark") is not None
