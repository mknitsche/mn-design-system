"""Waechter: package.json und pyproject.toml tragen dieselbe Version.

Schutzgut: falsche Information. package.json stand auf 0.1.0, waehrend das Paket bei
0.19.0 war; npm-Konsumenten und Werkzeuge lesen diese Zahl.
"""

from __future__ import annotations

import json
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parent.parent


def test_package_json_version_gleich_pyproject() -> None:
    py = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]["version"]
    npm = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]
    assert py, "pyproject.toml traegt keine Version"
    assert npm == py, f"package.json {npm} != pyproject.toml {py}"
