"""Rezolvarea căilor. Acest modul NU citește date de piață — doar rezolvă rădăcini.

Convenția de localizare a datelor este cea deja folosită în laborator
(`code/mtf.py`): variabila de mediu AI_QUANT_DATA_DIR are prioritate, altfel
<LAB_ROOT>/data/market.
"""

from __future__ import annotations

import os
from pathlib import Path

VE_ROOT = Path(__file__).resolve().parents[1]          # <lab>/validation_engine
LAB_ROOT = VE_ROOT.parent                              # <lab>

SPEC_SCHEMA_PATH = VE_ROOT / "SPEC_SCHEMA_v1.0.json"
CAPABILITIES_PATH = VE_ROOT / "capabilities.json"
RUNS_DIR = VE_ROOT / "runs"
CLARIFICATIONS_DIR = VE_ROOT / "clarifications"


def data_roots() -> tuple[Path, ...]:
    """Rădăcinile considerate 'date de piață' de garda de acces.

    Orice deschidere de fișier sub una dintre ele este o accesare de date.
    Se includ atât calea canonică din repository, cât și eventuala suprascriere
    prin AI_QUANT_DATA_DIR, pentru ca garda să nu poată fi ocolită prin mediu.
    """
    roots = [LAB_ROOT / "data"]
    env = os.environ.get("AI_QUANT_DATA_DIR")
    if env:
        roots.append(Path(env))
    out: list[Path] = []
    for r in roots:
        try:
            rr = r.resolve()
        except OSError:
            rr = r
        if rr not in out:
            out.append(rr)
    return tuple(out)
