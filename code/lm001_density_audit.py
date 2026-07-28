"""LM-001 TEMPORAL DENSITY AUDIT — Mandat 5.5 Sarcina 1.

Suprapunerea ferestrelor de orizont (20 bare) produce autocorelație în seria net_R.
Se NUMĂRĂ GEOMETRIC (suprapunere de indici), fără P&L, fără randamente. Indicii evenimentelor
provin din același detector geometric (structural, deja permis); DOAR numărarea suprapunerii e
livrabilul aici. Zero backtest, zero interogare de preț pentru performanță.

Populația: cele 21.048 evenimente = wick-sweep-uri valide, filtrate la [10,1 ; 65,0] pips
(displacement_filter + rejection_ceiling, manifest v2.5.6). Orizont H=20 bare (london=5h).
Două evenimente se suprapun temporal dacă |c_i − c_j| < H (ferestrele [c, c+H] se intersectează),
în ACELAȘI segment de descoperire (blocurile sunt separate de benzi de carantină ≫ 20 bare).
"""

from __future__ import annotations

import bisect
import json
import os
import sys
from collections import Counter
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_HERE, os.path.join(_ROOT, "edge_research")):
    if p not in sys.path:
        sys.path.insert(0, p)

import split_manifest as SM  # type: ignore[import-not-found]  # noqa: E402
from market_structure import Block, detect_swings, label_structure  # noqa: E402
from liquidity_mechanics import PoolSide, PoolTier, build_pools, detect_sweeps  # noqa: E402

TICK = 0.1
K = 2
H = 20                       # orizontul LM-001 (bare)
FILTER_LO, FILTER_HI = 10.1, 65.0


def _session(epoch: int) -> str:
    h = pd.Timestamp(epoch, unit="s", tz="UTC").hour
    return "asia" if h < 8 else "london" if h < 13 else "ny" if h < 21 else "late"


def collect_events() -> tuple[list[dict[str, Any]], int]:
    """(c local în segment, seg_idx, regime, session, pips) pentru evenimentele filtrate [10.1,65]."""
    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]
    df = pd.read_csv(os.path.join(_ROOT, "data", "market", "OANDA_XAUUSD_M15.csv"))
    df = df.sort_values("time").reset_index(drop=True)
    t = df["time"].to_numpy()

    evs: list[dict[str, Any]] = []
    horizon_excluded = 0
    for si, seg in enumerate(segs):
        s, e = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        regime = seg["type"]
        sub = df[(t >= s) & (t < e)].reset_index(drop=True)
        o = sub["open"].to_numpy(); hi = sub["high"].to_numpy()
        lo = sub["low"].to_numpy(); cl = sub["close"].to_numpy()
        tt = sub["time"].to_numpy()
        n = len(sub)
        blocks = [Block(0, n)]
        swings = label_structure(detect_swings(hi.tolist(), lo.tolist(), blocks, k=K))
        pools = build_pools(swings, PoolTier.EXTERNAL)
        sweeps = detect_sweeps(hi.tolist(), lo.tolist(), cl.tolist(), pools, blocks,
                               require_close_back_inside=True)
        for sw in sweeps:
            c = sw.idx
            if c + 1 >= n:
                continue                                 # fără next-open (spec §D)
            dist = (o[c + 1] - lo[c]) if sw.pool.side is PoolSide.BELOW else (hi[c] - o[c + 1])
            pips = float(dist) / TICK
            if not (FILTER_LO <= pips <= FILTER_HI):
                continue                                 # filtrul [10.1, 65.0]
            if c + H >= n:
                horizon_excluded += 1                    # exit c+H iese din segment (disclosure)
            evs.append({"c": c, "seg": si, "regime": regime, "session": _session(int(tt[c]))})
    return evs, horizon_excluded


def _degrees(cs: list[int]) -> list[int]:
    """Grad de suprapunere per eveniment: câte ALTE evenimente au |c_i − c_j| < H (același segment)."""
    cs = sorted(cs)
    out = []
    for c in cs:
        lo = bisect.bisect_left(cs, c - (H - 1))
        hi = bisect.bisect_right(cs, c + (H - 1))
        out.append((hi - lo) - 1)                        # exclude self
    return out


def _summ(degrees: list[int]) -> dict[str, Any]:
    n = len(degrees)
    if n == 0:
        return {"n": 0}
    d = np.asarray(degrees)
    overl = int((d >= 1).sum())
    return {"n": n,
            "avg_concurrent": float(d.mean() + 1.0),     # inclusiv el însuși
            "pct_overlapping": 100.0 * overl / n,
            "degree_mean": float(d.mean()), "degree_max": int(d.max()),
            "degree_p50": int(np.percentile(d, 50)), "degree_p90": int(np.percentile(d, 90)),
            "degree_hist": {str(k): int(v) for k, v in sorted(Counter(d.tolist()).items())}}


def main() -> int:
    evs, hz = collect_events()
    # grade calculate PER SEGMENT (suprapunerea nu traversează carantina)
    by_seg: dict[int, list[int]] = {}
    for ev in evs:
        by_seg.setdefault(ev["seg"], []).append(ev["c"])
    seg_degrees: dict[int, list[int]] = {si: _degrees(cs) for si, cs in by_seg.items()}
    # atașează gradul înapoi la fiecare eveniment (în ordinea sortată pe c)
    for si, cs in by_seg.items():
        degs = seg_degrees[si]
        idxs = [ev for ev in evs if ev["seg"] == si]
        idxs.sort(key=lambda ev: ev["c"])
        for ev, dg in zip(idxs, degs):
            ev["degree"] = dg

    all_deg = [ev["degree"] for ev in evs]
    regimes = ["bear", "bull", "correction"]
    sessions = ["asia", "london", "ny", "late"]

    print("=" * 84)
    print(f"LM-001 TEMPORAL DENSITY AUDIT — H={H} bars, population={len(evs)} (filter [10.1,65.0] pips)")
    print(f"horizon-boundary exclusions (c+H exits segment, disclosed): {hz}")
    print("=" * 84)

    def line(name: str, degs: list[int]) -> None:
        s = _summ(degs)
        if s["n"] == 0:
            print(f"  {name:12} n=0"); return
        print(f"  {name:12} n={s['n']:6} | avg_concurrent={s['avg_concurrent']:5.2f} | "
              f"overlapping={s['pct_overlapping']:5.1f}% | degree mean={s['degree_mean']:4.2f} "
              f"p50={s['degree_p50']} p90={s['degree_p90']} max={s['degree_max']}")

    print("\n[AGGREGATE]")
    line("ALL", all_deg)
    print("  degree histogram:", _summ(all_deg)["degree_hist"])
    print("\n[BY REGIME]")
    for r in regimes:
        line(r, [ev["degree"] for ev in evs if ev["regime"] == r])
    print("\n[BY SESSION]")
    for ss in sessions:
        line(ss, [ev["degree"] for ev in evs if ev["session"] == ss])

    rec = {"H": H, "population": len(evs), "horizon_boundary_excluded": hz,
           "aggregate": _summ(all_deg),
           "by_regime": {r: _summ([ev["degree"] for ev in evs if ev["regime"] == r]) for r in regimes},
           "by_session": {ss: _summ([ev["degree"] for ev in evs if ev["session"] == ss]) for ss in sessions}}
    out = os.path.join(_HERE, "..", "edge_research", "lm001_density_audit_results.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2)
    print("\nrecord ->", os.path.relpath(out, _ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
