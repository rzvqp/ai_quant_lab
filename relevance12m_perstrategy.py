"""Current XAUUSD 12-Month Relevance Audit -- per-strategy analysis (SCRATCH, preserved artifact).

Reuses the EXISTING, frozen `ai_trader.strategy_health.metrics.compute_window_metrics` and
`ai_trader.strategy_health.scoring.score_window` -- read-only reuse of already-tested library code,
NOT a redesign of the Health System (nothing in `ai_trader/strategy_health/` is imported for its
side effects or modified). Unlike Phase 6.9, this does NOT call `evaluate_strategy_health()` /
`combine_windows()` / `classify()` -- those blend 3m/6m/12m windows and apply the trend-bump rule,
which is the wrong tool here: the CEO's own instruction is "classification must be based ONLY on the
latest 12-month evidence... do not use older performance to promote a strategy." So this script scores
the 12-month window ALONE, against the cross-section of all 43 strategies' own 12-month evidence, with
no blending and no trend adjustment.

Classification bands (65 / 45) are the SAME frozen numbers `ai_trader/strategy_health/classifier.py`
already uses for ACTIVE/WATCHLIST/PROBATION -- reused, not reinvented, renamed for this report's own
CURRENTLY_STRONG/CURRENTLY_USABLE/CURRENTLY_WEAK vocabulary. Sample-sufficiency thresholds reuse the
Health System's own `CREDIBILITY_K=10` reference sample size (SUFFICIENT >= 10, matching the point
where a strategy's own evidence and the neutral prior are weighted equally; LIMITED 5-9; INSUFFICIENT
< 5) -- again reused, not a new number invented to fit this dataset.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from ai_trader.strategy_health.metrics import compute_window_metrics, trades_in_window
from ai_trader.strategy_health.scoring import score_window
from ai_trader.strategy_health.types import ClosedTrade

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data" / "market"

WINDOW_START = 1_729_674_000
WINDOW_END = 1_761_210_000

ACTIVE_BAND = 65.0
USABLE_BAND = 45.0
SUFFICIENT_N = 10
LIMITED_N = 5


def _session_of(as_of: int) -> str:
    """Mirrors `ai_trader.simulation.performance_analyzer._session_of` exactly (a private function
    reused here read-only, for reporting attribution only -- not imported directly since it is
    module-private; the classification logic is copied verbatim, not altered)."""
    hour = datetime.fromtimestamp(as_of, tz=UTC).hour
    if hour < 7:
        return "asia"
    if hour < 12:
        return "london"
    if hour < 20:
        return "ny"
    return "late"


def _month_key(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m")


def _build_atr_regime_lookup() -> pd.DataFrame:
    """A simple, disclosed, REPORTING-ONLY volatility-regime proxy (NOT part of any frozen module,
    NOT used for any trading decision): 14-bar True Range average over the analysis window's own
    bars, bucketed into low/medium/high TERTILES of that window's own distribution. Computed directly
    from the raw OHLC CSV, independent of the Market Scanner's own internal ATR feature."""
    df = pd.read_csv(DATA_DIR / "OANDA_XAUUSD_M15.csv")
    df = df[(df["time"] >= WINDOW_START - 200 * 900) & (df["time"] <= WINDOW_END)].reset_index(drop=True)
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    df["atr14"] = tr.rolling(14, min_periods=14).mean()
    window_df = df[(df["time"] >= WINDOW_START) & (df["time"] <= WINDOW_END)].dropna(subset=["atr14"])
    q1, q2 = window_df["atr14"].quantile([1 / 3, 2 / 3])
    df["regime"] = pd.cut(df["atr14"], bins=[-1, q1, q2, float("inf")], labels=["low_vol", "mid_vol", "high_vol"])
    return df[["time", "regime"]].set_index("time")


def _regime_at(lookup: pd.DataFrame, as_of: int) -> str:
    eligible = lookup[lookup.index <= as_of]
    if eligible.empty:
        return "unknown"
    val = eligible.iloc[-1]["regime"]
    return str(val) if pd.notna(val) else "unknown"


def sufficiency(n: int) -> str:
    if n >= SUFFICIENT_N:
        return "SUFFICIENT"
    if n >= LIMITED_N:
        return "LIMITED"
    return "INSUFFICIENT"


def classify(score: float | None, suff: str) -> str:
    if suff == "INSUFFICIENT" or score is None:
        return "INSUFFICIENT_EVIDENCE"
    if score >= ACTIVE_BAND:
        return "CURRENTLY_STRONG"
    if score >= USABLE_BAND:
        return "CURRENTLY_USABLE"
    return "CURRENTLY_WEAK"


def main() -> None:
    data = json.loads((REPO_ROOT / "relevance12m_portfolioA.json").read_text(encoding="utf-8"))
    all_ids = data["all_strategy_ids"]
    raw_trades = data["variant_A_all43"]["trades"]
    net_profit_a = data["variant_A_all43"]["performance"]["portfolio_summary"]["net_profit"]

    by_strategy_raw: dict[str, list[dict]] = defaultdict(list)
    for t in raw_trades:
        by_strategy_raw[t["strategy_id"]].append(t)

    by_strategy_closed: dict[str, list[ClosedTrade]] = {
        sid: [
            ClosedTrade(
                strategy_id=t["strategy_id"], exit_as_of=t["exit_as_of"], net_pnl=t["net_pnl"],
                pnl_r=t["pnl_r"], holding_bars=t["holding_bars"],
            )
            for t in by_strategy_raw.get(sid, [])
        ]
        for sid in all_ids
    }

    window_metrics = {
        sid: compute_window_metrics(by_strategy_closed[sid], "12m", WINDOW_END) for sid in all_ids
    }
    population = [m for m in window_metrics.values() if m.n_trades > 0]

    atr_lookup = _build_atr_regime_lookup()

    rows = []
    for sid in all_ids:
        wm = window_metrics[sid]
        own_score = score_window(wm, population)
        suff = sufficiency(wm.n_trades)
        cls = classify(own_score.score, suff)

        raw = by_strategy_raw.get(sid, [])
        buys = sum(1 for t in raw if t["direction"] == "LONG")
        sells = sum(1 for t in raw if t["direction"] == "SHORT")
        wins = sum(1 for t in raw if t["net_pnl"] > 0)
        losses = sum(1 for t in raw if t["net_pnl"] <= 0)
        active_months = sorted({_month_key(t["exit_as_of"]) for t in raw})
        sessions = defaultdict(int)
        for t in raw:
            sessions[_session_of(t["exit_as_of"])] += 1
        regimes = defaultdict(int)
        for t in raw:
            regimes[_regime_at(atr_lookup, t["entry_as_of"])] += 1
        total_fees = sum(t["fees"] for t in raw)

        rows.append({
            "strategy_id": sid,
            "n_trades": wm.n_trades,
            "buy_trades": buys,
            "sell_trades": sells,
            "winning_trades": wins,
            "losing_trades": losses,
            "win_rate": wm.win_rate,
            "expectancy_r": wm.expectancy_r,
            "net_r": wm.net_r,
            "profit_factor": wm.profit_factor,
            "net_pnl": wm.net_pnl,
            "return_contribution_pct": (wm.net_pnl / net_profit_a * 100.0) if net_profit_a else None,
            "max_drawdown_isolated": wm.max_drawdown,
            "max_losing_streak": wm.max_losing_streak,
            "monthly_consistency": wm.monthly_consistency,
            "equity_stability": wm.equity_stability,
            "active_months": active_months,
            "n_active_months": len(active_months),
            "avg_holding_bars": wm.avg_holding_bars,
            "session_attribution": dict(sessions),
            "regime_attribution": dict(regimes),
            "total_execution_cost_usd": total_fees,
            "sample_sufficiency": suff,
            "score_12m": own_score.score,
            "score_confidence": own_score.confidence,
            "classification": cls,
        })

    rows.sort(key=lambda r: (-(r["score_12m"] if r["score_12m"] is not None else -1)))

    counts = defaultdict(int)
    for r in rows:
        counts[r["classification"]] += 1

    out = {
        "window": {"start": WINDOW_START, "end": WINDOW_END},
        "n_strategies": len(all_ids),
        "classification_counts": dict(counts),
        "strategies": rows,
    }
    out_path = REPO_ROOT / "relevance12m_perstrategy.json"
    out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"classification_counts": dict(counts)}, indent=2))
    for r in rows:
        print(f"{r['strategy_id']:5s} n={r['n_trades']:3d} suff={r['sample_sufficiency']:12s} "
              f"score={r['score_12m']} cls={r['classification']}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
