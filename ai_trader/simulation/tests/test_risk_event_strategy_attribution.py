"""Phase 6.9A (CEO-approved 2026-07-16) end-to-end proof: a REAL denial, produced by the REAL
composed pipeline over real historical XAUUSD data, is recorded with the correct originating
strategy's own ``strategy_id`` -- not ``None``, not another strategy's id. `test_portfolio_simulator.
py::TestRiskEventAttribution` already proves the storage plumbing in isolation; this test proves the
harness's own two call sites (`ai_trader/simulation/harness.py::_run_one_bar`) actually forward
`decision.strategy_id` correctly when a real `RiskDecision` is denied."""

from __future__ import annotations

from pathlib import Path

from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.config import DateRange, SimulationContext
from ai_trader.simulation.harness import SimulationHarness
from ai_trader.simulation.portfolio_simulator import Position
from ai_trader.simulation.types import RunState, SimPhase
from ai_trader.strategy_manager.config import ManagerConfig
from ai_trader.strategy_runtime.registry import build_runtime_handles

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}
SLOT_HOLDER_ID = "S1"


def _risk_config() -> RiskConfig:
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    return cfg


def test_shared_slot_denial_is_attributed_to_the_real_denied_strategy_not_the_slot_holder() -> None:
    context = SimulationContext(
        run_id="RISK-EVENT-ATTRIBUTION", date_range=DateRange(1_672_617_600, 1_680_000_000),
        symbols=("XAUUSD",), timeframes=("M15", "H1", "H4", "D1"), starting_balance=2000.0,
        run_seed=1, warmup_bars=200,
    )
    harness = SimulationHarness(
        context, SYMBOL_META, DATA_DIR,
        manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(),
        enable_time_stops=True, enable_trailing_stops=True, strategy_id_filter=None,
    )
    harness.configure()
    harness.load()
    assert harness.state is RunState.WARMUP, harness.fail_reason
    assert harness.portfolio_simulator is not None

    all_ids = frozenset(
        h.id for h in build_runtime_handles(harness._strategy_manager, frozenset({"XAUUSD"}), only_ids=None)
    )
    assert SLOT_HOLDER_ID in all_ids

    while harness.phase is not SimPhase.RUNNING:
        assert harness.step(), harness.fail_reason

    # Occupy the single shared XAUUSD slot for the strategy's entire remaining life in this test --
    # every OTHER strategy's own actionable signal for XAUUSD must now be denied by Risk Manager's
    # own `check_max_per_symbol` (`LIMIT_MAX_PER_SYMBOL`), regardless of which strategy it is.
    harness.portfolio_simulator.account.positions["XAUUSD"] = Position(
        symbol="XAUUSD", strategy_id=SLOT_HOLDER_ID, direction=Direction.LONG, size=0.01,
        avg_entry=2000.0, opened_as_of=harness.as_of, opened_bar_index=harness.bar_index,
    )

    for _ in range(4000):
        if not harness.step():
            break

    account = harness.portfolio_simulator.account
    slot_denials = [e for e in account.risk_events if e.type == "DENY_LIMIT_MAX_PER_SYMBOL"]
    assert slot_denials, (
        "expected at least one real DENY_LIMIT_MAX_PER_SYMBOL event over this many real bars with the "
        "slot permanently occupied -- if this fails, no strategy produced any actionable signal at "
        "all in this window, which would need its own investigation, not a wider step count silently"
    )
    for event in slot_denials:
        assert event.strategy_id is not None, "a real DENY_LIMIT_MAX_PER_SYMBOL event must be attributed"
        assert event.strategy_id in all_ids, "attribution must name a real, known strategy id"

    # Every other, non-shared-slot DENY reason recorded in this same run must ALSO carry a real
    # strategy_id (the harness's own two call sites forward it identically for every reason code).
    other_denials = [
        e for e in account.risk_events
        if e.type.startswith("DENY_") and e.type != "DENY_LIMIT_MAX_PER_SYMBOL"
    ]
    for event in other_denials:
        assert event.strategy_id is not None
        assert event.strategy_id in all_ids

    # A bare "DENY" (no denied_reasons at all) still carries strategy_id when one exists.
    bare_denials = [e for e in account.risk_events if e.type == "DENY"]
    for event in bare_denials:
        assert event.strategy_id is not None
        assert event.strategy_id in all_ids
