"""Waechter: die EINE LaTeX-Schicht des Pakets ist gueltig, vollstaendig und wird ausgeliefert.

Schutzgut: falsche Information nach aussen und unbemerkter Stillstand. Bis 0.20.0 gab es
``dist/latex/tokens.tex`` — mit ``#`` in ``\\def`` (TeX-Parameterzeichen), Makronamen mit
Ziffern und ausserhalb des Wheels, also unbenutzbar; die PDF-Kette der Konsumenten griff
deshalb auf eigene, veraltete Farben und ueber Fontconfig auf die Web-Schriften
(``fonts/web/*.woff2``) und brach ab. Seit 0.21.0 ist ``mn-design.sty`` die einzige
LaTeX-Ausgabe; die Kompilierproben fahren die ``xelatex`` aus dem PATH des Aufrufers.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import tomllib

from mn_design_system import tokens
from mn_design_system.fonts import FONT_DIR
from mn_design_system.latex import LATEX_DIR, STY

ROOT = Path(__file__).resolve().parent.parent
_DEF = re.compile(r"\\definecolor\{([^}]+)\}\{HTML\}\{([^}]*)\}")
_XELATEX = shutil.which("xelatex")
braucht_xelatex = pytest.mark.skipif(
    _XELATEX is None,
    reason="xelatex fehlt auf diesem Host (CI) — Kompilierprobe nur lokal",
)


def _sty() -> str:
    return STY.read_text(encoding="utf-8")


def _kompiliere(
    ordner: Path, koerper: str, *, fontdir: str | None
) -> subprocess.CompletedProcess:
    kopf = "" if fontdir is None else f"\\def\\mndsfontdir{{{fontdir}}}"
    (ordner / "probe.tex").write_text(
        f"\\documentclass{{article}}{kopf}\\usepackage{{mn-design}}\n"
        f"\\begin{{document}}{koerper}\\end{{document}}\n",
        encoding="utf-8",
    )
    umgebung = {**os.environ, "TEXINPUTS": f"{LATEX_DIR}//:"}
    return subprocess.run(
        [_XELATEX, "-interaction=nonstopmode", "-halt-on-error", "probe.tex"],
        cwd=ordner,
        capture_output=True,
        text=True,
        timeout=180,
        env=umgebung,
        check=False,
    )


def test_eine_latex_schicht_im_paket_und_im_wheel() -> None:
    assert STY.is_file(), STY
    assert STY.parent == LATEX_DIR
    daten = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    muster = daten["tool"]["setuptools"]["package-data"]["mn_design_system"]
    assert "latex/*.sty" in muster, (
        "die .sty fehlt in package-data — sie kaeme nicht ins Wheel"
    )
    # Nur EIN LaTeX-Ort: die alte Token-Datei und der Platzhalter sind weg.
    assert not (ROOT / "dist" / "latex").exists()
    assert not (ROOT / "mn_design_system" / "components" / "latex").exists()


def test_jedes_farb_token_ist_eine_gueltige_latex_farbe() -> None:
    farben = dict(_DEF.findall(_sty()))
    erwartet = {
        "mn-" + k.replace(".", "-"): v[1:].upper()
        for k, v in tokens.TOKENS.items()
        if k.startswith("color.")
        and isinstance(v, str)
        and re.fullmatch(r"#[0-9A-Fa-f]{6}", v)
    }
    # Untergrenze (LP-36): ohne Farben waere "alle gueltig" trivial wahr.
    assert len(erwartet) > 100
    assert farben == erwartet


@pytest.mark.parametrize(
    "alias",
    [
        "mnText",
        "mnHOne",
        "mnHTwo",
        "mnAccent",
        "mnAccentSoft",
        "mnSurfaceSubtle",
        "mnGreySeven",
        "mnGreyFive",
        "mnGreyThree",
        "mnBrand",
        "mnStatusSuccess",
        "mnStatusWarning",
        "mnStatusError",
    ],
)
def test_semantische_farben_der_dokumente_sind_definiert(alias: str) -> None:
    ziel = re.search(rf"\\colorlet\{{{alias}\}}\{{([^}}]+)\}}", _sty())
    assert ziel, f"{alias} fehlt"
    assert ziel.group(1) in dict(_DEF.findall(_sty())), f"{alias} zeigt auf keine Farbe"


def test_jedes_druck_token_ist_ueber_mntoken_erreichbar() -> None:
    namen = set(re.findall(r"\\csname mn@token@([^\\]+)\\endcsname\{", _sty()))
    erwartet = {
        k for k in tokens.TOKENS if k.split(".")[0] in ("font", "space", "stroke")
    }
    assert len(erwartet) > 50
    assert namen == erwartet


def test_paket_kennung_traegt_datum_und_version() -> None:
    """LaTeX erwartet ``JJJJ/MM/TT vX.Y.Z`` — ohne Datum bricht das Einbinden."""
    daten = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = re.escape(daten["project"]["version"])
    assert re.search(
        rf"\\ProvidesPackage\{{mn-design\}}\[\d{{4}}/\d{{2}}/\d{{2}} v{version} ",
        _sty(),
    )


def test_jede_genannte_schriftdatei_existiert() -> None:
    gezaehlt = 0
    for ordner, optionen in re.findall(
        r"Path=\\mndsfontdir/([^/]+)/, Extension=(\.\w+)", _sty()
    ):
        assert (FONT_DIR / ordner).is_dir(), ordner
        assert optionen in (".ttf", ".otf")
        gezaehlt += 1
    assert gezaehlt >= 6
    for datei in (
        "geist/Geist-Regular.ttf",
        "geist/Geist-Bold.ttf",
        "source-serif/SourceSerif4-Italic.ttf",
        "source-serif/SourceSerif4-BoldItalic.ttf",
        "jetbrains-mono/JetBrainsMono-Regular.ttf",
        "stix-two/STIXTwoMath-Regular.otf",
        "noto/NotoSansSymbols2-Regular.ttf",
    ):
        assert (FONT_DIR / datei).is_file(), datei


@braucht_xelatex
def test_kompiliert_und_bettet_nur_paket_schriften_ein(tmp_path: Path) -> None:
    lauf = _kompiliere(
        tmp_path,
        r"{\color{mnHOne}\textbf{T}} x \textit{k} \texttt{m} $E=mc^2$ $\square$ $\boxtimes$ ✓ ✗ α Ω"
        r" \mnToken{font.size.body}",
        fontdir=str(FONT_DIR),
    )
    assert lauf.returncode == 0, lauf.stdout[-2000:]
    protokoll = (tmp_path / "probe.log").read_text(encoding="utf-8", errors="replace")
    assert "Missing character" not in protokoll, (
        "ein Zeichen fiel still weg (Schrift fuehrt es nicht)"
    )
    schriften = subprocess.run(
        ["pdffonts", "probe.pdf"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()[2:]
    namen = {z.split()[0].split("+", 1)[-1] for z in schriften}
    for name in (
        "Geist-Regular",
        "Geist-Bold",
        "SourceSerif4-Italic",
        "JetBrainsMono-Regular",
        "NotoSansSymbols2-Regular",
    ):
        assert name in namen, sorted(namen)
    assert any(n.startswith("STIXTwoMath") for n in namen), sorted(namen)
    fremd = sorted(
        n
        for n in namen
        if not re.match(
            r"(Geist|SourceSerif4|JetBrainsMono|STIXTwo|NotoSansSymbols2)", n
        )
    )
    assert not fremd, f"Schriften ausserhalb des Pakets: {fremd}"


@braucht_xelatex
@pytest.mark.parametrize("fontdir", [None, ""], ids=["nicht-gesetzt", "leer"])
def test_ohne_schriftordner_bricht_das_paket_laut(
    tmp_path: Path, fontdir: str | None
) -> None:
    lauf = _kompiliere(tmp_path, "x", fontdir=fontdir)
    assert lauf.returncode != 0
    # Die EIGENE Meldung des Pakets — nicht nur das Wort "mndsfontdir", das auch in einem
    # "Undefined control sequence" stuende (Mutation Diff-Pruefer cld1-S125).
    erwartet = "ist nicht gesetzt" if fontdir is None else "ist leer"
    assert "mndsfontdir ist" in lauf.stdout and erwartet in lauf.stdout, lauf.stdout[
        -1500:
    ]


@braucht_xelatex
def test_unbekanntes_token_bricht_laut(tmp_path: Path) -> None:
    lauf = _kompiliere(
        tmp_path, r"\mnToken{font.size.gibtsnicht}", fontdir=str(FONT_DIR)
    )
    assert lauf.returncode != 0
    assert "Unbekanntes Token" in lauf.stdout
