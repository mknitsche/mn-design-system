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
