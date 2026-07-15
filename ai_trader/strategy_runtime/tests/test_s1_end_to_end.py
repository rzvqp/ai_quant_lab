"""Checkpoint 1 proof: S1's real runtime evaluator, driven through the REAL composed six-module
pipeline (Market Scanner -> Strategy Manager -> Signal Engine -> Scoring Engine -> Risk Manager ->
Execution Engine) plus the Simulation Framework (Execution Simulator, Portfolio Simulator,
Performance Analyzer), over real historical XAUUSD data, produces real, economically sensible closed
trades -- not a fixture, not a mock, the genuine end-to-end chain."""

from __future__ import annotations

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


def _risk_config() -> RiskConfig:
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    return cfg


def test_s1_produces_a_real_trade_through_the_full_pipeline() -> None:
    context = SimulationContext(
        run_id="CHECKPOINT1-1", date_range=DateRange(1_672_617_600, 1_700_000_000), symbols=("XAUUSD",),
        timeframes=("M15", "H1", "H4", "D1"), starting_balance=2000.0, run_seed=1, warmup_bars=200,
    )
    harness = SimulationHarness(
        context, SYMBOL_META, DATA_DIR,
        manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(),
    )
    harness.configure()
    harness.load()
    assert harness.state is RunState.WARMUP, harness.fail_reason

    # S1 must actually be active (loaded, admitted, and the REAL evaluator wired in) before the run.
    # Phase 6.8 Wave B Checkpoint 2 migrated 14 more strategies alongside S1 -- this test's own
    # purpose (proving S1 specifically reaches a real runtime handle) only needs "S1 is present",
    # not "S1 is the only one active" (which stopped being true the moment Checkpoint 2 landed).
    from ai_trader.strategy_runtime.registry import build_runtime_handles
    handles = build_runtime_handles(harness._strategy_manager, frozenset({"XAUUSD"}))
    assert "S1" in [h.id for h in handles]

    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    assert harness.orders_submitted > 0, "S1 must submit at least one real order over this window"
    assert harness.fills_total > 0

    account = harness.portfolio_simulator.account
    assert len(account.trade_ledger) > 0, "at least one real trade must close over this window"

    # Phase 6.8 Wave B Checkpoint 2 registered 14 more strategies sharing this same runtime registry
    # (`build_runtime_handles` returns every active strategy, not S1 alone) -- since only one
    # position at a time is open per symbol system-wide, other strategies can legitimately win some
    # of the shared slot's trades now. This test's own remaining scope is "S1 itself still produces
    # at least one real, sane trade" (Checkpoint 2's own `test_checkpoint2_end_to_end.py` covers the
    # full 15-strategy proof, including the relaxed R-multiple bound for time-exit strategies).
    for trade in account.trade_ledger:
        assert trade.symbol == "XAUUSD"
        # every trade must be internally consistent: qty/prices positive and finite.
        assert trade.qty > 0
        assert trade.entry_price > 0 and trade.exit_price > 0
        # a real stop is always registered, so downside is bounded near -1R regardless of strategy;
        # only rr2/rr3-exit strategies cap the upside near +2R/+3R -- time-exit strategies do not.
        assert trade.pnl_r is not None
        assert trade.pnl_r >= -1.5

    s1_trades = [t for t in account.trade_ledger if t.strategy_id == "S1"]
    assert len(s1_trades) > 0, "S1 must close at least one real trade over this window"
    for trade in s1_trades:
        # S1's own rr2 exit still caps its upside near +2R (a little tolerance for slippage/spread).
        assert trade.pnl_r is not None and trade.pnl_r <= 2.5

    # The report must be internally consistent and schema-valid end to end.
    report = performance_analyzer.analyze(context, account)
    schema_dict = performance_analyzer.to_schema_dict(
        context, report, "COMPLETED", harness.composed_module_versions(), generated_at=0,
    )
    from ai_trader.simulation.schema_validation import validate_simulation_run_dict
    errors = validate_simulation_run_dict(schema_dict)
    assert errors == [], errors
    assert report.performance.trades == len(account.trade_ledger)
    s1_attribution = next(a for a in report.attribution if a.strategy_id == "S1")
    assert s1_attribution.trades == len(s1_trades)


def test_deterministic_replay_is_still_bit_identical_with_real_strategies_active() -> None:
    """The determinism law (SIMULATION_ARCHITECTURE.md §5) must hold even with real evaluator logic
    in the loop, not just the Phase 6.7 fail-safe-stub path."""
    from dataclasses import asdict

    def run(run_id: str) -> object:
        context = SimulationContext(
            run_id=run_id, date_range=DateRange(1_672_617_600, 1_685_000_000), symbols=("XAUUSD",),
            timeframes=("M15", "H1", "H4", "D1"), starting_balance=2000.0, run_seed=7, warmup_bars=200,
        )
        harness = SimulationHarness(
            context, SYMBOL_META, DATA_DIR,
            manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
            use_strategy_runtime=True, risk_config=_risk_config(),
        )
        harness.configure()
        harness.load()
        harness.run_to_completion()
        assert harness.state is RunState.COMPLETED, harness.fail_reason
        return performance_analyzer.analyze(context, harness.portfolio_simulator.account)

    report_a = run("DET-S1-A")
    report_b = run("DET-S1-B")
    assert asdict(report_a) == asdict(report_b)  # type: ignore[call-overload]
