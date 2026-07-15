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
    # Phase 6.8 Wave B has since registered 32 more strategies sharing the same runtime registry,
    # and only one position at a time is open per symbol system-wide -- so a run with every
    # strategy active can legitimately starve S1 of the shared slot entirely (observed: 0 S1 trades
    # over this exact window once ~30 competitors were active). This test's own purpose is "S1's
    # OWN evaluator, proven end to end" (Checkpoint 1's original scope), so it isolates S1 via
    # ``strategy_id_filter`` -- a generic harness capability, not a special case for S1. The
    # multi-strategy competitive scenario is separately covered by
    # ``test_checkpoint2_end_to_end.py``.
    context = SimulationContext(
        run_id="CHECKPOINT1-1", date_range=DateRange(1_672_617_600, 1_700_000_000), symbols=("XAUUSD",),
        timeframes=("M15", "H1", "H4", "D1"), starting_balance=2000.0, run_seed=1, warmup_bars=200,
    )
    harness = SimulationHarness(
        context, SYMBOL_META, DATA_DIR,
        manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(),
        strategy_id_filter=frozenset({"S1"}),
    )
    harness.configure()
    harness.load()
    assert harness.state is RunState.WARMUP, harness.fail_reason

    # S1 must actually be active (loaded, admitted, and the REAL evaluator wired in) before the run.
    from ai_trader.strategy_runtime.registry import build_runtime_handles
    handles = build_runtime_handles(harness._strategy_manager, frozenset({"XAUUSD"}), only_ids=frozenset({"S1"}))
    assert [h.id for h in handles] == ["S1"]

    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    assert harness.orders_submitted > 0, "S1 must submit at least one real order over this window"
    assert harness.fills_total > 0

    account = harness.portfolio_simulator.account
    assert len(account.trade_ledger) > 0, "S1 must close at least one real trade over this window"

    for trade in account.trade_ledger:
        assert trade.strategy_id == "S1"
        assert trade.symbol == "XAUUSD"
        # every trade must be internally consistent: qty/prices positive and finite.
        assert trade.qty > 0
        assert trade.entry_price > 0 and trade.exit_price > 0
        # R-multiple must be computed (S1 always registers a stop hint) and in a sane range for a
        # rr2-exit strategy (a loss caps near -1R, a win at the target caps near +2R; a little
        # tolerance either side for slippage/spread).
        assert trade.pnl_r is not None
        assert -1.5 <= trade.pnl_r <= 2.5

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
    assert s1_attribution.trades == len(account.trade_ledger)


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
