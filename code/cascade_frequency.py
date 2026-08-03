"""SARCINA 2 (v2.7.38) — frecvența CASCADEI de rupturi pe descoperirea M15_v2. READ-ONLY, fără P&L.

Cât de des se produc DOUĂ sau mai multe rupturi pe aceeași bară (semantica nouă). Distribuția: câte bare cu 1
rupere, cu 2, cu 3, cu N. Și câte rupturi erau PIERDUTE definitiv sub vechea semantică (referințe care rup acum
dar niciodată sub vechea buclă slot-unic + if/elif). GARD 1 neatins (măsurătoare structurală), GARD 2 neatins.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from typing import Any

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
from market_structure import (Block, BreakKind, StructureBreak, StructureLabel, Swing, _mk_break,
                               detect_breaks, detect_swings, label_structure)

REGIMES = ["bear", "bull", "correction"]
EXPECTED_BARS = {"bear": 52_403, "bull": 52_851, "correction": 25_237}


def _old_detect_breaks(close: list[float], swings: list[Swing], n: int) -> list[StructureBreak]:
    """Semantica VECHE: slot unic live_* + if/elif intra-direcție (eșalonare + suprimare)."""
    out: list[StructureBreak] = []
    consumed: set[int] = set()
    for c in range(n):
        lhh = lll = lhl = llh = None
        for s in swings:
            if s.confirmed_idx >= c or s.idx in consumed:
                continue
            if s.label is StructureLabel.HH:
                lhh = s
            elif s.label is StructureLabel.LL:
                lll = s
            elif s.label is StructureLabel.HL:
                lhl = s
            elif s.label is StructureLabel.LH:
                llh = s
        px = close[c]
        if lhh is not None and px > lhh.price:
            out.append(_mk_break(c, BreakKind.BOS_BULL, lhh, px, 0)); consumed.add(lhh.idx)
        elif llh is not None and px > llh.price:
            out.append(_mk_break(c, BreakKind.CHOCH_BULL, llh, px, 0)); consumed.add(llh.idx)
        if lll is not None and px < lll.price:
            out.append(_mk_break(c, BreakKind.BOS_BEAR, lll, px, 0)); consumed.add(lll.idx)
        elif lhl is not None and px < lhl.price:
            out.append(_mk_break(c, BreakKind.CHOCH_BEAR, lhl, px, 0)); consumed.add(lhl.idx)
    return out


def _regime_label(seg: dict[str, Any], i: int) -> str:
    for k in ("regime", "label", "name"):
        v = seg.get(k)
        if isinstance(v, str):
            return v.lower()
    return REGIMES[i]


def main() -> int:
    dfm, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | M15={len(dfm)}")
    if len(dfm) != 130_491:
        print(f"STOP: M15 {len(dfm)}."); return 2
    dfm = dfm.sort_values("time").reset_index(drop=True)
    t_all = dfm["time"].to_numpy()
    segs = [s for s in SM.load_manifest()["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]

    out: dict[str, Any] = {"regimes": {}}
    agg_dist: Counter[int] = Counter()
    tot_new = tot_old = tot_lost = tot_break_bars = tot_cascade_bars = 0
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        sw = label_structure(detect_swings(h, l, [Block(0, n)], k=2))
        new = detect_breaks(c, sw, [Block(0, n)])
        old = _old_detect_breaks(c, sw, n)

        per_bar = Counter(b.idx for b in new)                  # rupturi per bară
        dist = Counter(per_bar.values())                       # câte bare au 1/2/3/... rupturi
        cascade_bars = sum(cnt for k, cnt in dist.items() if k >= 2)
        max_on_bar = max(per_bar.values()) if per_bar else 0
        new_refs = {b.reference_swing.idx for b in new}
        old_refs = {b.reference_swing.idx for b in old}
        lost = len(new_refs - old_refs)                        # referințe care rup acum dar NICIODATĂ sub vechea semantică

        out["regimes"][label] = {
            "n_bars": n, "swings": len(sw), "breaks_new": len(new), "breaks_old": len(old),
            "break_bars": len(per_bar), "cascade_bars_ge2": cascade_bars, "max_breaks_on_one_bar": max_on_bar,
            "dist_breaks_per_bar": {str(k): v for k, v in sorted(dist.items())},
            "refs_lost_forever_under_old": lost}
        agg_dist.update(dist)
        tot_new += len(new); tot_old += len(old); tot_lost += lost
        tot_break_bars += len(per_bar); tot_cascade_bars += cascade_bars
        pct = 100.0 * cascade_bars / len(per_bar) if per_bar else 0.0
        print(f"\n=== {label.upper()} ({n} bare, {len(sw)} swings) ===")
        print(f"  rupturi: nou={len(new)} vechi={len(old)} | bare-cu-rupturi={len(per_bar)} | "
              f"bare-cascadă(≥2)={cascade_bars} ({pct:.2f}%) | max/bară={max_on_bar}")
        print(f"  distribuție rupturi/bară: {dict(sorted(dist.items()))}")
        print(f"  referințe PIERDUTE definitiv sub vechea semantică: {lost}")

    agg_pct = 100.0 * tot_cascade_bars / tot_break_bars if tot_break_bars else 0.0
    out["aggregate"] = {"breaks_new": tot_new, "breaks_old": tot_old, "break_bars": tot_break_bars,
                        "cascade_bars_ge2": tot_cascade_bars, "cascade_bar_fraction": round(agg_pct / 100, 5),
                        "refs_lost_forever_under_old": tot_lost,
                        "dist_breaks_per_bar": {str(k): v for k, v in sorted(agg_dist.items())}}
    print(f"\n########## AGREGAT ##########")
    print(f"  rupturi nou={tot_new} vechi={tot_old} (Δ={tot_new - tot_old}) | pierdute definitiv (vechi)={tot_lost}")
    print(f"  bare cu rupturi={tot_break_bars} | bare-cascadă(≥2)={tot_cascade_bars} = {agg_pct:.3f}% din barele cu rupturi")
    print(f"  distribuție rupturi/bară (agregat): {dict(sorted(agg_dist.items()))}")

    path = os.path.join(_ROOT, "reports", "cascade_frequency_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/cascade_frequency_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
