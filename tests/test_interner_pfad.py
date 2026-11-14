"""`_interner_pfad` (Kachel-Link, Profil-Menue): jede Einzelpruefung traegt ein eigenes Schutzgut
(Open Redirect auf fremde Hosts, Steuerzeichen in href). Je Pruefung ein Test, der NUR sie trifft."""

from __future__ import annotations

import pytest

from mn_design_system.components._patterns.contracts import _interner_pfad

AUSGANG = "/start/profil/?a=1#b"


def test_gueltiger_pfad_bleibt():
    assert _interner_pfad(AUSGANG) == AUSGANG


@pytest.mark.parametrize("v", ["start/", "https://x.example/", "javascript:x", "#a"])
def test_ohne_fuehrenden_schraegstrich_abgewiesen(v):
    with pytest.raises(ValueError):
        _interner_pfad(v)


def test_protokoll_relativ_abgewiesen():
    with pytest.raises(ValueError):
        _interner_pfad("//evil.example/")


@pytest.mark.parametrize("v", ["/\\host", "/a\\b"])
def test_backslash_abgewiesen(v):
    # der Browser liest "/\host" als fremden Host; nur die Backslash-Pruefung faengt es
    with pytest.raises(ValueError):
        _interner_pfad(v)


@pytest.mark.parametrize("v", ["/a\tb", "/a\nb", "/a\x00b", "/a\x7fb", "/a b"])
def test_steuer_und_leerzeichen_abgewiesen(v):
    # "/<Tab>/host" liest der Browser als fremden Host; nur die Zeichenpruefung faengt es
    with pytest.raises(ValueError):
        _interner_pfad(v)
