"""CEO-directed research study (2026-07-20, audited/finalized 2026-07-20): full historical performance
analysis of every executable strategy, Scenario A (fully isolated) vs Scenario B (current competitive
portfolio configuration). This is the SINGLE, FINAL, canonical analysis+report-generation script for
this study -- it both computes every metric AND emits the markdown tables (superseding the earlier
two-script split; the intermediate `ceo_strategy_performance_report_gen.py` has been folded in here and
removed).

**Methodological verification (2026-07-20 audit, see CEO_STRATEGY_PERFORMANCE_STUDY_REPORT.md §1 for the
full write-up)**: `phase69a_isolated_run.py` imports and calls the EXACT SAME `new_harness()` factory
function `phase69a_funnel_run.py` (the competitive run) defines -- confirmed by direct source read, not
assumed -- so both scenarios share byte-identical `SimulationContext` (window, symbols, timeframes,
starting balance, run_seed, warmup_bars), `RiskConfig` (spread/liquidity floor/sizing), `ManagerConfig`,
and harness construction flags; the ONLY difference is `strategy_id_filter`. `TradeRecord.exit_price`/
`exit_as_of` are non-optional fields (`ai_trader/simulation/portfolio_simulator.py`), so every saved
trade is structurally a genuinely closed position in both files. `compute_window_metrics`'s own
profit_factor formula (`ai_trader/strategy_health/metrics.py` line 78: `(gross_win/gross_loss) if
gross_loss > 0 else None`) and `performance_analyzer.py`'s own (line 313, same pattern) both return
`None`, never an infinite value, on zero losing trades -- verified by direct source read, not by
observing the data. Both saved JSON files were scanned for every error/bug-indicating deny-reason code
(`INTERNAL_ERROR`/`SCHEMA_MISMATCH`/`PORTFOLIO_UNAVAILABLE`/`DATA_DEGRADED`) across all 43 strategies in
both scenarios: zero found. Look-ahead safety is inherited, not re-derived: both scenarios use the
standard, unmodified `SimulationHarness`/`MarketScanner`/`ReplayDataSource` pipeline that governs every
other backtest in this project, with `ai_trader.strategy_runtime.context_access`'s own documented
"every value comes from `select_lookahead_safe_bars`-produced data" guarantee applying identically to
both runs -- no custom or future-peeking construction exists in either driver script.

READ-ONLY. Does not modify, import for mutation, or call any write path of any ai_trader/ production
module. No algorithm is changed, no parameter is tuned, no new strategy is introduced, no statistical
formula is invented -- every number below is produced by an EXISTING, already-shipped function:

- `ai_trader.strategy_health.types.from_trade_record` / `ClosedTrade`
- `ai_trader.strategy_health.metrics.compute_window_metrics` (win_rate/profit_factor/expectancy_r/
  expectancy_currency/net_r/net_pnl/max_drawdown/monthly_consistency/equity_stability/
  max_losing_streak/avg_holding_bars/n_trades)
- `ai_trader.strategy_health.evaluator.evaluate_strategy_health` (the project's own established
  robustness classification: percentile-rank + Bühlmann-credibility-shrinkage + PCA-derived weights)
- `ai_trader.shadow_evidence.research._sharpe_ratio` / `_best_worst_month` / `_direction_stats` /
  `_max_consecutive_wins` (private but plain, importable pure functions)
- `ai_trader.shadow_evidence.comparison.rank_by` / `leaderboard`
- `ai_trader.shadow_evidence.portfolio_research.correlation_matrix` / `diversification_metrics`
- `ai_trader.simulation.performance_analyzer._attribution` / `_max_losing_streak` (the same per-strategy
  attribution logic already used to build the real `SimulationReportData`)

Two formulas (payoff ratio = avg_win / avg_loss; recovery factor = net_pnl / max_drawdown) are applied
using the EXACT SAME definitions `ai_trader/simulation/performance_analyzer.py` already uses internally
(lines 313 and 317-320 of that file) -- reused verbatim here as plain arithmetic on already-computed
values, not a new statistical method.

**Data source**: `phase69a_isolated_funnel.json` (43 single-strategy-only harness runs, one dedicated
portfolio slot each -- Scenario A) and `phase69a_competitive_funnel.json` (one all-43-strategies-
competing run, real shared-slot portfolio rules -- Scenario B). Both already exist on disk from Phase
6.9A's own CEO-authorized funnel measurement, over the IDENTICAL window and config
(2024-10-23 09:00 UTC -> 2025-10-23 09:00 UTC, $2,000 capital, 5% risk/trade, run_seed=1) -- the only
paired isolated/competitive dataset that exists anywhere in this project. Re-using it (rather than
running a fresh backtest) is itself in the spirit of "foloseste exclusiv codul existent": no new
simulation is executed, only already-produced trade ledgers are re-analyzed.

**Disclosed scope limitation**: a full per-trade join against Market Intelligence's own regime
classification (would require a ~23,600-bar sequential MarketScanner replay purely for labeling) was
NOT performed -- the cost is large relative to the value for a reporting-only study, and BEST/WORST
MONTH (via the existing `_best_worst_month`) already gives a genuine, non-fabricated temporal
performance signal reused as the practical proxy for "period it performs best/worst in."
"""

from __future__ import annotations

import dataclasses
import enum
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from ai_trader.shadow_evidence.comparison import leaderboard, rank_by
from ai_trader.shadow_evidence.research import (
    DirectionStats,
    StrategyResearchSummary,
    _best_worst_month,
    _direction_stats,
    _max_consecutive_wins,
    _sharpe_ratio,
)
from ai_trader.shadow_evidence.portfolio_research import correlation_matrix, diversification_metrics
from ai_trader.shadow_evidence.types import ShadowTradeLegRecord
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.performance_analyzer import _attribution, _max_losing_streak
from ai_trader.simulation.portfolio_simulator import TradeRecord
from ai_trader.strategy_health.evaluator import evaluate_strategy_health
from ai_trader.strategy_health.metrics import compute_window_metrics
from ai_trader.strategy_health.types import from_trade_record

REPO_ROOT = Path(__file__).resolve().parent
WINDOW_START = 1_729_674_000
WINDOW_END = 1_761_210_000  # exactly 365 days after WINDOW_START
MIN_TRADES_RELIABLE = 25  # reused from code/alpha_lab.py's own MINTR convention (Checkpoint 13's own precedent)


def _load(name: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / name).read_text(encoding="utf-8"))


def _to_trade_record(d: dict[str, Any]) -> TradeRecord:
    return TradeRecord(
        client_order_id=d["client_order_id"], strategy_id=d["strategy_id"], symbol=d["symbol"],
        direction=Direction(d["direction"]), entry_price=d["entry_price"], exit_price=d["exit_price"],
        entry_as_of=d["entry_as_of"], exit_as_of=d["exit_as_of"], qty=d["qty"], gross_pnl=d["gross_pnl"],
        fees=d["fees"], net_pnl=d["net_pnl"], pnl_r=d["pnl_r"], holding_bars=d["holding_bars"],
        mfe=d["mfe"], mae=d["mae"],
    )


def _payoff_ratio(trades: list[TradeRecord]) -> float | None:
    # Verbatim reuse of performance_analyzer.py's own formula (avg_win / avg_loss), lines 311-313.
    wins = [t.net_pnl for t in trades if t.net_pnl > 0]
    losses = [abs(t.net_pnl) for t in trades if t.net_pnl <= 0]
    avg_win = statistics.fmean(wins) if wins else None
    avg_loss = statistics.fmean(losses) if losses else None
    return (avg_win / avg_loss) if (avg_win is not None and avg_loss) else None


def _recovery_factor(net_pnl: float, max_drawdown: float) -> float | None:
    # Verbatim reuse of performance_analyzer.py's own formula (net_profit / max_drawdown), lines 317-320
    # -- applied here to the trade-sequence-based max_drawdown (strategy_health.metrics's own
    # definition) rather than an equity-curve-based one, since no per-strategy equity curve exists for
    # the competitive scenario -- the SAME drawdown definition is used for BOTH scenarios for a fair,
    # apples-to-apples comparison.
    return (net_pnl / max_drawdown) if max_drawdown > 0 else None


def _blocking_breakdown(funnel: dict[str, Any]) -> dict[str, Any]:
    """The CEO's own 5-category funnel split, mapped directly onto already-recorded fields -- no new
    counting logic, only re-grouping existing per-reason counts:

    1. nonexistent_signals    = risk_deny_reasons['NOT_ACTIONABLE'] (the strategy's own setup never
                                 fired this bar -- the dominant, already-computed count).
    2. generated_ineligible   = every OTHER risk_deny_reason except NOT_ACTIONABLE and
                                 LIMIT_MAX_PER_SYMBOL (SIZE_BELOW_MIN/BELOW_FLOOR/COOLDOWN_*/etc. -- a
                                 real setup was scored but failed a sizing/eligibility/quality gate).
    3. eligible_blocked_by_position = risk_deny_reasons['LIMIT_MAX_PER_SYMBOL'] specifically -- the
                                 shared-slot constraint, and ONLY that constraint.
    4. executed               = order_counts['filled'] (== n_trades).
    5. nonfinalized_excluded  = order_counts['cancelled'] + order_counts['expired'] (submitted but
                                 never became a closed TradeRecord -- excluded from every performance
                                 metric in this study, exactly as it is excluded from the saved
                                 `trades` list itself).
    """
    reasons = funnel["risk_deny_reasons"]
    orders = funnel["order_counts"]
    nonexistent = reasons.get("NOT_ACTIONABLE", 0)
    shared_slot = reasons.get("LIMIT_MAX_PER_SYMBOL", 0)
    generated_ineligible = sum(v for k, v in reasons.items() if k not in ("NOT_ACTIONABLE", "LIMIT_MAX_PER_SYMBOL"))
    executed = orders.get("filled", 0)
    nonfinalized = orders.get("cancelled", 0) + orders.get("expired", 0)
    return {
        "nonexistent_signals": nonexistent,
        "generated_ineligible": generated_ineligible,
        "eligible_blocked_by_position": shared_slot,
        "executed": executed,
        "nonfinalized_excluded": nonfinalized,
    }


def _principal_loss_reason(iso_funnel: dict[str, Any], comp_funnel: dict[str, Any]) -> str:
    """Which denial category shows the LARGEST increase from isolated to competitive -- computed per
    strategy, never assumed to be the shared-slot rule (CEO's own explicit instruction). Ties broken by
    a fixed, disclosed category order."""
    iso_reasons = iso_funnel["risk_deny_reasons"]
    comp_reasons = comp_funnel["risk_deny_reasons"]
    all_codes = sorted(set(iso_reasons) | set(comp_reasons))
    deltas = {code: comp_reasons.get(code, 0) - iso_reasons.get(code, 0) for code in all_codes}
    positive = {code: d for code, d in deltas.items() if d > 0}
    if not positive:
        return "none (no denial category increased under competition)"
    best_code = max(sorted(positive), key=lambda c: positive[c])
    return f"{best_code} (+{positive[best_code]})"


def _classify(
    n_trades: int, profit_factor: float | None, expectancy_r: float | None, health_state: str,
) -> tuple[str, str]:
    """The CEO's own five-category final classification (A-E), applied via already-established
    thresholds only -- MIN_TRADES_RELIABLE reused from code/alpha_lab.py's own MINTR, profitability
    defined as PF>1 AND Exp_R>0 (the same pairing this whole study already used). No strategy is
    eliminated; every strategy receives exactly one category plus an exact, numeric justification."""
    if n_trades == 0:
        return "D", "Inactive -- zero isolated trades; the strategy's own setup never fires in this window (see §1 verification: no error/bug-indicating deny reason found)."
    reliable = n_trades >= MIN_TRADES_RELIABLE
    profitable = (profit_factor is not None and profit_factor > 1.0) and (expectancy_r is not None and expectancy_r > 0.0)
    pf_str = f"{profit_factor:.2f}" if profit_factor is not None else "n/a"
    er_str = f"{expectancy_r:.3f}" if expectancy_r is not None else "n/a"
    if reliable and profitable:
        return "A", f"Candidate -- reliable and profitable: n={n_trades} (>= {MIN_TRADES_RELIABLE}), PF={pf_str} (>1), Exp_R={er_str} (>0), health={health_state}."
    if not reliable and profitable:
        return "B", f"Promising -- profitable but under-sampled: n={n_trades} (< {MIN_TRADES_RELIABLE}), PF={pf_str}, Exp_R={er_str}."
    if reliable and not profitable:
        return "C", f"Reliable but unprofitable: n={n_trades} (>= {MIN_TRADES_RELIABLE}), PF={pf_str}, Exp_R={er_str} -- not recommended for removal (standing project rule), flagged as weakest reliable-sample performer."
    return "E", f"Inconclusive -- insufficient or conflicting evidence: n={n_trades} (< {MIN_TRADES_RELIABLE}), PF={pf_str}, Exp_R={er_str}."


def _strategy_metrics(strategy_id: str, trades: list[TradeRecord]) -> dict[str, Any]:
    closed = [from_trade_record(t) for t in trades]
    wm = compute_window_metrics(closed, window="12m", as_of=WINDOW_END)
    sorted_trades = sorted(trades, key=lambda t: t.exit_as_of)
    r_values = [t.pnl_r for t in trades if t.pnl_r is not None]
    sharpe = _sharpe_ratio(r_values)
    best_month, best_month_pnl, worst_month, worst_month_pnl = _best_worst_month(trades)
    long_stats = _direction_stats(trades, Direction.LONG)
    short_stats = _direction_stats(trades, Direction.SHORT)
    max_consec_wins = _max_consecutive_wins(sorted_trades)
    max_losing_streak = _max_losing_streak(trades)
    payoff = _payoff_ratio(trades)
    recovery = _recovery_factor(wm.net_pnl, wm.max_drawdown)

    summary = StrategyResearchSummary(
        strategy_id=strategy_id, source="shadow", window_metrics=wm, average_r=wm.expectancy_r,
        sharpe_ratio=sharpe, best_month=best_month, best_month_pnl=best_month_pnl,
        worst_month=worst_month, worst_month_pnl=worst_month_pnl, long=long_stats, short=short_stats,
        max_consecutive_wins=max_consec_wins,
    )

    return {
        "strategy_id": strategy_id,
        "window_metrics": wm,
        "sharpe_ratio": sharpe,
        "payoff_ratio": payoff,
        "recovery_factor": recovery,
        "best_month": best_month, "best_month_pnl": best_month_pnl,
        "worst_month": worst_month, "worst_month_pnl": worst_month_pnl,
        "long": long_stats, "short": short_stats,
        "max_consecutive_wins": max_consec_wins, "max_losing_streak": max_losing_streak,
        "research_summary": summary,
    }


def main() -> dict[str, Any]:
    isolated_raw = _load("phase69a_isolated_funnel.json")
    competitive_raw = _load("phase69a_competitive_funnel.json")

    all_strategy_ids = sorted(isolated_raw.keys())

    # ------------------------------------------------------------------ Scenario A: isolated
    isolated_trades_by_strategy: dict[str, list[TradeRecord]] = {}
    isolated_funnel_by_strategy: dict[str, dict[str, Any]] = {}
    for sid in all_strategy_ids:
        entry = isolated_raw[sid]
        isolated_trades_by_strategy[sid] = [_to_trade_record(t) for t in entry["trades"]]
        isolated_funnel_by_strategy[sid] = {
            "signal_counts": entry["signal_counts"], "scoring_counts": entry["scoring_counts"],
            "risk_counts": entry["risk_counts"], "risk_deny_reasons": entry["risk_deny_reasons"],
            "order_counts": entry["order_counts"], "saved_performance": entry.get("performance"),
        }

    # ------------------------------------------------------------------ Scenario B: competitive
    competitive_trades_by_strategy: dict[str, list[TradeRecord]] = defaultdict(list)
    for t in competitive_raw["trades"]:
        tr = _to_trade_record(t)
        competitive_trades_by_strategy[tr.strategy_id].append(tr)
    competitive_funnel_by_strategy: dict[str, dict[str, Any]] = {}
    for sid in all_strategy_ids:
        competitive_funnel_by_strategy[sid] = {
            "signal_counts": competitive_raw["signal_counts"].get(sid, {}),
            "scoring_counts": competitive_raw["scoring_counts"].get(sid, {}),
            "risk_counts": competitive_raw["risk_counts"].get(sid, {}),
            "risk_deny_reasons": competitive_raw["risk_deny_reasons"].get(sid, {}),
            "order_counts": competitive_raw["order_counts"].get(sid, {}),
        }

    # ------------------------------------------------------------------ per-strategy metrics, both scenarios
    isolated_metrics = {
        sid: _strategy_metrics(sid, isolated_trades_by_strategy[sid]) for sid in all_strategy_ids
    }
    competitive_metrics = {
        sid: _strategy_metrics(sid, competitive_trades_by_strategy.get(sid, [])) for sid in all_strategy_ids
    }

    # ------------------------------------------------------------------ portfolio-wide attribution (existing fn)
    all_competitive_trades = [_to_trade_record(t) for t in competitive_raw["trades"]]
    attribution = _attribution(all_competitive_trades)
    attribution_by_sid = {a.strategy_id: a for a in attribution}

    # ------------------------------------------------------------------ robustness (strategy_health, existing)
    isolated_closed = {sid: [from_trade_record(t) for t in isolated_trades_by_strategy[sid]] for sid in all_strategy_ids}
    competitive_closed = {sid: [from_trade_record(t) for t in competitive_trades_by_strategy.get(sid, [])] for sid in all_strategy_ids}
    isolated_health = evaluate_strategy_health(isolated_closed, WINDOW_END)
    competitive_health = evaluate_strategy_health(competitive_closed, WINDOW_END)

    # ------------------------------------------------------------------ diversification (existing fn)
    trade_legs = [
        ShadowTradeLegRecord(leg=t, position_id=t.client_order_id, exit_reason="CLOSED")
        for t in all_competitive_trades
    ]
    corr = correlation_matrix(trade_legs)
    diversification = diversification_metrics(corr)

    # ------------------------------------------------------------------ rankings (existing fn),
    # segmented by reliability tier (n>=MIN_TRADES_RELIABLE) so a small-sample strategy (e.g. 2-4
    # trades) can never appear ranked above a reliable-sample strategy without that being visible --
    # 2026-07-20 audit finding: the original single mixed-reliability ranking let tiny-n strategies
    # dominate the top of Profit-Factor/Expectancy tables with no sample-size signal attached.
    isolated_summaries = {sid: isolated_metrics[sid]["research_summary"] for sid in all_strategy_ids}
    competitive_summaries = {sid: competitive_metrics[sid]["research_summary"] for sid in all_strategy_ids}

    def _reliable_subset(summaries: dict[str, StrategyResearchSummary]) -> dict[str, StrategyResearchSummary]:
        return {sid: s for sid, s in summaries.items() if s.window_metrics.n_trades >= MIN_TRADES_RELIABLE}

    def _small_sample_subset(summaries: dict[str, StrategyResearchSummary]) -> dict[str, StrategyResearchSummary]:
        return {sid: s for sid, s in summaries.items() if 0 < s.window_metrics.n_trades < MIN_TRADES_RELIABLE}

    iso_reliable = _reliable_subset(isolated_summaries)
    iso_small = _small_sample_subset(isolated_summaries)
    comp_reliable = _reliable_subset(competitive_summaries)
    comp_small = _small_sample_subset(competitive_summaries)

    def _rank_tiered(reliable: dict, small: dict, metric: str, descending: bool = True) -> dict[str, list]:
        return {
            "reliable_n_ge_25": rank_by(reliable, metric, descending=descending) if reliable else [],
            "small_sample_n_lt_25": rank_by(small, metric, descending=descending) if small else [],
        }

    rankings = {
        "isolated": {
            "expectancy_r": _rank_tiered(iso_reliable, iso_small, "expectancy_r"),
            "profit_factor": _rank_tiered(iso_reliable, iso_small, "profit_factor"),
            "max_drawdown": _rank_tiered(iso_reliable, iso_small, "max_drawdown", descending=False),
            "net_pnl": _rank_tiered(iso_reliable, iso_small, "net_pnl"),
        },
        "competitive": {
            "expectancy_r": _rank_tiered(comp_reliable, comp_small, "expectancy_r"),
            "profit_factor": _rank_tiered(comp_reliable, comp_small, "profit_factor"),
            "max_drawdown": _rank_tiered(comp_reliable, comp_small, "max_drawdown", descending=False),
            "net_pnl": _rank_tiered(comp_reliable, comp_small, "net_pnl"),
        },
        "robustness_isolated": sorted(
            ((sid, r.overall_score, r.state.value, isolated_metrics[sid]["window_metrics"].n_trades) for sid, r in isolated_health.items()),
            key=lambda x: (x[1] is None, -(x[1] or 0.0)),
        ),
        "robustness_competitive": sorted(
            ((sid, r.overall_score, r.state.value, competitive_metrics[sid]["window_metrics"].n_trades) for sid, r in competitive_health.items()),
            key=lambda x: (x[1] is None, -(x[1] or 0.0)),
        ),
    }

    # ------------------------------------------------------------------ blocking taxonomy + classification
    blocking: dict[str, Any] = {}
    classification: dict[str, dict[str, str]] = {}
    for sid in all_strategy_ids:
        iso_f, comp_f = isolated_funnel_by_strategy[sid], competitive_funnel_by_strategy[sid]
        iso_n = isolated_metrics[sid]["window_metrics"].n_trades
        comp_n = competitive_metrics[sid]["window_metrics"].n_trades
        opportunities_lost = iso_n - comp_n
        retention_pct = (comp_n / iso_n) if iso_n > 0 else None
        shared_slot_denials = comp_f["risk_deny_reasons"].get("LIMIT_MAX_PER_SYMBOL", 0)
        # crowding_pct = share of ALL competitive-scenario denial EVENTS specifically attributable to
        # the shared slot -- a properly [0,1]-bounded fraction (denials are per-BAR events, not per
        # lost-trade, so dividing by opportunities_lost instead -- an earlier draft of this script did
        # exactly that -- produces figures >100% and is not a genuine percentage; fixed in the
        # 2026-07-20 audit).
        total_comp_denials = sum(comp_f["risk_deny_reasons"].values())
        crowding_pct = (shared_slot_denials / total_comp_denials) if total_comp_denials > 0 else None
        blocking[sid] = {
            "isolated_breakdown": _blocking_breakdown(iso_f),
            "competitive_breakdown": _blocking_breakdown(comp_f),
            "isolated_trade_count": iso_n,
            "competitive_trade_count": comp_n,
            "opportunities_lost": opportunities_lost,
            "retention_pct": retention_pct,
            "crowding_pct": crowding_pct,
            "principal_loss_reason": _principal_loss_reason(iso_f, comp_f),
        }
        category, justification = _classify(
            iso_n, isolated_metrics[sid]["window_metrics"].profit_factor,
            isolated_metrics[sid]["window_metrics"].expectancy_r, isolated_health[sid].state.value,
        )
        classification[sid] = {"category": category, "justification": justification}

    return {
        "window": {"start": WINDOW_START, "end": WINDOW_END},
        "all_strategy_ids": all_strategy_ids,
        "isolated_metrics": isolated_metrics,
        "competitive_metrics": competitive_metrics,
        "isolated_funnel": isolated_funnel_by_strategy,
        "competitive_funnel": competitive_funnel_by_strategy,
        "attribution": attribution_by_sid,
        "isolated_health": isolated_health,
        "competitive_health": competitive_health,
        "correlation": corr,
        "diversification": diversification,
        "rankings": rankings,
        "blocking": blocking,
        "classification": classification,
    }


def _jsonify(obj: Any) -> Any:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: _jsonify(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, enum.Enum):
        return obj.value
    if isinstance(obj, dict):
        return {str(k): _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify(v) for v in obj]
    if isinstance(obj, TradeRecord):
        return {f.name: _jsonify(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    return obj


def _num(x: float | None, digits: int = 2) -> str:
    return "n/a" if x is None else f"{x:.{digits}f}"


def _pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x * 100:.1f}%"


def _tiered_ranking_md(tiered: dict[str, list], title: str) -> str:
    lines = [f"#### {title}", "", "**Reliable sample (n >= 25)**", "", "| Rank | Strategy | Value | n_trades |", "|---|---|---|---|"]
    for i, (sid, v) in enumerate(tiered["reliable_n_ge_25"], 1):
        lines.append(f"| {i} | {sid} | {_num(v, 3)} | reliable |")
    if not tiered["reliable_n_ge_25"]:
        lines.append("| -- | (none) | -- | -- |")
    lines += ["", "**Small sample (n < 25) -- NOT comparable to the reliable tier above, shown separately to avoid false precision**", "", "| Rank | Strategy | Value |", "|---|---|---|"]
    for i, (sid, v) in enumerate(tiered["small_sample_n_lt_25"], 1):
        lines.append(f"| {i} | {sid} | {_num(v, 3)} |")
    if not tiered["small_sample_n_lt_25"]:
        lines.append("| -- | (none) | -- |")
    return "\n".join(lines)


def generate_tables(result: dict[str, Any]) -> str:
    sids = result["all_strategy_ids"]
    iso, comp = result["isolated_metrics"], result["competitive_metrics"]
    iso_health, comp_health = result["isolated_health"], result["competitive_health"]
    blocking, classification = result["blocking"], result["classification"]
    corr = result["correlation"]

    avg_corr: dict[str, float | None] = {}
    for sid in sids:
        vals = [v for (a, b), v in corr.items() if (a == sid or b == sid) and a != b and v is not None]
        avg_corr[sid] = (sum(vals) / len(vals)) if vals else None

    def highly_correlated_with(sid: str) -> list[tuple[str, float]]:
        # dict, not set -- a pair (a, b) and (b, a) never both appear as separate correlation_matrix
        # keys for the same unordered pair, but de-duplicating via `set()` on (partner, value) tuples
        # still leaves ties at equal |value| with NO defined order (Python's per-process string hash
        # randomization made this table's own tie order change between runs -- a 2026-07-20 audit
        # finding, fixed here with an explicit, deterministic secondary sort key: partner strategy_id).
        seen: dict[str, float] = {}
        for (a, b), v in corr.items():
            if a == b or v is None:
                continue
            if a == sid and abs(v) > 0.7:
                seen[b] = v
            elif b == sid and abs(v) > 0.7:
                seen[a] = v
        return sorted(seen.items(), key=lambda x: (-abs(x[1]), x[0]))

    out: list[str] = []

    # -------- Table 1: master comparison
    out.append("## Table 1: Scenario A (isolated) vs Scenario B (competitive) master comparison\n")
    out.append("| Strategy | A trades | A PF | A Exp_R | A NetPnL | A DD | A Sharpe | B trades | B PF | B Exp_R | B NetPnL | B DD | B Sharpe |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for sid in sids:
        a, b = iso[sid]["window_metrics"], comp[sid]["window_metrics"]
        out.append(
            f"| {sid} | {a.n_trades} | {_num(a.profit_factor)} | {_num(a.expectancy_r, 3)} | {_num(a.net_pnl)} | {_num(a.max_drawdown)} | {_num(iso[sid]['sharpe_ratio'])} | "
            f"{b.n_trades} | {_num(b.profit_factor)} | {_num(b.expectancy_r, 3)} | {_num(b.net_pnl)} | {_num(b.max_drawdown)} | {_num(comp[sid]['sharpe_ratio'])} |"
        )

    # -------- Table 2: blocking taxonomy (5 categories) + retention/crowding
    out.append("\n## Table 2: Blocking taxonomy (5 categories) and shared-slot cost per strategy\n")
    out.append("| Strategy | A nonexistent | A ineligible | A shared-slot-blocked | A executed | A nonfinalized | B nonexistent | B ineligible | B shared-slot-blocked | B executed | B nonfinalized | Opportunities lost | Retention % | Crowding % | Principal loss reason |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for sid in sids:
        bd = blocking[sid]
        ab, bb = bd["isolated_breakdown"], bd["competitive_breakdown"]
        out.append(
            f"| {sid} | {ab['nonexistent_signals']} | {ab['generated_ineligible']} | {ab['eligible_blocked_by_position']} | {ab['executed']} | {ab['nonfinalized_excluded']} | "
            f"{bb['nonexistent_signals']} | {bb['generated_ineligible']} | {bb['eligible_blocked_by_position']} | {bb['executed']} | {bb['nonfinalized_excluded']} | "
            f"{bd['opportunities_lost']} | {_pct(bd['retention_pct'])} | {_pct(bd['crowding_pct'])} | {bd['principal_loss_reason']} |"
        )

    # -------- Table 3: robustness + payoff/recovery/best-worst-month
    out.append("\n## Table 3: Robustness (Strategy Health), win rate, payoff, recovery, best/worst month\n")
    out.append("| Strategy | A Health | A Score | A WinRate | A Payoff | A Recovery | A Best month | A Worst month | B Health | B Score | B WinRate |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for sid in sids:
        a = iso[sid]
        awm = a["window_metrics"]
        ah, bh = iso_health[sid], comp_health[sid]
        out.append(
            f"| {sid} | {ah.state.value} | {_num(ah.overall_score, 1)} | {_pct(awm.win_rate)} | "
            f"{_num(a['payoff_ratio'])} | {_num(a['recovery_factor'])} | "
            f"{a['best_month']}({_num(a['best_month_pnl'])}) | {a['worst_month']}({_num(a['worst_month_pnl'])}) | "
            f"{bh.state.value} | {_num(bh.overall_score, 1)} | {_pct(comp[sid]['window_metrics'].win_rate)} |"
        )

    # -------- Rankings (tiered)
    rk = result["rankings"]
    out.append("\n## Rankings -- Scenario A (isolated)\n")
    out.append(_tiered_ranking_md(rk["isolated"]["expectancy_r"], "By Expectancy_R"))
    out.append("")
    out.append(_tiered_ranking_md(rk["isolated"]["profit_factor"], "By Profit Factor"))
    out.append("")
    out.append(_tiered_ranking_md(rk["isolated"]["max_drawdown"], "By Max Drawdown (ascending = best)"))
    out.append("")
    out.append(_tiered_ranking_md(rk["isolated"]["net_pnl"], 'By Net PnL ("alpha generated" proxy -- raw profit, NOT beta-adjusted statistical alpha)'))

    out.append("\n## Rankings -- Robustness (Strategy Health overall_score), Scenario A\n")
    out.append("| Rank | Strategy | Score | State | n_trades |")
    out.append("|---|---|---|---|---|")
    for i, (sid, score, state, n) in enumerate(rk["robustness_isolated"], 1):
        out.append(f"| {i} | {sid} | {_num(score, 1)} | {state} | {n} |")

    out.append("\n## Rankings -- Scenario B (competitive)\n")
    out.append(_tiered_ranking_md(rk["competitive"]["expectancy_r"], "By Expectancy_R"))
    out.append("")
    out.append(_tiered_ranking_md(rk["competitive"]["profit_factor"], "By Profit Factor"))

    out.append("\n## Rankings -- Robustness (Strategy Health overall_score), Scenario B\n")
    out.append("| Rank | Strategy | Score | State | n_trades |")
    out.append("|---|---|---|---|---|")
    for i, (sid, score, state, n) in enumerate(rk["robustness_competitive"], 1):
        out.append(f"| {i} | {sid} | {_num(score, 1)} | {state} | {n} |")

    # -------- Diversification
    out.append("\n## Diversification / correlation flags (Scenario B trades, sparse -- see caveats in main report)\n")
    out.append("| Strategy | Avg pairwise corr (B) | Highly correlated with (|corr|>0.7) |")
    out.append("|---|---|---|")
    for sid in sids:
        hc = highly_correlated_with(sid)
        hc_str = ", ".join(f"{s}({v:.2f})" for s, v in hc[:5]) if hc else "none"
        out.append(f"| {sid} | {_num(avg_corr[sid], 3)} | {hc_str} |")
    d = result["diversification"]
    out.append(f"\nPortfolio-wide: n_strategy_pairs={d.n_strategy_pairs}, avg_pairwise_correlation={_num(d.avg_pairwise_correlation, 4)}, n_pairs_highly_correlated={d.n_pairs_highly_correlated}\n")

    # -------- Table 4: final 5-tier classification
    out.append("\n## Table 4: Final classification (A/B/C/D/E) with exact justification\n")
    out.append("| Strategy | Category | Justification |")
    out.append("|---|---|---|")
    for sid in sids:
        c = classification[sid]
        out.append(f"| {sid} | {c['category']} | {c['justification']} |")

    counts: dict[str, int] = defaultdict(int)
    for sid in sids:
        counts[classification[sid]["category"]] += 1
    out.append(f"\nCategory counts: A={counts['A']}, B={counts['B']}, C={counts['C']}, D={counts['D']}, E={counts['E']} (total={sum(counts.values())})\n")

    return "\n".join(out)


if __name__ == "__main__":
    result = main()
    n_iso = sum(m["window_metrics"].n_trades for m in result["isolated_metrics"].values())
    n_comp = sum(m["window_metrics"].n_trades for m in result["competitive_metrics"].values())
    print(f"Loaded {len(result['all_strategy_ids'])} strategies.")
    print(f"Isolated total trades: {n_iso}")
    print(f"Competitive total trades: {n_comp}")

    data_path = REPO_ROOT / "ceo_strategy_performance_study_data.json"
    data_json = json.dumps(_jsonify(result), indent=2, sort_keys=True)
    data_path.write_text(data_json, encoding="utf-8")
    print(f"Full data dumped to {data_path}")

    tables_path = REPO_ROOT / "ceo_strategy_performance_study_tables.md"
    tables_path.write_text(generate_tables(result) + "\n", encoding="utf-8")
    print(f"Tables written to {tables_path}")

    import hashlib
    print(f"data.json sha256: {hashlib.sha256(data_json.encode('utf-8')).hexdigest()}")
