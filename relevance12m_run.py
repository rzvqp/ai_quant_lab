"""Current XAUUSD 12-Month Relevance Audit -- run script (SCRATCH, same precedent as the phase69_*.py
scripts: run once, capture output into the committed report, preserved as a diagnostic artifact per
CEO instruction). Runs FOUR standalone, identically-configured 12-month backtests (A/B/C/D), each a
FRESH `SimulationHarness` scoped to ONLY the analysis window (never the full 3.6-year Wave D range) --
this matches how every other single-window real end-to-end test in this repo already works
(warmup_bars=200 cold-start), so all 4 variants are directly, fairly comparable (no variant benefits
from years of extra market-scanner state the others lack).

WINDOW SELECTION (decided BEFORE running anything, disclosed in full in the report):
the CEO asked for "the most recent completed 12 months" but also explicitly forbade using the sealed
terminal holdout (the last 20% of the M15 series, docs/S21_S40_IMPLEMENTATION_REPORTS.md:6 and
PROJECT_STATE_v1.0.md:34 -- "last 20% M15 (16,831 bars): SEALED -- never opened"). The literal most
recent 12 months of ALL data (ending 2026-07-13) falls almost entirely inside that sealed holdout, so
this script instead uses the most recent COMPLETE 12 months that lie entirely within the non-sealed
(research + validation) 80% of the dataset: the last non-sealed bar (2025-10-23 09:00 UTC, bar index
67320 of 84152) back 365 days to 2024-10-23 09:00 UTC.
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

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}

# ---- window (see module docstring) ----
WINDOW_START = 1_729_674_000   # 2024-10-23 09:00:00 UTC
WINDOW_END = 1_761_210_000     # 2025-10-23 09:00:00 UTC (last non-sealed bar; sealed holdout begins 2025-10-23 09:15 UTC)
STARTING_BALANCE = 2000.0
RUN_SEED = 1


def _risk_config() -> RiskConfig:
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    cfg.sizing = replace(cfg.sizing, risk_per_trade_pct=0.05)
    return cfg


def _new_harness(run_id: str, strategy_id_filter: frozenset[str] | None) -> SimulationHarness:
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


def run_variant(run_id: str, strategy_id_filter: frozenset[str] | None) -> SimulationHarness:
    harness = _new_harness(run_id, strategy_id_filter)
    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    return harness


def _trade_to_dict(t: TradeRecord) -> dict[str, object]:
    d = asdict(t)
    d["direction"] = t.direction.value
    return d


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


def main() -> None:
    print("=== Discovering all 43 runtime-eligible strategy ids ===", flush=True)
    probe = _new_harness("RELEVANCE12M-PROBE", strategy_id_filter=None)
    all_ids = sorted(
        h.id for h in build_runtime_handles(probe._strategy_manager, frozenset(probe.context.symbols), only_ids=None)
    )
    print(f"{len(all_ids)} strategies: {all_ids}", flush=True)

    print("=== A. All 43 strategies ===", flush=True)
    harness_a = run_variant("RELEVANCE12M-A-ALL43", strategy_id_filter=None)
    assert harness_a.portfolio_simulator is not None
    perf_a = _performance_dict(harness_a)
    trades_a = [_trade_to_dict(t) for t in harness_a.portfolio_simulator.account.trade_ledger]
    print(json.dumps(perf_a["performance"], indent=2), flush=True)
    print(f"trades in A: {len(trades_a)}", flush=True)

    results = {
        "config": {
            "window_start": WINDOW_START, "window_end": WINDOW_END,
            "starting_balance": STARTING_BALANCE, "run_seed": RUN_SEED, "risk_per_trade_pct": 0.05,
        },
        "all_strategy_ids": all_ids,
        "variant_A_all43": {"performance": perf_a, "trades": trades_a},
    }
    out_path = REPO_ROOT / "relevance12m_portfolioA.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
