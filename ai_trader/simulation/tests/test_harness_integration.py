"""Real six-module pipeline integration test: Market Scanner, Strategy Manager, Signal Engine, Scoring
Engine, Risk Manager, Execution Engine -- all REAL, composed unchanged, driven over real historical
XAUUSD bars from ``data/market/``, exercising the Execution Simulator + Portfolio Simulator +
Performance Analyzer end-to-end (mirrors ``NEXT_SESSION.md`` §D's own "real Scanner->...->Risk Manager
chain" precedent, extended through the full Simulation Harness).
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.simulation.config import DateRange, SimulationContext
from ai_trader.simulation.harness import SimulationHarness
from ai_trader.simulation.types import RunState

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}


def _small_context(**overrides: object) -> SimulationContext:
    defaults: dict[str, object] = dict(
        run_id="INTEGRATION-1", date_range=DateRange(1_700_000_000, 1_700_030_000),
        symbols=("XAUUSD",), timeframes=("M15", "H1", "H4", "D1"), starting_balance=100_000.0,
        run_seed=1, warmup_bars=50,
    )
    defaults.update(overrides)
    return SimulationContext(**defaults)  # type: ignore[arg-type]


def test_real_pipeline_runs_to_completion_fail_safe() -> None:
    """The real Strategy Library's strategies have no executable signal logic yet (Signal Engine's
    documented, disclosed gap -- ``NEXT_SESSION.md`` §C3/§G item 1, carried forward unchanged): every
    real strategy signal is INVALID by design, so this proves the framework runs the REAL composed
    pipeline over real historical data end-to-end, fail-safe, never crashing -- not that it trades
    profitably (that requires the separate, not-yet-scoped strategy-logic-implementation task)."""
    context = _small_context()
    harness = SimulationHarness(context, SYMBOL_META, DATA_DIR)
    harness.configure()
    assert harness.state is RunState.CONFIGURED
    harness.load()
    assert harness.state is RunState.WARMUP, harness.fail_reason
    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    assert harness.bars_processed > 0
    assert harness.portfolio_simulator is not None
    # Fail-safe proof: equity is never corrupted (no crash, no NaN/negative-balance artifact) even
    # though every real strategy path resolves to SKIP/DENY/no-op.
    assert harness.portfolio_simulator.account.equity == context.starting_balance


def test_load_fails_fast_on_bad_date_range() -> None:
    context = _small_context(date_range=DateRange(1_000_000_000, 1_000_000_100))  # far outside the CSV data
    harness = SimulationHarness(context, SYMBOL_META, DATA_DIR)
    harness.configure()
    harness.load()
    assert harness.state is RunState.FAILED
    assert harness.fail_reason is not None


def test_report_is_schema_valid() -> None:
    from ai_trader.simulation import performance_analyzer
    from ai_trader.simulation.schema_validation import validate_simulation_run_dict

    context = _small_context(run_id="INTEGRATION-SCHEMA")
    harness = SimulationHarness(context, SYMBOL_META, DATA_DIR)
    harness.configure()
    harness.load()
    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    assert harness.portfolio_simulator is not None
    report = performance_analyzer.analyze(context, harness.portfolio_simulator.account)
    schema_dict = performance_analyzer.to_schema_dict(
        context, report, "COMPLETED", harness.composed_module_versions(), generated_at=0,
    )
    errors = validate_simulation_run_dict(schema_dict)
    assert errors == [], errors
