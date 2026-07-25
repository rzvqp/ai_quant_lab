"""OFFICIAL — execuția `matched_null@v1` cu parametrii oficiali DC-0004, pe fereastra
DESCHISĂ (in-sample). Distinct de harness-ul de CALIBRARE.

Parametri oficiali DC-0004: B=200000, `seed_policy=derived_from_spec_hash`, tail=left,
preserve=session, statistic=mean. Ordinea celulelor = ordinea declarată în specificație.
Holdout NEATINS. Rezultatul este in-sample; metoda rămâne `UNVALIDATED` până la F6,
deci acest rezultat este provizoriu (nu o promovare de protocol).
"""

from __future__ import annotations

import hashlib
import json

from ..calibration.reproduce_obs0012 import build_open_cells
from ..methods import matched_null
from .. import paths

B_OFFICIAL = 200000

# Ordinea DECLARATĂ a celulelor eligibile în DC-0004 (secțiunea family / cells).
SPEC_CELL_ORDER = [("up", "asia"), ("down", "asia"), ("up", "london"),
                   ("down", "london"), ("up", "ny"), ("down", "ny")]


def _dc0004_spec_hash() -> str:
    raw = (paths.VE_ROOT / "tests" / "fixtures" / "reference_spec_dc0004.json").read_bytes()
    return hashlib.sha256(raw).hexdigest()


def _derived_seed(spec_sha: str, test_id: str) -> int:
    h = hashlib.sha256(f"{spec_sha}||{test_id}".encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def official_run() -> dict:
    cells_by_key, obs_order, journal = build_open_cells()
    cells = [cells_by_key[k] for k in SPEC_CELL_ORDER if k in cells_by_key]

    spec_sha = _dc0004_spec_hash()
    # OFICIAL: semințe INDEPENDENTE per celulă, derivate din hash — INDEPENDENT DE ORDINE.
    # Ordinea celulelor (artefact obs) NU influențează rezultatul oficial.
    per_cell = {c["cell_id"]: _derived_seed(spec_sha, f"T1_matched_null_k6||{c['cell_id']}")
                for c in cells}
    results = matched_null.run(cells, B=B_OFFICIAL, tail="left", statistic="mean",
                               per_cell_seeds=per_cell)

    return {
        "mode": "OFFICIAL",
        "official": True,
        "method_calibration_status": "UNVALIDATED",
        "note": "Rezultat oficial in-sample cu parametrii DC-0004 (B=200000, seed derivat per "
                "celulă, independent de ordine). Metoda e UNVALIDATED până la F6; rezultat "
                "provizoriu. Holdout neatins.",
        "B": B_OFFICIAL,
        "seed_policy": "derived_from_spec_hash (per celulă, independent de ordine)",
        "spec_sha256": spec_sha,
        "per_cell_seeds": per_cell,
        "results": [{"cell": r["cell_id"], "n": r["n"], "observed": r["observed"],
                     "p": round(r["p"], 6), "mc_ci95": r["mc_ci95"], "seed": r["seed"]} for r in results],
        "max_ts_read": journal.max_ts_by_source(),
        "sealed_window_touched": journal.sealed_window_touched(),
    }
