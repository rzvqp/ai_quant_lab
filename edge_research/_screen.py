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


def day_index_ny17(time) -> "list[int]":
    """17:00-NY anchored day ordinal — VERBATIM the ratified caller-side convention used across the
    obdz analyses (`obdz002_population._day_index` et al., identical everywhere): floor((NY-time − 17h)).
    The level modules take day_index/week_index as INPUT ('derivare CALLER-SIDE'); this supplies it —
    it is the required anchor, not a new one, and not a reimplemented detector."""
    import pandas as pd, numpy as np
    dt = pd.to_datetime(time, unit="s", utc=True)          # DatetimeIndex
    ny = dt.tz_convert("America/New_York").tz_localize(None)
    d = (ny - pd.Timedelta(hours=17)).floor("D").values.astype("datetime64[D]").astype("int64")
    return np.asarray(d, dtype=np.int64)


def bars_to_period_end(period_index, start_idx: int, block_end: int) -> int:
    """Live-valid horizon: number of bars from start_idx until the period_index changes (or block end).
    Used for day/week-boundary time-stops (the period clock is known at entry, no lookahead)."""
    pk = period_index[start_idx]
    j = start_idx + 1
    while j < block_end and period_index[j] == pk:
        j += 1
    return max(1, j - start_idx)


@dataclass
class Trade:
    signal_idx: int
    side: str          # 'long' | 'short'
    stop: float
    time_stop_bars: int
    target: float | None = None


def breakout_trades(levels_norm, high, low, close, period_index, blocks):
    """Route-2 BREAKOUT builder (structural stop). levels_norm = list of dicts with keys:
    price, is_high (bool), avail (first bar of the level's active period), opp (opposite-level price).
    Signal = FIRST bar in the level's active period whose CLOSE closes THROUGH the level in the break
    direction (is_high -> close>price -> LONG ; else close<price -> SHORT). Stop = the OPPOSITE level
    (structural, non-microscopic — the far side of the broken range). Exit = period-boundary time-stop.
    No fixed target. No lookahead (close-through and stop known at the signal bar)."""
    def _be(idx):
        for b in blocks:
            if b.start <= idx < b.end:
                return b.end
        return len(close)
    trades = []
    n_broken = 0
    for lv in levels_norm:
        avail = lv["avail"]; bend = _be(avail)
        wend = min(avail + bars_to_period_end(period_index, avail, bend), len(close))
        sig = None; side = None
        for j in range(avail, wend):
            if lv["is_high"] and close[j] > lv["price"]:
                sig, side = j, "long"; break
            if (not lv["is_high"]) and close[j] < lv["price"]:
                sig, side = j, "short"; break
        if sig is None or lv["opp"] is None:
            continue
        n_broken += 1
        tsb = bars_to_period_end(period_index, sig, _be(sig))
        trades.append(Trade(signal_idx=sig, side=side, stop=float(lv["opp"]),
                            time_stop_bars=tsb, target=None))
    return trades, dict(n_levels=len(levels_norm), n_broken=n_broken)


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
    tot = sum(rs)
    srt = sorted(rs, reverse=True)
    # FAT-TAIL robustness (parameter-free): single-best share + top-1%-trimmed re-computation.
    k = max(1, int(n * 0.01))
    trimmed = srt[k:]
    tw = [x for x in trimmed if x > 0]; tl = [-x for x in trimmed if x <= 0]
    t_avg = (sum(trimmed) / len(trimmed)) if trimmed else 0.0
    t_pf = (sum(tw) / sum(tl)) if sum(tl) > 0 else float("inf")
    return dict(
        n=n,
        win_rate=round(len(wins) / n, 4),
        total_R=round(tot, 2),
        avg_R=round(tot / n, 4),
        median_R=round(sorted(rs)[n // 2], 4),
        profit_factor=round(gross_win / gross_loss, 3) if gross_loss > 0 else float("inf"),
        best=round(max(rs), 2), worst=round(min(rs), 2),
        best_share_of_total=round(srt[0] / tot, 3) if tot > 0 else None,
        top5_share_of_total=round(sum(srt[:5]) / tot, 3) if tot > 0 else None,
        trimmed_top1pct=dict(removed=k, avg_R=round(t_avg, 4), profit_factor=round(t_pf, 3),
                             total_R=round(sum(trimmed), 2)),
        exit_mix={key: reasons[key] for key in reasons},
    )


def screen_verdict(m: dict, min_n: int = 30) -> str:
    """Quick economic screen. GROSS R (no costs). Conservative — KILL obvious losers, and NEVER call a
    fat-tail 'PROMISING'. A positive total built on a few tiny-stop outliers is not edge (CEO rule):
    downgrade if the single best trade is >30% of total R, or the top-1%-trimmed avg_R is non-positive."""
    if m.get("n", 0) < min_n:
        return f"INSUFFICIENT_N ({m.get('n',0)} < {min_n}) — cannot screen"
    exp = m["avg_R"]; pf = m["profit_factor"]; tot = m["total_R"]
    if exp <= 0 or tot <= 0:
        return f"ELIMINATE — non-positive expectancy (avg_R={exp}, total_R={tot}, PF={pf})"
    bs = m.get("best_share_of_total"); tr = m.get("trimmed_top1pct", {})
    t_avg = tr.get("avg_R", 0.0); t_pf = tr.get("profit_factor", 0.0)
    fat = (bs is not None and bs > 0.30) or (t_avg <= 0)
    if fat:
        return (f"BORDERLINE — FAT-TAIL (best trade = {bs} of total R; top-1%-trimmed avg_R={t_avg}, "
                f"PF={t_pf}). Positive total is a few tiny-stop outliers, NOT edge → deprioritize.")
    if exp > 0.05 and pf >= 1.20 and t_avg > 0 and t_pf >= 1.15:
        return (f"PROMISING — positive gross edge ROBUST to top-1% trim (avg_R={exp}->trim {t_avg}, "
                f"PF={pf}->trim {t_pf}, best_share={bs}, total_R={tot}) → formal pipeline")
    return f"BORDERLINE — weak positive gross (avg_R={exp}, PF={pf}); costs likely decisive → hold/deprioritize"
