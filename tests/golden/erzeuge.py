"""Schreibt ``0_23_0.json``. NUR gegen v0.23.0 ausfuehren (siehe faelle.py)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from faelle import FAELLE, GOLDEN

GOLDEN.write_text(
    json.dumps({n: f() for n, f in FAELLE.items()}, ensure_ascii=False, indent=1)
    + "\n",
    encoding="utf-8",
)
print(f"{len(FAELLE)} Faelle -> {GOLDEN}")
