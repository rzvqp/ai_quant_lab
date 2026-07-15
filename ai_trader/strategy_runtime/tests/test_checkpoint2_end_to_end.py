"""Phase 6.8 Wave B Checkpoint 2 proof: B1 (session/calendar) + B2 (liquidity/sweep) -- 14 real
evaluators alongside S1's own Checkpoint 1 reference slice -- driven through the REAL composed
six-module pipeline + Simulation Framework over real historical XAUUSD data, mirroring
``test_s1_end_to_end.py``'s own pattern, extended per-batch exactly as ``PHASE_6_8_WAVE_B_PLAN.md``
§5 requires (not deferred to the very end)."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.simulation import performance_analyzer
from ai_trader.simulation.config import DateRange, SimulationContext
from ai_trader.simulation.harness import SimulationHarness
from ai_trader.simulation.types import RunState
from ai_trader.strategy_manager.config import ManagerConfig

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}

CHECKPOINT_2_IDS = frozenset({
    "S1", "S6", "S16", "S17", "S18", "S19", "S24", "S29", "S30", "S31",
    "S2", "S11", "S12", "S21", "S22",
})
TIME_EXIT_IDS = frozenset({"S16", "S17", "S18", "S19", "S24"})


def _risk_config() -> RiskConfig:
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    return cfg


def _run(run_id: str) -> SimulationHarness:
    context = SimulationContext(
        run_id=run_id, date_range=DateRange(1_672_617_600, 1_700_000_000), symbols=("XAUUSD",),
        timeframes=("M15", "H1", "H4", "D1"), starting_balance=2000.0, run_seed=1, warmup_bars=200,
    )
    harness = SimulationHarness(
        context, SYMBOL_META, DATA_DIR,
        manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(), enable_time_stops=True,
    )
    harness.configure()
    harness.load()
    assert harness.state is RunState.WARMUP, harness.fail_reason
    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    return harness


def test_all_checkpoint_2_strategies_are_active_before_the_run() -> None:
    from ai_trader.strategy_runtime.registry import build_runtime_handles

    context = SimulationContext(
        run_id="CHECKPOINT2-HANDLES", date_range=DateRange(1_672_617_600, 1_680_000_000),
        symbols=("XAUUSD",), timeframes=("M15", "H1", "H4", "D1"), starting_balance=2000.0,
        run_seed=1, warmup_bars=200,
    )
    harness = SimulationHarness(
        context, SYMBOL_META, DATA_DIR, manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(),
    )
    harness.configure()
    harness.load()
    handles = build_runtime_handles(harness._strategy_manager, frozenset({"XAUUSD"}))
    assert {h.id for h in handles} == CHECKPOINT_2_IDS


def test_checkpoint_2_produces_real_trades_through_the_full_pipeline() -> None:
    harness = _run("CHECKPOINT2-1")
    assert harness.orders_submitted > 0
    account = harness.portfolio_simulator.account  # type: ignore[union-attr]
    assert len(account.trade_ledger) > 0, "at least one Checkpoint 2 strategy must close a real trade"

    for trade in account.trade_ledger:
        assert trade.strategy_id in CHECKPOINT_2_IDS
        assert trade.symbol == "XAUUSD"
        assert trade.qty > 0
        assert trade.entry_price > 0 and trade.exit_price > 0
        # every trade carries a real stop, so downside is bounded near -1R regardless of exit kind;
        # time-exit strategies have no target, so upside is NOT capped near +2R/+3R the way S1 is.
        assert trade.pnl_r is None or trade.pnl_r >= -1.5
        if trade.strategy_id in TIME_EXIT_IDS:
            # a time-exit strategy's own trade can NEVER outlive its declared time-stop horizon.
            assert trade.holding_bars <= 24

    report = performance_analyzer.analyze(harness.context, account)
    schema_dict = performance_analyzer.to_schema_dict(
        harness.context, report, "COMPLETED", harness.composed_module_versions(), generated_at=0,
    )
    from ai_trader.simulation.schema_validation import validate_simulation_run_dict
    errors = validate_simulation_run_dict(schema_dict)
    assert errors == [], errors
    assert report.performance.trades == len(account.trade_ledger)


def test_deterministic_replay_holds_with_all_checkpoint_2_strategies_and_time_stops_active() -> None:
    def run_report(run_id: str) -> object:
        harness = _run(run_id)
        return performance_analyzer.analyze(harness.context, harness.portfolio_simulator.account)  # type: ignore[union-attr]

    report_a = run_report("CHECKPOINT2-DET-A")
    report_b = run_report("CHECKPOINT2-DET-B")
    assert asdict(report_a) == asdict(report_b)  # type: ignore[call-overload]
