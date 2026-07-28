"""LM-001 GEOMETRY AUDIT — Mandate 5.1 Step 1 (STAT-LM001-GEOMETRY-MK03-MK04-v1.0).

Măsoară GEOMETRIA wick-sweep-urilor LM-001 pe cele 130.491 bare de descoperire
M15_v2. Distanța în pips de la intrarea next-open (`open[c+1]`) până la extremul
fitilului de manipulare (`low[c]` BELOW / `high[c]` ABOVE), pentru fiecare wick-sweep
valid la închiderea barei c (D6), pe bazine din swing-uri CLASIFICATE (D1/D2/D4/D5/D7).

INTERDICȚII (spec §F): fără P&L, fără tranzacții, fără optimizare, fără praguri
înghețate. `detect_breaks` NU e apelat (bug de re-armare izolat). Numere de geometrie.

Mascare: `edge_research/split_manifest.py` (coordonate verbatim) + convenția semi-deschisă
`[start_epoch, end_epoch)` ratificată (Mandat 3.10) → 52.403/52.851/25.237 = 130.491.
Intrarea c+1 e validă DOAR dacă c+1 e în ACELAȘI discovery_range (spec §D); altfel EXCLUS.
Sesiuni = `code/mtf.py:37-38` (asia<8, london[8,13), ny[13,21), late>=21), după ora UTC a barei c.
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_HERE, os.path.join(_ROOT, "edge_research")):
    if p not in sys.path:
        sys.path.insert(0, p)

import split_manifest as SM  # noqa: E402
from market_structure import Block, StructureLabel, SwingKind, detect_swings, label_structure  # noqa: E402
from liquidity_mechanics import PoolSide, PoolTier, build_pools, detect_sweeps  # noqa: E402

TICK = 0.1  # code/mstrat.py:10 TICK=0.1 ; code/alpha_lab.py:11 tick=0.1
K = 2


def _session(epoch: int) -> str:
    h = pd.Timestamp(epoch, unit="s", tz="UTC").hour
    if h < 8:
        return "asia"
    if h < 13:
        return "london"
    if h < 21:
        return "ny"
    return "late"


def collect() -> tuple[list[dict], int]:
    manifest = SM.load_manifest()  # hash-verified, fail-closed
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]
    df = pd.read_csv(os.path.join(_ROOT, "data", "market", "OANDA_XAUUSD_M15.csv"))
    df = df.sort_values("time").reset_index(drop=True)
    t = df["time"].to_numpy()

    events: list[dict] = []
    excluded = 0
    for seg in segs:
        s, e = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        regime = seg["type"]
        mask = (t >= s) & (t < e)                      # semi-deschis [start, end)
        sub = df[mask].reset_index(drop=True)
        o = sub["open"].to_numpy(); hi = sub["high"].to_numpy()
        lo = sub["low"].to_numpy(); cl = sub["close"].to_numpy()
        tt = sub["time"].to_numpy()
        n = len(sub)
        blocks = [Block(0, n)]

        swings = label_structure(detect_swings(hi.tolist(), lo.tolist(), blocks, k=K))
        pools = build_pools(swings, PoolTier.EXTERNAL)  # ignoră UNCLASSIFIED (D)
        sweeps = detect_sweeps(hi.tolist(), lo.tolist(), cl.tolist(), pools, blocks,
                               require_close_back_inside=True)  # D6/D7, block-confined (D4)

        for sw in sweeps:
            c = sw.idx
            if c + 1 >= n:                              # spec §D: fără next-open în același range
                excluded += 1
                continue
            if sw.pool.side is PoolSide.BELOW:
                dist = float(o[c + 1] - lo[c])          # open[c+1] - low[c]
            else:
                dist = float(hi[c] - o[c + 1])          # high[c] - open[c+1]
            events.append({
                "pips": dist / TICK,                    # poate fi negativ (gap) — se raportează ca atare
                "regime": regime,
                "session": _session(int(tt[c])),
            })
    return events, excluded


def _stats(pips: list[float]) -> dict:
    n = len(pips)
    if n == 0:
        return {"n": 0}
    a = np.asarray(pips)
    q = np.percentile(a, [10, 25, 50, 75, 90])
    return {
        "n": n, "min": float(a.min()), "p10": float(q[0]), "p25": float(q[1]),
        "median": float(q[2]), "p75": float(q[3]), "p90": float(q[4]), "max": float(a.max()),
    }


def _fractions(pips: list[float]) -> dict:
    n = len(pips)
    if n == 0:
        return {"n": 0}
    a = np.asarray(pips)
    lo = int((a < 40).sum()); mid = int(((a >= 40) & (a < 65)).sum()); hi = int((a >= 65).sum())
    d = {"n": n, "<40": lo, "[40,65)": mid, ">=65": hi,
         "<40_pct": 100 * lo / n, "[40,65)_pct": 100 * mid / n, ">=65_pct": 100 * hi / n}
    if n < 25:
        d["flag"] = "SUB-PRAG (n<25), informativ"
    return d


def _line(name: str, s: dict) -> str:
    if s["n"] == 0:
        return f"  {name:12} n=0"
    return (f"  {name:12} n={s['n']:5} | min={s['min']:8.1f} p10={s['p10']:7.1f} p25={s['p25']:7.1f} "
            f"med={s['median']:7.1f} p75={s['p75']:7.1f} p90={s['p90']:7.1f} max={s['max']:8.1f}")


def _fline(name: str, f: dict) -> str:
    if f["n"] == 0:
        return f"  {name:12} n=0"
    flag = f"  [{f['flag']}]" if "flag" in f else ""
    return (f"  {name:12} n={f['n']:5} | <40: {f['<40']:5} ({f['<40_pct']:5.1f}%)  "
            f"[40,65): {f['[40,65)']:5} ({f['[40,65)_pct']:5.1f}%)  "
            f">=65: {f['>=65']:5} ({f['>=65_pct']:5.1f}%){flag}")


def main() -> int:
    events, excluded = collect()
    pips_all = [ev["pips"] for ev in events]
    regimes = ["bear", "bull", "correction"]
    sessions = ["asia", "london", "ny", "late"]

    print("=" * 96)
    print("LM-001 GEOMETRY AUDIT — displacement (entry next-open -> manipulation wick extremum), pips")
    print(f"TICK=0.10 | discovery bars=130,491 (M15_v2, half-open) | N valid={len(events)} | N excluded(no next-open)={excluded}")
    print("=" * 96)

    print("\n[PERCENTILE MATRIX — pips]")
    print(_line("AGGREGATE", _stats(pips_all)))
    print("  -- by regime --")
    for r in regimes:
        print(_line(r, _stats([e["pips"] for e in events if e["regime"] == r])))
    print("  -- by session --")
    for s in sessions:
        print(_line(s, _stats([e["pips"] for e in events if e["session"] == s])))

    print("\n[FRACTIONS — floor 40 / ceiling 65 pips (the audit's purpose; N explicit per cell)]")
    print(_fline("AGGREGATE", _fractions(pips_all)))
    print("  -- by regime --")
    for r in regimes:
        print(_fline(r, _fractions([e["pips"] for e in events if e["regime"] == r])))
    print("  -- by session --")
    for s in sessions:
        print(_fline(s, _fractions([e["pips"] for e in events if e["session"] == s])))

    rec = {
        "n_valid": len(events), "n_excluded": excluded,
        "aggregate_stats": _stats(pips_all), "aggregate_fractions": _fractions(pips_all),
        "by_regime": {r: {"stats": _stats([e["pips"] for e in events if e["regime"] == r]),
                          "fractions": _fractions([e["pips"] for e in events if e["regime"] == r])}
                      for r in regimes},
        "by_session": {s: {"stats": _stats([e["pips"] for e in events if e["session"] == s]),
                           "fractions": _fractions([e["pips"] for e in events if e["session"] == s])}
                       for s in sessions},
    }
    out = os.path.join(_ROOT, "edge_research", "lm001_geometry_audit_results.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2)
    print(f"\nrecord -> {os.path.relpath(out, _ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
