"""Die zwei MKN-Logos im Paket: Dateien, Rechtevermerk, Auslieferung.

Die Logos (Kopf „MKN" und volles Logo „MKN 2nd Brain") liegen hier, damit jede Anwendung
dieselbe freigegebene Fassung nutzt. Sie sind © Matthias Nitsche und ausdruecklich NICHT von
der Lizenz in `LICENSE` gedeckt — der Vermerk muss neben den Dateien liegen und mit ihnen
ausgeliefert werden, sonst reist ein Logo ohne seinen Rechtehinweis.
"""

from __future__ import annotations

from pathlib import Path

import tomllib

import mn_design_system

_PAKET = Path(mn_design_system.__file__).parent
_LOGOS = _PAKET / "logos"
_DATEIEN = ("2026-MKN-LogoKopf.svg", "2026-MKN-2ndBrain-Logo.svg")


def test_beide_logos_liegen_als_svg_im_paket():
    for name in _DATEIEN:
        datei = _LOGOS / name
        assert datei.is_file(), datei
        kopf = datei.read_bytes()[:400]
        assert kopf.startswith(b"<?xml") and b"<svg" in kopf, name


def test_notice_nennt_rechteinhaber_und_ausnahme_von_der_lizenz():
    notice = (_LOGOS / "NOTICE").read_text(encoding="utf-8")
    assert "© Matthias Nitsche" in notice
    assert "NICHT" in notice and "LICENSE" in notice
    for name in _DATEIEN:
        assert name in notice


def test_package_data_liefert_logos_und_vermerk_aus():
    """Das Wheel enthaelt nur, was `package-data` nennt (setuptools globbt relativ zum Paket)."""
    pyproject = _PAKET.parent / "pyproject.toml"
    muster = tomllib.loads(pyproject.read_text(encoding="utf-8"))["tool"]["setuptools"][
        "package-data"
    ]["mn_design_system"]
    abgedeckt = {p for m in muster for p in _PAKET.glob(m) if p.is_file()}
    erwartet = {_LOGOS / name for name in _DATEIEN} | {_LOGOS / "NOTICE"}
    assert erwartet <= abgedeckt, sorted(str(p) for p in erwartet - abgedeckt)
