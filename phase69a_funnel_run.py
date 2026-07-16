"""Phase 6.9A -- Strategy Evidence Flow Audit: the competitive (all-43) instrumented funnel run,
PLUS the parity check proving the instrumentation technique changes zero behavior. SCRATCH script,
preserved diagnostic artifact (same precedent as phase69_*.py / relevance12m_*.py).

Uses the EXACT SAME approved, non-holdout analysis window as the Current XAUUSD 12-Month Relevance
Audit (2024-10-23 -> 2025-10-23) for direct comparability -- same $2,000 capital, 5% risk, cost model,
seed=1, execution model, market data.
"""

from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.simulation import performance_analyzer
from ai_trader.simulation.config import DateRange, SimulationContext
from ai_trader.simulation.harness import SimulationHarness
from ai_trader.simulation.portfolio_simulator import TradeRecord
from ai_trader.simulation.types import RunState
from ai_trader.strategy_manager.config import ManagerConfig
from ai_trader.strategy_runtime.registry import build_runtime_handles
from phase69a_funnel_recorder import FunnelRecorder, instrument, order_level_counts

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}

WINDOW_START = 1_729_674_000   # 2024-10-23 09:00:00 UTC -- identical to the relevance audit's own window
WINDOW_END = 1_761_210_000     # 2025-10-23 09:00:00 UTC
STARTING_BALANCE = 2000.0
RUN_SEED = 1


def _risk_config() -> RiskConfig:
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    cfg.sizing = replace(cfg.sizing, risk_per_trade_pct=0.05)
    return cfg


def new_harness(run_id: str, strategy_id_filter: frozenset[str] | None) -> SimulationHarness:
    context = SimulationContext(
        run_id=run_id, date_range=DateRange(WINDOW_START, WINDOW_END), symbols=("XAUUSD",),
        timeframes=("M15", "H1", "H4", "D1"), starting_balance=STARTING_BALANCE, run_seed=RUN_SEED,
        warmup_bars=200,
    )
    harness = SimulationHarness(
        context, SYMBOL_META, DATA_DIR,
        manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(),
        enable_time_stops=True, enable_trailing_stops=True, strategy_id_filter=strategy_id_filter,
    )
    harness.configure()
    harness.load()
    assert harness.state is RunState.WARMUP, harness.fail_reason
    return harness


def _performance_dict(harness: SimulationHarness) -> dict[str, object]:
    assert harness.portfolio_simulator is not None
    report = performance_analyzer.analyze(harness.context, harness.portfolio_simulator.account)
    return {"portfolio_summary": asdict(report.portfolio_summary), "performance": asdict(report.performance)}


def _full_report_dict(harness: SimulationHarness) -> dict[str, object]:
    """Every field of `SimulationReportData`, not just the two the JSON artifact happens to need --
    used ONLY by `verify_zero_behavior_change()` so its own "byte-identical results" claim is
    actually checked against the full report (attribution/stats/risk_events/allocation included),
    per an adversarial review finding that the narrower `_performance_dict()` alone overstated it."""
    assert harness.portfolio_simulator is not None
    report = performance_analyzer.analyze(harness.context, harness.portfolio_simulator.account)
    return {
        "portfolio_summary": asdict(report.portfolio_summary),
        "performance": asdict(report.performance),
        "attribution": [asdict(a) for a in report.attribution],
        "stats": asdict(report.stats),
        "allocation": asdict(report.allocation) if report.allocation is not None else None,
        "risk_events": [asdict(e) for e in report.risk_events],
    }


def _trade_to_dict(t: TradeRecord) -> dict[str, object]:
    d = asdict(t)
    d["direction"] = t.direction.value
    return d


def run_competitive_instrumented() -> tuple[SimulationHarness, FunnelRecorder]:
    harness = new_harness("PHASE69A-COMPETITIVE-INSTRUMENTED", strategy_id_filter=None)
    recorder = FunnelRecorder()
    instrument(harness, recorder)
    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    return harness, recorder


def run_competitive_plain() -> SimulationHarness:
    harness = new_harness("PHASE69A-COMPETITIVE-PLAIN", strategy_id_filter=None)
    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    return harness


def verify_zero_behavior_change() -> None:
    """The technique's own proof: an INSTRUMENTED run and a PLAIN run, identical config, must
    produce byte-identical trade ledgers and performance reports."""
    instrumented_harness, _ = run_competitive_instrumented()
    plain_harness = run_competitive_plain()
    assert instrumented_harness.portfolio_simulator is not None
    assert plain_harness.portfolio_simulator is not None

    perf_instrumented = _full_report_dict(instrumented_harness)
    perf_plain = _full_report_dict(plain_harness)
    assert perf_instrumented == perf_plain, "INSTRUMENTATION CHANGED BEHAVIOR -- full report diverged"

    trades_instrumented = [_trade_to_dict(t) for t in instrumented_harness.portfolio_simulator.account.trade_ledger]
    trades_plain = [_trade_to_dict(t) for t in plain_harness.portfolio_simulator.account.trade_ledger]
    assert trades_instrumented == trades_plain, "INSTRUMENTATION CHANGED BEHAVIOR -- trade ledger diverged"
    print(f"PARITY VERIFIED: instrumented run and plain run produced byte-identical results "
          f"({len(trades_plain)} trades).")


def main() -> None:
    print("=== Verifying instrumentation causes zero behavior change ===", flush=True)
    verify_zero_behavior_change()

    print("=== Running the competitive (all-43) instrumented funnel measurement ===", flush=True)
    harness, recorder = run_competitive_instrumented()
    assert harness.portfolio_simulator is not None

    all_ids = sorted(
        h.id for h in build_runtime_handles(harness._strategy_manager, frozenset(harness.context.symbols), only_ids=None)
    )
    order_counts = order_level_counts(harness)
    trades = [_trade_to_dict(t) for t in harness.portfolio_simulator.account.trade_ledger]
    perf = _performance_dict(harness)

    results = {
        "config": {"window_start": WINDOW_START, "window_end": WINDOW_END, "starting_balance": STARTING_BALANCE, "run_seed": RUN_SEED},
        "all_strategy_ids": all_ids,
        "performance": perf,
        "trades": trades,
        "signal_counts": {sid: {m: dict(b) for m, b in months.items()} for sid, months in recorder.signal_counts.items()},
        "scoring_counts": {sid: {m: dict(b) for m, b in months.items()} for sid, months in recorder.scoring_counts.items()},
        "risk_counts": {sid: {m: dict(b) for m, b in months.items()} for sid, months in recorder.risk_counts.items()},
        "risk_deny_reasons": {sid: dict(r) for sid, r in recorder.risk_deny_reasons.items()},
        "shared_slot_denials_by_month": {sid: dict(m) for sid, m in recorder.shared_slot_denials.items()},
        "order_counts": {sid: dict(c) for sid, c in order_counts.items()},
    }
    out_path = REPO_ROOT / "phase69a_competitive_funnel.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}", flush=True)
    print(f"Total trades: {len(trades)}", flush=True)


if __name__ == "__main__":
    main()
