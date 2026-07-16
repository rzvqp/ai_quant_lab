"""Phase 6.9 -- Rolling Health-Gated Backtest orchestrator (SCRATCH script, mirrors Wave D's own
precedent: run once, capture output into a committed report, then delete -- see
`NEXT_SESSION.md` §F: "every one-off analysis script used this session was deleted after its output
was captured into a committed report"). NOT part of the permanent library -- the only permanent,
tested, committed additions are `ai_trader/simulation/harness.py`'s overlay-isolation fix and
`ai_trader/strategy_health/rolling_gate.py`.

Runs THREE full-history passes over the exact Wave D historical range/config
(`WAVE_D_PORTFOLIO_SIMULATION_REPORT.md` §1):
  A. Static baseline  -- all 43 strategies active throughout (`strategy_id_filter=None`), reproduced
     fresh in this session as a config-correctness cross-check against Wave D's own documented
     513-trade / +$313.21 result.
  B. Rolling Health-Gated backtest -- ONE continuous harness (never re-instantiated -- avoids the
     warmup/session-anchor discontinuity that independently re-running per-month harnesses would
     introduce), with `harness._strategy_id_filter` mutated at each monthly checkpoint from
     `ai_trader.strategy_health.rolling_gate.active_strategy_ids_at()`, called on the REAL trade
     ledger accumulated so far. First 12 months (365 days, matching the 12m window's own day-count)
     run UNGATED (bootstrap); monthly (30-day) re-evaluation from month 13 onward. A checkpoint's own
     new roster takes effect starting the NEXT bar (the checkpoint's own bar still executes under the
     OLD roster) -- the same one-bar-lag convention every other mechanism in this Simulation Framework
     already uses (next-open entries, the time-stop's own one-bar-early fire).
  B' A second full run of B, byte-for-byte, to prove determinism (§8.3.4/§8.7).

Writes `phase69_results.json` (repo root) with every metric the CEO's Phase 6.9 directive asked for.
"""

from __future__ import annotations

import json
from dataclasses import asdict, replace
from datetime import UTC, datetime
from pathlib import Path

from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.simulation import performance_analyzer
from ai_trader.simulation.config import DateRange, SimulationContext
from ai_trader.simulation.harness import SimulationHarness
from ai_trader.simulation.portfolio_simulator import TradeRecord
from ai_trader.simulation.types import RunState
from ai_trader.strategy_health.rolling_gate import health_reports_at
from ai_trader.strategy_health.types import ClosedTrade, HealthState
from ai_trader.strategy_manager.config import ManagerConfig
from ai_trader.strategy_runtime.registry import build_runtime_handles

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}

_DAY = 86400
RUN_START = 1_671_187_500   # 2022-12-16 (Wave D's own start)
RUN_END = 1_783_922_400     # 2026-07-13 (Wave D's own end)
BOOTSTRAP_DAYS = 365        # first 12 months ungated (matches the 12m window's own day-count)
CHECKPOINT_INTERVAL_DAYS = 30  # fixed-day-count "month", NOT a calendar month (determinism)
STARTING_BALANCE = 2000.0
RUN_SEED = 1


def _risk_config() -> RiskConfig:
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    cfg.sizing = replace(cfg.sizing, risk_per_trade_pct=0.05)  # SizingLimits is frozen -- replace, not mutate
    return cfg


def _context(run_id: str) -> SimulationContext:
    return SimulationContext(
        run_id=run_id, date_range=DateRange(RUN_START, RUN_END), symbols=("XAUUSD",),
        timeframes=("M15", "H1", "H4", "D1"), starting_balance=STARTING_BALANCE, run_seed=RUN_SEED,
        warmup_bars=200,
    )


def _new_harness(run_id: str, strategy_id_filter: frozenset[str] | None) -> SimulationHarness:
    harness = SimulationHarness(
        _context(run_id), SYMBOL_META, DATA_DIR,
        manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(),
        enable_time_stops=True, enable_trailing_stops=True, strategy_id_filter=strategy_id_filter,
    )
    harness.configure()
    harness.load()
    assert harness.state is RunState.WARMUP, harness.fail_reason
    return harness


def _checkpoint_schedule() -> list[int]:
    checkpoints = []
    t = RUN_START + BOOTSTRAP_DAYS * _DAY
    while t < RUN_END:
        checkpoints.append(t)
        t += CHECKPOINT_INTERVAL_DAYS * _DAY
    return checkpoints


def _to_closed_trade(t: TradeRecord) -> ClosedTrade:
    return ClosedTrade(
        strategy_id=t.strategy_id, exit_as_of=t.exit_as_of, net_pnl=t.net_pnl, pnl_r=t.pnl_r,
        holding_bars=t.holding_bars,
    )


def run_static_baseline() -> SimulationHarness:
    harness = _new_harness("PHASE69-STATIC-BASELINE", strategy_id_filter=None)
    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    return harness


def run_rolling_gated(run_id: str) -> tuple[SimulationHarness, list[dict[str, object]]]:
    harness = _new_harness(run_id, strategy_id_filter=None)  # bootstrap: ungated
    assert harness.portfolio_simulator is not None
    all_ids = frozenset(
        h.id for h in build_runtime_handles(
            harness._strategy_manager, frozenset(harness.context.symbols), only_ids=None,
        )
    )
    checkpoints = _checkpoint_schedule()
    trades_by_strategy: dict[str, list[ClosedTrade]] = {sid: [] for sid in all_ids}
    ledger_cursor = 0  # index into account.trade_ledger already folded into trades_by_strategy

    checkpoint_records: list[dict[str, object]] = []
    next_idx = 0
    while harness.step():
        as_of = harness.as_of
        assert as_of is not None
        while next_idx < len(checkpoints) and as_of >= checkpoints[next_idx]:
            account = harness.portfolio_simulator.account
            for trade in account.trade_ledger[ledger_cursor:]:
                trades_by_strategy.setdefault(trade.strategy_id, []).append(_to_closed_trade(trade))
            ledger_cursor = len(account.trade_ledger)

            checkpoint_as_of = checkpoints[next_idx]
            reports = health_reports_at(trades_by_strategy, checkpoint_as_of)
            active_ids = frozenset(sid for sid, r in reports.items() if r.state is HealthState.ACTIVE)
            harness._strategy_id_filter = active_ids  # takes effect starting the NEXT bar

            checkpoint_records.append({
                "as_of": checkpoint_as_of,
                "date": datetime.fromtimestamp(checkpoint_as_of, tz=UTC).strftime("%Y-%m-%d"),
                "active_ids": sorted(active_ids),
                "states": {sid: r.state.value for sid, r in reports.items()},
                "trend_deltas": {sid: r.trend_delta for sid, r in reports.items()},
                "confidences_12m": {
                    sid: r.window_scores["12m"].confidence for sid, r in reports.items()
                },
                "overall_scores": {sid: r.overall_score for sid, r in reports.items()},
            })
            next_idx += 1

    assert harness.state is RunState.COMPLETED, harness.fail_reason
    return harness, checkpoint_records


def _performance_dict(harness: SimulationHarness) -> dict[str, object]:
    assert harness.portfolio_simulator is not None
    report = performance_analyzer.analyze(harness.context, harness.portfolio_simulator.account)
    return {
        "portfolio_summary": asdict(report.portfolio_summary),
        "performance": asdict(report.performance),
        "attribution": [asdict(a) for a in report.attribution],
        "monthly": [asdict(p) for p in report.stats.monthly],
        "risk_events": [asdict(e) for e in report.risk_events],
    }


def _daily_equity_curve(harness: SimulationHarness) -> list[dict[str, object]]:
    """One point per UTC calendar day (last mark-to-market of that day) -- a reduced, report-sized
    equity curve rather than all 84,151 raw bars."""
    assert harness.portfolio_simulator is not None
    by_day: dict[str, object] = {}
    for p in harness.portfolio_simulator.account.equity_curve:
        if not p.phase_running:
            continue
        day = datetime.fromtimestamp(p.as_of, tz=UTC).strftime("%Y-%m-%d")
        by_day[day] = {"date": day, "equity": p.equity, "balance": p.balance, "drawdown_pct": p.drawdown_pct}
    return [by_day[d] for d in sorted(by_day)]


def main() -> None:
    print("=== A. Static baseline (all 43, strategy_id_filter=None) ===", flush=True)
    static_harness = run_static_baseline()
    static_perf = _performance_dict(static_harness)
    print(json.dumps(static_perf["performance"], indent=2), flush=True)

    print("=== B. Rolling Health-Gated backtest (run 1) ===", flush=True)
    rolling_harness_1, checkpoints_1 = run_rolling_gated("PHASE69-ROLLING-1")
    rolling_perf_1 = _performance_dict(rolling_harness_1)
    print(json.dumps(rolling_perf_1["performance"], indent=2), flush=True)

    print("=== B'. Rolling Health-Gated backtest (run 2, determinism check) ===", flush=True)
    rolling_harness_2, checkpoints_2 = run_rolling_gated("PHASE69-ROLLING-2")
    rolling_perf_2 = _performance_dict(rolling_harness_2)

    assert rolling_perf_1 == rolling_perf_2, "DETERMINISM FAILURE: two identical rolling-gated runs diverged"
    assert checkpoints_1 == checkpoints_2, "DETERMINISM FAILURE: checkpoint roster history diverged"
    print("Determinism check PASSED: run 1 == run 2 (performance + full checkpoint history)", flush=True)

    results = {
        "config": {
            "date_range": [RUN_START, RUN_END], "starting_balance": STARTING_BALANCE, "run_seed": RUN_SEED,
            "bootstrap_days": BOOTSTRAP_DAYS, "checkpoint_interval_days": CHECKPOINT_INTERVAL_DAYS,
            "risk_per_trade_pct": 0.05,
        },
        "static_baseline": static_perf,
        "static_baseline_daily_equity": _daily_equity_curve(static_harness),
        "rolling_gated": rolling_perf_1,
        "rolling_gated_daily_equity": _daily_equity_curve(rolling_harness_1),
        "checkpoints": checkpoints_1,
        "determinism_verified": True,
    }
    out_path = REPO_ROOT / "phase69_results.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
