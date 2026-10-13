"""Lizenztexte: jede Schriftfamilie im Paket bringt ihren Lizenztext mit (v0.16.0).

Die SIL Open Font License 1.1 verlangt, dass jede weitergegebene Kopie der Schrift den
Copyright-Vermerk und den Lizenztext enthaelt. Bis 0.15.0 lag nur bei Geist ein Text im
Paket; fuenf weitere Familien und die Web-Schriften wurden ohne ihn ausgeliefert, Phosphor
(MIT) ebenso. Geprueft wird nicht nur, dass eine Datei da ist, sondern dass sie die
Copyright-Zeile traegt, die in den Schriftdateien selbst steht (name-Tabelle, ID 0).
"""

from __future__ import annotations

import struct
from fnmatch import fnmatch
from pathlib import Path

import pytest

from mn_design_system.fonts import FONT_DIR

_SCHRIFT_ENDUNGEN = {".ttf", ".otf", ".woff2"}

#: Familien, die laut Metadaten (name ID 13/14) unter der MIT-Lizenz stehen; alle anderen
#: stehen unter der SIL Open Font License 1.1.
_MIT = {"phosphor"}

#: Die Familien, die das Paket heute mitbringt (Untergrenze, LP-36): ein Lauf ueber
#: „alle gefundenen Familien“ ist bei leerer Entdeckung trivial gruen.
_ERWARTET = {
    "geist",
    "inter",
    "jetbrains-mono",
    "noto",
    "phosphor",
    "source-sans",
    "source-serif",
    "stix-two",
    "web",
}


def _familien() -> list[Path]:
    return sorted(
        d
        for d in FONT_DIR.iterdir()
        if d.is_dir()
        and any(f.suffix.lower() in _SCHRIFT_ENDUNGEN for f in d.iterdir())
    )


def _lizenzdatei(familie: Path) -> Path | None:
    kandidaten = sorted(
        f
        for f in familie.iterdir()
        if f.is_file() and f.name.upper().startswith(("OFL", "LICENSE"))
    )
    return kandidaten[0] if kandidaten else None


def _copyright_zeile(pfad: Path) -> str | None:
    """name-ID 0 einer TTF/OTF (reines struct, keine Zusatzbibliothek)."""
    daten = pfad.read_bytes()
    anzahl = struct.unpack(">H", daten[4:6])[0]
    name_offset = None
    for i in range(anzahl):
        tag, _pruef, offset, _laenge = struct.unpack(
            ">4sIII", daten[12 + 16 * i : 28 + 16 * i]
        )
        if tag == b"name":
            name_offset = offset
    if name_offset is None:
        return None
    _fmt, anz, str_offset = struct.unpack(">HHH", daten[name_offset : name_offset + 6])
    gefunden: dict[tuple[int, int], str] = {}
    for i in range(anz):
        basis = name_offset + 6 + 12 * i
        plattform, _enc, sprache, nid, laenge, so = struct.unpack(
            ">HHHHHH", daten[basis : basis + 12]
        )
        if nid != 0 or plattform not in (1, 3):
            continue
        start = name_offset + str_offset + so
        roh = daten[start : start + laenge]
        gefunden[(plattform, sprache)] = (
            roh.decode("utf-16-be") if plattform == 3 else roh.decode("mac_roman")
        )
    return gefunden.get((3, 0x409)) or gefunden.get((1, 0))


def _copyright_zeilen(familie: Path) -> set[str]:
    zeilen = {
        _copyright_zeile(f)
        for f in familie.iterdir()
        if f.suffix.lower() in {".ttf", ".otf"}
    }
    return {z for z in zeilen if z}


def test_untergrenze_der_familien():
    """Das Paket bringt mindestens diese neun Familien mit — sonst prueft der Rest nichts."""
    namen = {d.name for d in _familien()}
    assert len(namen) >= 9
    assert _ERWARTET <= namen


@pytest.mark.parametrize("name", sorted(_ERWARTET))
def test_jede_familie_hat_einen_lizenztext(name):
    familie = FONT_DIR / name
    datei = _lizenzdatei(familie)
    assert datei is not None, f"{name}: keine OFL*/LICENSE*-Datei"
    text = datei.read_text(encoding="utf-8")
    if name in _MIT:
        assert text.startswith("MIT License")
        assert "Permission is hereby granted, free of charge" in text
    else:
        assert "SIL OPEN FONT LICENSE Version 1.1" in text
        assert "PERMISSION AND CONDITIONS" in text


def test_neue_familien_tauchen_nicht_ohne_lizenz_auf():
    """Eine neue Schrift im Paket ohne Lizenztext faellt hier auf, nicht erst beim Release."""
    ohne = [d.name for d in _familien() if _lizenzdatei(d) is None]
    assert ohne == []


@pytest.mark.parametrize("name", sorted(_ERWARTET - {"web", "geist"}))
def test_lizenztext_traegt_die_copyright_zeile_der_schrift(name):
    """Jede Copyright-Zeile aus den Metadaten der Schriftdateien steht im Lizenztext —
    nichts Erfundenes, nichts Abgeschriebenes.

    Ausgenommen: ``geist`` (der Text liegt seit 0.15.0 bei und nennt die Zeile des
    Upstream-Projekts, „Vercel, in collaboration with basement.studio“; die Schriftdateien
    tragen „The Geist Project Authors“) und ``web`` (eigener Test unten)."""
    familie = FONT_DIR / name
    zeilen = _copyright_zeilen(familie)
    assert zeilen, f"{name}: keine Copyright-Zeile in den Schriftdateien lesbar"
    text = _lizenzdatei(familie).read_text(encoding="utf-8")
    fehlend = sorted(z for z in zeilen if z not in text)
    assert fehlend == []


def test_geist_text_beginnt_mit_einem_copyright_vermerk():
    text = (FONT_DIR / "geist" / "OFL.txt").read_text(encoding="utf-8")
    assert text.startswith("Copyright")


def test_web_schriften_tragen_die_copyright_zeilen_ihrer_quellfamilien():
    """fonts/web/ enthaelt Geist und Source Serif 4 im WOFF2-Format; ihr Text traegt die
    Zeilen derselben Familien (Quelle: deren TTF-Metadaten)."""
    text = _lizenzdatei(FONT_DIR / "web").read_text(encoding="utf-8")
    erwartet = _copyright_zeilen(FONT_DIR / "geist") | _copyright_zeilen(
        FONT_DIR / "source-serif"
    )
    assert len(erwartet) == 2
    assert sorted(z for z in erwartet if z not in text) == []


def test_lizenzdateien_gehen_ins_wheel():
    """package-data muss die Lizenzdateien einschliessen, sonst fehlen sie im Wheel."""
    tomllib = pytest.importorskip("tomllib")  # ab Python 3.11
    pyproject = tomllib.loads(
        (Path(__file__).parent.parent / "pyproject.toml").read_text(encoding="utf-8")
    )
    muster = pyproject["tool"]["setuptools"]["package-data"]["mn_design_system"]
    paket = Path(__file__).parent.parent / "mn_design_system"
    lizenzen = sorted(
        p.relative_to(paket).as_posix()
        for p in (paket / "fonts").glob("*/*")
        if p.name == "OFL.txt" or p.name.startswith("LICENSE")
    )
    assert len(lizenzen) >= 9, "Untergrenze: die Lizenzdateien wurden gefunden (LP-36)"
    # An den echten Dateien geprueft, nicht am Text der Musterliste (Critic 0.16.0).
    ohne_muster = [d for d in lizenzen if not any(fnmatch(d, m) for m in muster)]
    assert ohne_muster == []
