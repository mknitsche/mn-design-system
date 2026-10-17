"""Vendoring Apache ECharts 6.1.0 (0.17.0): Datei, Hash, Lizenz, Auslieferung.

Das Design-System bringt die Diagramm-Bibliothek selbst mit (Pin + Hash wie das Wheel,
kein CDN, kein Netz beim Seitenbau; dasselbe Muster wie die Schriften unter `fonts/`).
Apache-2.0 verlangt, dass jede weitergegebene Kopie LICENSE und NOTICE mitbringt.

Geprueft wird nicht nur, dass die Dateien da sind, sondern dass `VENDOR.json` die Datei
wirklich beschreibt (Hash), dass die Version aus EINER Quelle kommt (VENDOR.json, nicht
doppelt getippt) und dass das Paket die Dateien auch ausliefert (package-data deckt sie).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import tomllib

import mn_design_system
from mn_design_system.components import web
from mn_design_system.components.web import foundation

_MIN_BYTES = 500_000
_VENDOR_JSON_FELDER = {
    "name",
    "version",
    "datei",
    "sha256",
    "quelle",
    "tarball_integrity",
    "lizenz",
}


def _vendor_dir() -> Path:
    return foundation.vendor_js_dir()


def _vendor_json() -> dict:
    return json.loads((_vendor_dir() / "VENDOR.json").read_text(encoding="utf-8"))


def test_vendor_dir_liegt_im_paket():
    pfad = _vendor_dir()
    paket = Path(mn_design_system.__file__).parent
    assert pfad == paket / "vendor" / "echarts"
    assert pfad.is_dir()


def test_vendor_json_hat_alle_felder_und_stimmige_werte():
    meta = _vendor_json()
    assert _VENDOR_JSON_FELDER <= set(meta), sorted(_VENDOR_JSON_FELDER - set(meta))
    assert meta["name"] == "echarts"
    assert meta["lizenz"] == "Apache-2.0"
    assert re.fullmatch(r"\d+\.\d+\.\d+", meta["version"])
    assert meta["quelle"] == (
        f"https://registry.npmjs.org/echarts/-/echarts-{meta['version']}.tgz"
    )
    assert re.fullmatch(r"sha512-[A-Za-z0-9+/]{86}==", meta["tarball_integrity"])
    assert re.fullmatch(r"[0-9a-f]{64}", meta["sha256"])


def test_js_datei_vorhanden_und_nicht_leer():
    """Untergrenze (LP-36): ein Hash ueber eine leere/abgeschnittene Datei waere
    „gruen“ — der Build ist ueber 500 KB gross."""
    js = _vendor_dir() / _vendor_json()["datei"]
    assert js.is_file()
    assert js.stat().st_size > _MIN_BYTES


def test_js_datei_hat_den_hash_aus_vendor_json():
    meta = _vendor_json()
    js = _vendor_dir() / meta["datei"]
    assert hashlib.sha256(js.read_bytes()).hexdigest() == meta["sha256"]


def test_js_datei_ist_der_common_build_der_pinversion():
    js = (_vendor_dir() / _vendor_json()["datei"]).read_text(encoding="utf-8")
    assert _vendor_json()["datei"] == "echarts.common.min.js"
    assert "Apache Software Foundation" in js[:1200]  # Lizenzkopf des Upstream-Builds


def test_license_ist_apache_2_0_im_wortlaut():
    text = (_vendor_dir() / "LICENSE").read_text(encoding="utf-8")
    assert "Apache License" in text
    assert "Version 2.0" in text
    assert "TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION" in text


def _lizenz_verweise() -> set[str]:
    """Pfade `/licenses/<name>`, auf die der LICENSE-Text des Upstream-Projekts verweist.

    Nicht gemeint sind URLs wie `http://www.apache.org/licenses/LICENSE-2.0`: vor dem
    `/licenses/` einer Paketreferenz steht kein Buchstabe, Ziffer oder Punkt."""
    text = (_vendor_dir() / "LICENSE").read_text(encoding="utf-8")
    return set(re.findall(r"(?<![A-Za-z0-9.])/licenses/([A-Za-z0-9._-]+)", text))


def test_jeder_lizenz_verweis_der_license_datei_liegt_im_vendor_ordner():
    """Die Apache-LICENSE nennt Teile mit eigener Lizenz (d3.js, BSD-3) und verweist auf
    `/licenses/LICENSE-d3`. Der Build enthaelt d3-Code; BSD-3 verlangt, dass der
    Lizenztext bei der Weitergabe mitgeht — ein Verweis ins Leere verletzt das."""
    verweise = _lizenz_verweise()
    assert verweise == {"LICENSE-d3"}, (
        verweise
    )  # Untergrenze: der Verweis wird gefunden
    fehlend = sorted(
        n for n in verweise if not (_vendor_dir() / "licenses" / n).is_file()
    )
    assert not fehlend, f"Lizenzdatei(en) fehlen im Vendor-Ordner: {fehlend}"


def test_d3_lizenz_ist_bsd_3_im_wortlaut():
    text = (_vendor_dir() / "licenses" / "LICENSE-d3").read_text(encoding="utf-8")
    assert "Mike Bostock" in text
    assert "Redistribution and use in source and binary forms" in text
    assert "Neither the name of the author nor the names of contributors" in text


def test_notice_vorhanden_und_nennt_die_asf():
    text = (_vendor_dir() / "NOTICE").read_text(encoding="utf-8")
    assert "Apache ECharts" in text
    assert "The Apache Software Foundation" in text


def test_konstanten_kommen_aus_vendor_json():
    meta = _vendor_json()
    assert foundation.ECHARTS_VERSION == meta["version"]
    assert foundation.ECHARTS_DATEI == meta["datei"]
    assert (foundation.vendor_js_dir() / foundation.ECHARTS_DATEI).is_file()


def test_web_paket_exportiert_die_vendor_api():
    assert web.vendor_js_dir is foundation.vendor_js_dir
    assert web.ECHARTS_DATEI == foundation.ECHARTS_DATEI
    assert web.ECHARTS_VERSION == foundation.ECHARTS_VERSION
    for name in ("vendor_js_dir", "ECHARTS_DATEI", "ECHARTS_VERSION"):
        assert name in web.__all__


def test_package_data_liefert_die_vendor_dateien_aus():
    """Das Wheel enthaelt nur, was `package-data` nennt. Jede Vendor-Datei muss von
    mindestens einem Muster gefunden werden (setuptools globbt relativ zum Paket)."""
    pyproject = Path(mn_design_system.__file__).parents[1] / "pyproject.toml"
    muster = tomllib.loads(pyproject.read_text(encoding="utf-8"))["tool"]["setuptools"][
        "package-data"
    ]["mn_design_system"]
    paket = Path(mn_design_system.__file__).parent
    abgedeckt = {p for m in muster for p in paket.glob(m) if p.is_file()}
    erwartet = {
        _vendor_dir() / "VENDOR.json",
        _vendor_dir() / "LICENSE",
        _vendor_dir() / "NOTICE",
        _vendor_dir() / "licenses" / "LICENSE-d3",
        _vendor_dir() / _vendor_json()["datei"],
    }
    assert erwartet <= abgedeckt, sorted(str(p) for p in erwartet - abgedeckt)
