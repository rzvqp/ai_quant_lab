"""Flow B — SIGNAL BUILDERS + delegation to the CANONICAL EVALUATOR (Step 6, 2026-08 CEO mandate).

⚠ THE LOCAL GROSS EVALUATOR HAS BEEN ELIMINATED. Red Team confirmed the local `simulate` diverged
from the lab's evaluator on the FIRST trade (screen +1.00 gross vs mstrat +0.80 NET). There is now
ONE evaluator in the whole lab: **`mstrat.simulate`** (the shared production backtester — entry@next-open,
stop/target/timeout/trailing, floored executable stop, NET of CFG cost, no-overlap). This module NO
LONGER computes gross R. It provides:
  * SIGNAL BUILDERS (unchanged logic, NOT evaluation): derive_blocks, day_index_ny17,
    bars_to_period_end, breakout_trades, Trade
  * canonical_evaluate(d, trades) -- converts Trades -> mstrat setups and calls mstrat.simulate,
    returning the NET-of-cost ledger. THE ONLY evaluation path.
  * metrics / screen_verdict -- summary + fat-tail check, now computed on the CANONICAL NET R.
  * simulate(...) -- DEPRECATED: raises. Do not compute gross R locally.

Cost/convention are the canonical evaluator's (CFG: tick=0.01, spread_ticks=slip_ticks=1.0). Flow A does
NOT invent cost or choose its own convention — if the canonical spread assumption changes, that is VE's/
CEO's call, applied once at the source. Data is loaded ONLY via _common.load (holdout sealed). NO LOOKAHEAD.
"""
from __future__ import annotations
import sys, os, warnings
from dataclasses import dataclass

# ratified detector snapshot — imported, never reimplemented
_SNAP = os.environ.get("RATIFIED_CODE_DIR")
if _SNAP and _SNAP not in sys.path:
    sys.path.insert(0, _SNAP)
from market_structure import Block  # noqa: E402

# CANONICAL EVALUATOR snapshot (mstrat.simulate + alpha_lab.CFG) — the ONE lab evaluator
_CANON = os.environ.get("CANONICAL_CODE_DIR",
                        r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad\canonical_code\code")


def _canonical():
    """Import the canonical evaluator lazily (mstrat.simulate + CFG). Raises if unavailable — we do
    NOT silently fall back to a local gross computation."""
    if _CANON and _CANON not in sys.path:
        sys.path.insert(0, _CANON)
    from mstrat import simulate as _sim   # noqa: E402
    from alpha_lab import CFG              # noqa: E402
    return _sim, CFG


def derive_blocks(df, gap_hours: float = 72.0) -> list[Block]:
    """R9 CANONICAL POPULATION (measurement contract v1.0, edge_research/_contract.py). The ONLY
    legitimate population is the MANIFEST discovery segmentation. When `df` comes from
    `_common.load` it carries the official manifest blocks in `df.attrs['official_blocks']`; this
    function returns THOSE, exclusively — never a >72h gap-based reconstruction that differs
    (divergence M-4: the gap split fragments the population on ~3-day HOLIDAY closures
    (Christmas/New Year/Easter), producing e.g. 15 blocks where the manifest defines 3 discovery
    segments — different populations, incomparable numbers vs mstrat which uses the manifest).

    The legacy >72h gap split is retained ONLY as a fallback for a df that did NOT come from the
    manifest loader (an ad-hoc/synthetic frame), and it warns loudly that the result is NOT
    manifest-verified. Holiday gaps are treated like the ordinary weekend gaps already kept inside
    a block (bar-count windows tolerate them), so using the manifest blocks introduces no new
    window-across-gap behavior.
    """
    t = df["time"].to_numpy()
    bounds = [0]
    thr = gap_hours * 3600.0
    for i in range(1, len(t)):
        if (t[i] - t[i - 1]) > thr:
            bounds.append(i)
    bounds.append(len(t))
    gap_blocks = [(bounds[k], bounds[k + 1]) for k in range(len(bounds) - 1) if bounds[k + 1] > bounds[k]]

    attrs = getattr(df, "attrs", {}) or {}
    official = attrs.get("official_blocks")
    official_n = attrs.get("official_blocks_n")
    if official is not None and official_n == len(df):
        official = [(int(s), int(e)) for s, e in official]
        if gap_blocks != official:
            warnings.warn(
                f"derive_blocks: R9 contract override — manifest defines {len(official)} discovery "
                f"block(s); the legacy >72h gap split produced {len(gap_blocks)} (extra boundaries are "
                f"holiday closures, not data holes). Using the MANIFEST population EXCLUSIVELY "
                f"(divergence M-4 resolved).", RuntimeWarning, stacklevel=2)
        return [Block(s, e) for s, e in official]
    if official is not None:  # present but df length changed since load -> cannot safely map indices
        warnings.warn(
            "derive_blocks: df carries manifest official_blocks but its length changed since load; "
            "R9 cannot be enforced on a modified frame — falling back to gap blocks (quick-screen only).",
            RuntimeWarning, stacklevel=2)
    else:
        warnings.warn(
            "derive_blocks: df has no manifest official_blocks (not from _common.load) — using "
            "gap-derived blocks, quick-screen ONLY, NOT manifest-verified (R9).",
            RuntimeWarning, stacklevel=2)
    return [Block(s, e) for s, e in gap_blocks]


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
    exit_kind: str | None = None   # canonical menu: 'rr' | 'trailing' | 'time' | None (auto)
    exit_param: float | None = None  # rr multiple for 'rr'; bar count for 'time'


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


def simulate(*a, **k):
    """DEPRECATED (Step 6): the local GROSS evaluator is eliminated. Red Team found it diverged from
    the lab evaluator on the first trade. Use `canonical_evaluate(d, trades)` — the ONE lab evaluator."""
    raise RuntimeError(
        "_screen.simulate is ELIMINATED (Step 6). Local gross evaluation is forbidden — there is ONE "
        "evaluator in the lab: mstrat.simulate. Call canonical_evaluate(d, trades) instead.")


def trades_to_setups(trades):
    """Convert Flow-A Trade signals into canonical mstrat setups WITHOUT changing signal logic.
    mstrat entry = o[ei]; my entry = open[signal_idx+1] -> ei = signal_idx+1, si = signal_idx.
    Exit is expressed in the canonical menu: a price target -> ('opp_liq', price) (fixed-price exit,
    with mstrat's own 48-bar backstop); no target -> ('time', time_stop_bars). Stop is the price."""
    setups = []
    for t in trades:
        dirn = 1 if t.side == "long" else -1
        if t.exit_kind is not None:                      # explicit canonical exit (rr / trailing / time)
            ek, ep = t.exit_kind, t.exit_param
        elif t.target is not None:
            ek, ep = "opp_liq", float(t.target)
        else:
            ek, ep = "time", int(t.time_stop_bars)
        setups.append(dict(si=int(t.signal_idx), ei=int(t.signal_idx) + 1, dir=dirn,
                           stop=float(t.stop), exit_kind=ek, exit_param=ep))
    return setups


def canonical_evaluate(d, trades, gross=False):
    """Delegates to the canonical evaluator mstrat.simulate (floored stop, no-overlap, worst-case).
    NET of CFG cost by default. `gross=True` runs the SAME canonical engine at ZERO transaction cost
    (spread=slip=0) for GATE 1 GROSS ONLY — this is the explicit gross gate, NOT a net cost fallback and
    NOT an alternative calculator; the executable-stop floor still applies. The NET verdict (Phase B) uses
    the RATIFIED cost model (AI_TRADER_SHADOW_COST_MODEL_v1), never a local number."""
    sim, CFG = _canonical()
    cfg = dict(CFG)
    if gross:
        cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = 0.0   # GROSS = canonical mechanics, zero cost
    dd = d.copy()
    if "m_atr" not in dd.columns:
        dd["m_atr"] = dd["atr14"]
    setups = trades_to_setups(trades)
    led = sim(dd, setups, cfg)   # DataFrame: R, si, ei
    return [dict(r=float(r), signal_idx=int(si)) for r, si in zip(led["R"].to_numpy(), led["si"].to_numpy())]


def metrics(res) -> dict:
    n = len(res)
    if n == 0:
        return dict(n=0)
    rs = [x["r"] for x in res]
    wins = [x for x in rs if x > 0]
    losses = [x for x in rs if x <= 0]
    gross_win = sum(wins); gross_loss = -sum(losses)
    from collections import Counter
    reasons = Counter(x.get("reason", "canonical") for x in res)
    tot = sum(rs)
    srt = sorted(rs, reverse=True)
    risks = sorted(x.get("risk", float("nan")) for x in res if x.get("risk") is not None)
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
        median_stop=round(risks[len(risks) // 2], 2) if risks else None,
        stop_p25=round(risks[len(risks) // 4], 2) if risks else None,
        stop_p75=round(risks[3 * len(risks) // 4], 2) if risks else None,
        best_share_of_total=round(srt[0] / tot, 3) if tot > 0 else None,
        top5_share_of_total=round(sum(srt[:5]) / tot, 3) if tot > 0 else None,
        trimmed_top1pct=dict(removed=k, avg_R=round(t_avg, 4), profit_factor=round(t_pf, 3),
                             total_R=round(sum(trimmed), 2)),
        exit_mix={key: reasons[key] for key in reasons},
    )


def screen_verdict(m: dict, min_n: int = 30) -> str:
    """Screen on the CANONICAL NET R (from canonical_evaluate/mstrat.simulate). Conservative — KILL
    obvious losers, and NEVER call a fat-tail 'PROMISING'. A positive total built on a few tiny-stop
    outliers is not edge: downgrade if the single best trade is >30% of total R, or the top-1%-trimmed
    avg_R is non-positive."""
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
        return (f"PROMISING — positive NET edge ROBUST to top-1% trim (avg_R={exp}->trim {t_avg}, "
                f"PF={pf}->trim {t_pf}, best_share={bs}, total_R={tot}) → formal pipeline")
    return f"BORDERLINE — weak positive NET (avg_R={exp}, PF={pf}); marginal → hold/deprioritize"
