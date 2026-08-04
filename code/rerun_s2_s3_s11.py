"""SARCINA 3 — re-rularea S2/S3/S11 sub semantica de rupturi VECHE vs NOUĂ (cascadă).

Corecție de EXECUȚIE (Statistician: NU consumă familia). Pre-angajament: scop FIX (S2/S3/S11), setări IDENTICE
(descoperirea M15_v2, per regim `[Block(0,n)]`, k=2, orizont GRUPA A=20, net_R Open-R = ieșire pură pe timp la
entry+20), rezultatul nou ÎNLOCUIEȘTE vechiul în ORICE direcție (inclusiv mai prost), numărători VECHI vs NOI
obligatorii, NIMIC ALTCEVA schimbat. Singura diferență: `detect_breaks` (vechi = slot-unic + if/elif; nou =
cascadă v2.7.38). Semantica nouă a schimbat MULȚIMEA de rupturi (542 apărute pierdute definitiv + cele întârziate
mutate pe bara reală) → apar setup-uri GENUIN noi, nu doar deplasare de timing.

GARD 1 ridicat EXCLUSIV pentru rulare (P&L: net_R). GARD 2 neatins. Fără p-value, fără verdict — triaj descriptiv.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Callable, Sequence

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT, os.path.join(_ROOT, "edge_research")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from edge_research._common import PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC, load
import split_manifest as SM  # type: ignore[import-not-found]
import trading_strategies as TS
from market_structure import Block, StructureBreak, Swing, detect_breaks as NEW_BREAKS
from cascade_frequency import _old_detect_breaks

REGIMES = ["bear", "bull", "correction"]
EXPECTED_BARS = {"bear": 52_403, "bull": 52_851, "correction": 25_237}
N_MIN = 25
StratFn = Callable[..., list[Any]]


def _old_breaks_blocks(close: Sequence[float], swings: Sequence[Swing], blocks: Sequence[Block]) -> list[StructureBreak]:
    """Adaptor la semnătura `detect_breaks(close, swings, blocks)` — un singur bloc [0,n) per regim (block_index 0)."""
    return _old_detect_breaks(list(close), list(swings), blocks[-1].end)


def _net_R_rows(sigs: list[Any], o: list[float], c: list[float], n: int, year: np.ndarray,
                label: str) -> list[tuple[int, str, float]]:
    """net_R Open-R: intrare open[entry], IEȘIRE PURĂ PE TIMP la entry+GRUPA A (=20), net_R via trading_strategies."""
    rows: list[tuple[int, str, float]] = []
    for s in sigs:
        ei = min(s.entry_idx + TS.HORIZON_GROUP_A, n - 1)
        r = TS.net_R(s, float(o[s.entry_idx]), float(c[ei]))
        rows.append((int(year[s.entry_idx]), label, float(r)))
    return rows


def _summ(rows: list[tuple[int, str, float]]) -> dict[str, Any]:
    rr = [r for (_y, _l, r) in rows]
    n = len(rr)
    if n == 0:
        return {"n": 0, "net_R": 0.0, "mean_R": None, "winrate": None,
                "positive_years": 0, "eligible_years": 0, "positive_regimes": 0}
    arr = np.asarray(rr)
    by_year: dict[int, list[float]] = {}
    by_reg: dict[str, list[float]] = {}
    for (y, l, r) in rows:
        by_year.setdefault(y, []).append(r); by_reg.setdefault(l, []).append(r)
    elig = {y: v for y, v in by_year.items() if len(v) >= N_MIN}
    pos_y = sum(1 for v in elig.values() if sum(v) > 0)
    pos_r = sum(1 for v in by_reg.values() if sum(v) > 0)
    return {"n": n, "net_R": round(float(arr.sum()), 2), "mean_R": round(float(arr.mean()), 4),
            "winrate": round(float((arr > 0).mean()), 4),
            "positive_years": pos_y, "eligible_years": len(elig), "positive_regimes": pos_r,
            "by_regime_netR": {k: round(float(sum(v)), 2) for k, v in by_reg.items()}}


def main() -> int:
    print(f"loader v6 | re-rulare S2/S3/S11 | k=2 GRUPA_A={TS.HORIZON_GROUP_A} N_MIN={N_MIN}")
    dfm, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    if len(dfm) != 130_491:
        print(f"STOP: M15 {len(dfm)}."); return 2
    dfm = dfm.sort_values("time").reset_index(drop=True)
    t_all = dfm["time"].to_numpy()
    segs = [s for s in SM.load_manifest()["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]

    strategies: list[tuple[str, StratFn]] = [("S2", TS.detect_s2), ("S3", TS.detect_s3), ("S11", TS.detect_s11)]
    acc: dict[str, dict[str, list[tuple[int, str, float]]]] = {
        name: {"old": [], "new": []} for name, _ in strategies}
    breakset = {"old": 0, "new": 0, "refs_lost": 0}

    for i, seg in enumerate(segs):
        label = REGIMES[i]
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        year = pd.to_datetime(sub["time"], unit="s", utc=True).dt.year.to_numpy()
        blocks = [Block(0, n)]

        # mecanism: mulțimea de rupturi vechi vs nou (referințe DISTINCTE care rup acum dar niciodată sub vechi)
        sw = TS._labeled_swings(h, l, blocks, TS.K_DEFAULT)
        nb = NEW_BREAKS(c, sw, blocks); ob = _old_breaks_blocks(c, sw, blocks)
        breakset["new"] += len(nb); breakset["old"] += len(ob)
        breakset["refs_lost"] += len({b.reference_swing.idx for b in nb} - {b.reference_swing.idx for b in ob})

        for variant, patch in (("old", _old_breaks_blocks), ("new", NEW_BREAKS)):
            setattr(TS, "detect_breaks", patch)                 # DOAR detect_breaks diferă; restul IDENTIC
            for name, fn in strategies:
                sigs = fn(o, h, l, c, blocks)
                acc[name][variant].extend(_net_R_rows(sigs, o, c, n, year, label))
        setattr(TS, "detect_breaks", NEW_BREAKS)                # restaurează starea reală a modulului

    out: dict[str, Any] = {"note": "descriptive; execution correction (NOT family-consuming); no p-value; no verdict",
                           "break_set": breakset, "strategies": {}}
    print(f"\n########## MULȚIMEA DE RUPTURI (mecanism) ##########")
    print(f"  rupturi nou={breakset['new']} vechi={breakset['old']} (Δ={breakset['new']-breakset['old']}) | "
          f"referințe apărute (pierdute definitiv sub vechi)={breakset['refs_lost']}")
    for name, _ in strategies:
        old = _summ(acc[name]["old"]); new = _summ(acc[name]["new"])
        out["strategies"][name] = {"old": old, "new": new}
        print(f"\n########## {name} — VECHI vs NOU (setări identice, doar detect_breaks) ##########")
        for tag, m in (("VECHI", old), ("NOU", new)):
            if m["n"] == 0:
                print(f"  {tag:5s} n=0"); continue
            print(f"  {tag:5s} n={m['n']:4d} netR={m['net_R']:+.2f} mean={m['mean_R']:+.4f} WR={m['winrate']} "
                  f"| ani+={m['positive_years']}/{m['eligible_years']} reg+={m['positive_regimes']}/3 "
                  f"| {m['by_regime_netR']}")
        print(f"  Δ n={new['n']-old['n']:+d}  Δ netR={new['net_R']-old['net_R']:+.2f}")

    path = os.path.join(_ROOT, "reports", "rerun_s2_s3_s11_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/rerun_s2_s3_s11_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
