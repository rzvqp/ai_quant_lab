"""Selectie determinista `V4_4_FRESH_BLIND14`, conform protocolului comis la `e8ce481` + `7a2c93d`.

★ CITESTE DOAR coloana `time`. NU atinge OHLC la selectie. NU importa niciun detector.
Etichetele nu exista. Selectia e oarba prin CONSTRUCTIE fata de semantica SI fata de ambele detectoare.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
from typing import Any

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "blind_batch_03"))

from edge_research._common import (  # noqa: E402
    PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC, load,
)
from select_batch_03 import (  # noqa: E402
    BLOCKS_EPOCH, C, EDGE, GAP_MAX, INDEP, SEP, Stream, build_exclusions,
)

SEED_STRING = b"RANGE_V4_4_FRESH_BLIND14|3bb61cf|845a03c|N14"
SEED = hashlib.sha256(SEED_STRING).digest()
LENGTH_QUOTA = [(480, 4), (288, 5), (96, 5)]          # descrescator, total 14
ESCROW_DIR = os.environ.get("ESCROW_DIR",
                            os.path.join(os.path.expanduser("~"), "escrow_red_team"))
MB3_SELECTION = os.path.join(ESCROW_DIR, "selection_batch_03.json")


def main() -> int:
    d, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    T = d["time"].to_numpy().astype("int64")           # ★ DOAR `time`
    n = len(T)
    blocks = []
    for nm, a, b in BLOCKS_EPOCH:
        i = np.nonzero((T >= a) & (T <= b))[0]
        blocks.append((nm, int(i[0]), int(i[-1])))

    ex, acc = build_exclusions(T, n)                   # E1 + E2/E3 + E6
    before = int(ex.sum())
    # E7 — TOATE cele 48 de ferestre MB3. Coordonate NON-semantice din artefactul propriu de
    # selectie; niciun payload de etichete deschis, niciun grafic MB3 privit, iar pentru
    # MB3-025..048 nici nu exista etichete. Raman SEALED_FUTURE_EVIDENCE.
    mb3 = json.load(io.open(MB3_SELECTION, encoding="utf-8"))
    for w in mb3["windows"]:
        ex[max(0, w["r_start"] - INDEP):min(n, w["r_end"] + INDEP)] = True
    acc["E7_MB3_all_48_windows"] = int(ex.sum()) - before
    acc["TOTAL"] = int(ex.sum())

    gaps = np.diff(T)
    cache: dict[tuple[int, int], list[int]] = {}

    def eligible(L: int, bi: int) -> list[int]:
        if (L, bi) not in cache:
            _, b0, b1 = blocks[bi]
            cache[(L, bi)] = [s for s in range(b0 + EDGE + C, b1 - EDGE - L - C + 1)
                              if not ex[s - C:s + L + C].any()
                              and gaps[s - C:s + L + C - 1].max() <= GAP_MAX]
        return cache[(L, bi)]

    # blocuri ELIGIBILE = cele cu pozitii la lungimea minima; B3 e epuizat si cade de la sine
    cap = {bi: len(eligible(96, bi)) for bi in range(len(blocks))}
    eligible_bi = [bi for bi in cap if cap[bi] > 0]
    exhausted = [blocks[bi][0] for bi in cap if cap[bi] == 0]
    order = sorted(eligible_bi, key=lambda b: -cap[b])          # capacitate DESCRESCATOARE
    quota = {bi: q for bi, q in zip(order, ([5, 5, 4] if len(order) == 3 else []))}
    if len(order) != 3:
        print(f"FB14_BLOCKED_UNEXPECTED_ELIGIBLE_BLOCKS={len(order)}")
        return 1

    # matricea bloc x lungime — round-robin determinist (AMENDAMENT 1)
    plan: dict[tuple[int, int], int] = {(bi, L): 0 for bi in order for L, _ in LENGTH_QUOTA}
    left = dict(quota)
    p = 0
    for L, q in LENGTH_QUOTA:
        for _ in range(q):
            for _try in range(len(order)):
                bi = order[p % len(order)]
                p += 1
                if left[bi] > 0:
                    plan[(bi, L)] += 1
                    left[bi] -= 1
                    break
    assert sum(plan.values()) == 14

    st = Stream(SEED)
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    def free(L: int, bi: int) -> list[int]:
        return [s for s in eligible(L, bi)
                if not any(s - C < w["r_end"] + SEP and w["r_start"] - SEP < s + L + C
                           for w in accepted)]

    for L, _ in LENGTH_QUOTA:                       # lungimi descrescatoare
        for bi in order:                            # blocuri, capacitate descrescatoare
            for _k in range(plan[(bi, L)]):
                pool = free(L, bi)
                if not pool:
                    print(f"FB14_BLOCKED_NO_FEASIBLE_{blocks[bi][0]}_L{L}")
                    return 1
                s = pool[st.next_u64() % len(pool)]
                accepted.append({"block": blocks[bi][0], "L": L, "start": s, "end": s + L,
                                 "r_start": s - C, "r_end": s + L + C,
                                 "draw": st.draws, "pool": len(pool)})

    accepted.sort(key=lambda w: (w["start"],))       # ordine TEMPORALA, non-semantica
    for i, w in enumerate(accepted, 1):
        w["id"] = f"FB14-{i:03d}"

    out = {
        "batch_id": "V4_4_FRESH_BLIND14",
        "epistemic_status": "FRESH_BLIND14_CONFIRMATION",
        "protocol_commits": ["e8ce481", "7a2c93d"],
        "authority": {"rt_audit": "845a03c", "v4_4_implementation": "3bb61cf",
                      "config_id_prefix": "23d98c07"},
        "seed_string": SEED_STRING.decode(), "seed_sha256": SEED.hex(),
        "exclusion_accounting": acc, "n_canonical": n,
        "blocks_exhausted": exhausted,
        "block_quota": {blocks[bi][0]: quota[bi] for bi in order},
        "plan_block_by_length": {blocks[bi][0]: {str(L): plan[(bi, L)] for L, _ in LENGTH_QUOTA}
                                 for bi in order},
        "total_draws": st.draws, "technical_replacements": rejected,
        "windows": accepted,
    }
    txt = json.dumps(out, indent=2, ensure_ascii=False) + chr(10)
    io.open(os.path.join(ESCROW_DIR, "selection_fb14.json"), "w",
            encoding="utf-8", newline=chr(10)).write(txt)
    print("blocuri epuizate      :", exhausted or "niciunul")
    print("exclus TOTAL          :", acc["TOTAL"], f"({100*acc['TOTAL']/n:.1f}%)")
    print("cote pe bloc          :", out["block_quota"])
    print("plan bloc x lungime   :", out["plan_block_by_length"])
    print("selectate             :", len(accepted), "| trageri:", st.draws)
    print("selection_sha256      :", hashlib.sha256(txt.encode("utf-8")).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
