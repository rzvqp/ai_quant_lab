"""Flow B — QUICK ECONOMIC SCREENER (reusable).

CEO progress criterion (2026): ECONOMIC OUTPUT, not infrastructure. Flow per candidate is
IDEA -> POLICY -> QUICK BACKTEST -> ECONOMIC SCREENING; obviously-unprofitable candidates are
eliminated immediately, only promising ones consume the expensive formal pipeline.

This module is the shared measurement apparatus (NOT a representation of any phenomenon — the
phenomena come from the RATIFIED detectors, imported, never reimplemented). It provides:
  * derive_blocks(df)  -- the contiguity segments the ratified detectors require, from time-gaps
  * simulate(...)      -- forward trade simulation with WORST-CASE intrabar resolution
                          (stop-before-target when a bar spans both — the ratified DEMO convention)
  * metrics(...)       -- economic summary (n, win%, total R, expectancy, profit factor)
  * screen_verdict(...)-- ELIMINATE / PROMISING / BORDERLINE

Data is loaded ONLY via edge_research._common.load (holdout sealed). Blocks are derived from the
delivered df's own time-contiguity (a gap > gap_hours between consecutive bars = a segment
boundary), which keeps weekends inside a block (like the manifest discovery segments) but never
lets a detector window cross a real data gap. This is the QUICK-screen block model; a promoted
candidate's FORMAL run uses the manifest's exact discovery segments.

NO LOOKAHEAD: entry is next-open after the signal bar; every stop/target is known at entry.
Costs are NOT modeled here (quick screen reads GROSS R) — an obviously-unprofitable gross result
needs no cost model; a promising gross result is where costs get measured, downstream.
"""
from __future__ import annotations
import sys, os
from dataclasses import dataclass

# ratified code snapshot (commit 5443077) — imported, never reimplemented
_SNAP = os.environ.get("RATIFIED_CODE_DIR")
if _SNAP and _SNAP not in sys.path:
    sys.path.insert(0, _SNAP)
from market_structure import Block  # noqa: E402


def derive_blocks(df, gap_hours: float = 72.0) -> list[Block]:
    """Contiguity segments from the delivered df's time column. A gap > gap_hours (default 3 days)
    between consecutive bars starts a new block — separates the manifest discovery segments (weeks
    of quarantine) while keeping ordinary weekend gaps (~2 days) inside a block."""
    t = df["time"].to_numpy()
    bounds = [0]
    thr = gap_hours * 3600.0
    for i in range(1, len(t)):
        if (t[i] - t[i - 1]) > thr:
            bounds.append(i)
    bounds.append(len(t))
    return [Block(bounds[k], bounds[k + 1]) for k in range(len(bounds) - 1) if bounds[k + 1] > bounds[k]]


@dataclass
class Trade:
    signal_idx: int
    side: str          # 'long' | 'short'
    stop: float
    time_stop_bars: int
    target: float | None = None


def simulate(o, h, l, c, trades, worst_case: bool = True):
    """Forward-simulate. Entry = open[signal_idx+1] (next-open, no lookahead). Scan to the time-stop:
    if a bar spans BOTH stop and target, WORST-CASE assigns the stop (fail-closed). R = signed
    (exit-entry)/|entry-stop|. Returns per-trade dicts."""
    n = len(c)
    res = []
    for t in trades:
        si = t.signal_idx
        ei = si + 1
        if ei >= n:
            continue
        entry = float(o[ei]); stop = float(t.stop); side = t.side; tgt = t.target
        risk = abs(entry - stop)
        if risk <= 0:
            continue
        # validity guard: refuse if entry already beyond stop or already beyond target
        if side == "long" and entry <= stop:
            continue
        if side == "short" and entry >= stop:
            continue
        if tgt is not None and ((side == "long" and entry >= tgt) or (side == "short" and entry <= tgt)):
            continue
        end = min(ei + t.time_stop_bars, n - 1)
        exit_price = None; reason = None
        for j in range(ei, end + 1):
            hi = float(h[j]); lo = float(l[j])
            hit_stop = (lo <= stop) if side == "long" else (hi >= stop)
            hit_tgt = tgt is not None and ((hi >= tgt) if side == "long" else (lo <= tgt))
            if hit_stop and hit_tgt:
                exit_price, reason = stop, "stop_wc"  # worst-case: stop first
                break
            if hit_stop:
                exit_price, reason = stop, "stop"; break
            if hit_tgt:
                exit_price, reason = tgt, "target"; break
        if exit_price is None:
            exit_price, reason = float(c[end]), "time"
        r = (exit_price - entry) / risk if side == "long" else (entry - exit_price) / risk
        res.append(dict(r=r, reason=reason, entry=entry, exit=exit_price, side=side, signal_idx=si))
    return res


def metrics(res) -> dict:
    n = len(res)
    if n == 0:
        return dict(n=0)
    rs = [x["r"] for x in res]
    wins = [x for x in rs if x > 0]
    losses = [x for x in rs if x <= 0]
    gross_win = sum(wins); gross_loss = -sum(losses)
    from collections import Counter
    reasons = Counter(x["reason"] for x in res)
    return dict(
        n=n,
        win_rate=round(len(wins) / n, 4),
        total_R=round(sum(rs), 2),
        avg_R=round(sum(rs) / n, 4),
        median_R=round(sorted(rs)[n // 2], 4),
        profit_factor=round(gross_win / gross_loss, 3) if gross_loss > 0 else float("inf"),
        best=round(max(rs), 2), worst=round(min(rs), 2),
        exit_mix={k: reasons[k] for k in reasons},
    )


def screen_verdict(m: dict, min_n: int = 30) -> str:
    """Quick economic screen. GROSS R (no costs). Conservative thresholds — the point is to KILL
    obvious losers fast, not to declare winners (that is the formal pipeline's job)."""
    if m.get("n", 0) < min_n:
        return f"INSUFFICIENT_N ({m.get('n',0)} < {min_n}) — cannot screen"
    exp = m["avg_R"]; pf = m["profit_factor"]; tot = m["total_R"]
    if exp <= 0 or tot <= 0:
        return f"ELIMINATE — non-positive expectancy (avg_R={exp}, total_R={tot}, PF={pf})"
    if exp > 0.05 and pf >= 1.20:
        return f"PROMISING — positive gross edge (avg_R={exp}, PF={pf}, total_R={tot}) → formal pipeline"
    return f"BORDERLINE — weak positive gross (avg_R={exp}, PF={pf}); costs likely decisive → hold/deprioritize"
